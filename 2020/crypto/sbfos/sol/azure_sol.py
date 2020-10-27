#!/usr/bin/env python3

import struct
import codecs
import itertools

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def pack(x):
    return struct.pack('<QQ', x >> 64, (x) & (2**64-1))
def unpack(x):
    a, b = struct.unpack('<QQ', x)
    return a << 64 | b
def from_gf128(tag):
    return struct.pack('>QQ', tag >> 64, (tag) & (2**64-1))
def to_gf128(tag):
    a, b = struct.unpack(">QQ", tag)
    return a << 64 | b

def gf128_mul(x, y):
    R = 0xE1000000000000000000000000000000
    ''' Multiplication in GF(2^128). 
    The caller specifies the irreducible polynomial.
    '''
    z = 0
    for i in range(127, -1, -1):
        z ^= x * ((y >> i) & 1)      # if MSB is 0, XOR with 0, else XOR with x
        x = (x >> 1) ^ ((x & 1) * R) # shift and also reduce by R if overflow detected
    return z



key  = b'keykeykeykeykeyk'
iv   = b'iviviviviviv'
gcm = Cipher(algorithm=algorithms.AES(key), mode=modes.GCM(iv, min_tag_length=16), backend=default_backend())

ecb = Cipher(algorithm=algorithms.AES(key), mode=modes.ECB(), backend=default_backend())
ecbenc = ecb.encryptor()
ecbdec = ecb.decryptor()

def sanity_check():
    gcmenc = gcm.encryptor()
    ct = to_gf128(gcmenc.update(ecbenc.update(iv+b'\0\0\0\2'))) # encrypts to 0
    print("ciphertext (should be 0):", codecs.encode(pack(ct), "hex"))
    gcmenc.finalize()

    J0 = to_gf128(ecbenc.update(iv+b'\0\0\0\1'))
    print("J0: %016x " % (J0,))
    print("output of final gf128_mul():", codecs.encode(from_gf128(to_gf128(gcmenc.tag) ^ J0), 'hex'))
    print("  (decrypted value of J0  ):", codecs.encode(ecbdec.update(from_gf128(J0)), 'hex'))

    H = to_gf128(ecbenc.update(b'\0'*16))
    print("gf128_mul() key:", codecs.encode(from_gf128(H), "hex"))
    print("  (decrypts to):", codecs.encode(ecbdec.update(from_gf128(H)), "hex"))

    l = b'\x00'*15 + b'\x80'
    print("ell %016x" % (to_gf128(l),))
    a = gf128_mul(to_gf128(l), H)
    print("L * H: %016x" % (a,))
    a = a ^ J0
    print("computed tag: %016x" % (a,))
    print("computed tag matches real tag:", a == to_gf128(gcmenc.tag))

    print()

sanity_check()

pts = []
for c in range(ord('a'), ord('f')):
    pts.append(bytes(chr(c)*16, encoding='utf-8'))
cts = []
tags = []
for pt in pts:
    gcmenc = gcm.encryptor()
    ct = gcmenc.update(pt)
    gcmenc.finalize()
    tag = to_gf128(gcmenc.tag)
    cts.append(ct)
    tags.append(tag)

def calc_pretag(A, C, H):
    tag = 0
    for a in A:
        tag = gf128_mul(tag ^ to_gf128(a), H)
    for c in C:
        tag = gf128_mul(tag ^ to_gf128(c), H)

    footer = struct.pack(">QQ", len(A) * 8, len(C) * 128)
    tag = gf128_mul(tag ^ to_gf128(footer), H)

    return tag

H = to_gf128(ecbenc.update(b'\0'*16))
J0 = to_gf128(ecbenc.update(iv+b'\0\0\0\1'))

for ct, tag in zip(cts, tags):
    print('Computed tag matches openssl:', tag == (calc_pretag([], [ct], H)) ^ J0)

