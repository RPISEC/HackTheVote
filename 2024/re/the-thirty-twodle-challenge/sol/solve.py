from pwn import *

HOST = "the-thirty-twodle-challenge.chal.hackthe.vote"
PORT = 1337


r = remote(HOST, PORT)
words = [
    b"waqfs",
    b"brick",
    b"glent",
    b"jumpy",
    b"vozhd",
]

r.sendlineafter(b'seed:', b'15f')

for word in words:
    r.sendlineafter(b'Guess ', word)

r.recvuntil(b'You solved the challenge!')
r.sendline(b'cat flag')
r.interactive()
