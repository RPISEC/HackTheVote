
def bytes_to_polynomial(block, a):
    #https://meowmeowxw.gitlab.io/ctf/utctf-2020-crypto/
    poly = 0 
    # pad to 128
    bin_block = bin(bl(block))[2 :].zfill(128)
    # reverse it to count correctly, wrong don't reverse it lol
    # bin_block = bin_block[::-1]
    for i in range(len(bin_block)):
        poly += a^i * int(bin_block[i])
    return poly

def polynomial_to_bytes(poly):
    #https://meowmeowxw.gitlab.io/ctf/utctf-2020-crypto/
    return lb(int(bin(poly.integer_representation())[2:].zfill(128)[::-1], 2))

import struct

#from Crypto.Cipher import AES
#ecb = AES.new(b'\0'*16, AES.MODE_ECB)
#gcm = AES.new(b'\0'*16, AES.MODE_GCM, b'\0'*16)
#print([ecb.decrypt(p128le(r)) for r in roots])

from cryptography.hazmat.backends.openssl import backend as openssl_backend
#from cryptography.hazmat.backends import default_backend
#openssl_backend = default_backend()

from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import ECB, GCM

#key = b'\0'*16
key = b'key'*5+b'k'
ecb = Cipher(AES(key), ECB(), openssl_backend)
gcmenc = Cipher(AES(b'\0'*16), GCM(b'\0'*12), openssl_backend)

ecbenc = ecb.encryptor()
ecbdec = ecb.decryptor()
#suspect_H = u128be(ecbenc.update(p128be(1)))

chunks = lambda xs, n: [xs[i*n:(i+1)*n] for i in range(len(xs) // n)]

def blockplus(a, b):
    return p128le(u128le(a) ^ u128le(b))

def blockstar(a, b):
    'https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf'
    'Section 6.3 Multiplication Operation on Blocks'
    R = 0b11100001 << 120
    x = u128le(a)
    y = u128le(b)
    z = 0
    v = y
    for i in range(128):
        #if (x >> (127-i)) & 1:
        if (x >> i) & 1:
            z ^= v
        if v & 1:
            v = (v >> 1) ^ R
        else:
            v = (v >> 1)
    return p128le(z)

def mygcm(key, iv, msg):
    assert len(key) == 16
    assert len(iv) == 12
    assert len(msg) % 16 == 0
    ecb = Cipher(AES(key), ECB(), openssl_backend)
    ecbenc = ecb.encryptor()
    ctr = 0
    ctxt = b''
    tag = b'\0' * 16
    ctr += 1
    H = ecbenc.update(iv + struct.pack(">I", ctr))
    ctr += 1
    for chunk in chunks(msg, 16):
        block = blockplus(ecbenc.update(iv + struct.pack(">I", ctr)), chunk)
        ctr += 1
        ctxt += block
        tag = blockstar(tag, H)
        tag = blockplus(tag, block)

    tag = blockstar(tag, H)
    tag = blockplus(tag, struct.pack(">QQ", 0, len(ctxt)*8))

    tag = blockstar(tag, H)
    tag = blockplus(tag, H)
    return (ctxt, tag)

def theirgcm(key, iv, msg):
    assert len(key) == 16
    assert len(iv) == 12
    assert len(msg) % 16 == 0
    gcmenc = Cipher(AES(key), GCM(iv, min_tag_length=16), openssl_backend)
    enc = gcmenc.encryptor()
    ctxt = b''
    for chunk in chunks(msg, 16):
        ctxt += enc.update(chunk)
    enc.finalize()
    return (ctxt, enc.tag)

'''
mygcm(b'\0'*16, b'\0'*12, '')

print([suspect_H, ecbenc.update(p128be(0))])
print([ecbenc.update(p128le(1)), ecbenc.update(p128le(0))])
print('-'*5)
print([p128le(r) for r in roots])
print([p128be(r) for r in roots])
print('-'*5)
print([ecbdec.update(p128le(r)) for r in roots])
print([ecbdec.update(p128be(r)) for r in roots])
'''

'''
gcmdec = Cipher(AES(b'\0'*16), GCM(b'\0'*12, tags[0]), openssl_backend)
tmp = gcmdec.decryptor()
for chunk in chunks(ctxts[0], 16):
    print(repr(tmp.update(chunk)))
print(repr(tmp.finalize()))
print('-'*5)

print(repr(mygcm(b'\0'*16, b'\0'*12, '')))
print(repr(theirgcm(b'\0'*16, b'\0'*12, '')))
print('-'*5)
print(repr(mygcm(b'\0'*16, b'\0'*12, b'\0'*16)))
print(repr(theirgcm(b'\0'*16, b'\0'*12, b'\0'*16)))
'''
