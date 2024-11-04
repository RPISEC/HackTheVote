#!/usr/bin/env python3

import hashlib
import itertools
from pathlib import Path
import string
from pwn import remote, context

context.log_level = 'debug'

HOST = "small-snake.chal.hackthe.vote"
PORT = 1337

r = remote(HOST, PORT)

r.recvuntil(b'sha256(')
prefix = r.recvuntil(b' + ', drop=True)
print(prefix)
r.recvuntil(b'*')
num_zeros = int(r.recvuntil(b')', drop=True))

print("solving pow...")
pow_answer = None
for i in itertools.permutations(string.ascii_lowercase, r=6):
    i = ''.join(i)

    if hashlib.sha256(prefix + i.encode()).hexdigest().endswith('0'*num_zeros):
        print(hashlib.sha256(prefix + i.encode()).hexdigest())
        pow_answer = i.encode()
        break

if pow_answer is None:
    print("Couldn't solve pow :(")
    exit(1)

r.sendlineafter(b'>', pow_answer)

with open(Path(__file__).parent / 'sol', 'rb') as f:
    solution = f.read()

r.sendlineafter(b'>', solution)

r.interactive()
