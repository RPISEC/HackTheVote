#!/usr/bin/python3
import socket

from server import PLAINTEXTS

HOST = "regdb.hackthe.vote"
PORT = 50007


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    data = s.recv(1024)
    s.sendall(b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPZDDZ\n")
    s.sendall(b"69V2NVjCkhWv#r\x0b1\n")
    e1 = bytes.fromhex(s.recv(1024).strip().decode())
    e2 = bytes.fromhex(s.recv(1024).strip().decode())
    x = [e1[i] ^ e2[i] for i in range(len(e1))]
    for p in PLAINTEXTS:
        ft = bytes([x[i] ^ p[i] for i in range(len(p))])
        if ft[:5] == b"flag{":
            print(ft)
            exit()
print("Failed. Solution has 9/25 success rate")
