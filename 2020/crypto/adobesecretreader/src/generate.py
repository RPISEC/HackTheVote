#!/usr/bin/env python3
import os
import ast
import sys
import random
from Crypto.Util.number import getPrime, long_to_bytes, bytes_to_long

from secrets import flag, K
from obfuscate import obfuscate as obf

prime = None
poly = []
shares = set()

def eval_poly(x):
    y = 0
    for i, c in enumerate(poly):
        y = (y + c * pow(x, i, prime)) % prime
    return y

def setup():
    global prime, poly
    if os.path.exists('prime'):
        with open('prime') as f:
            prime = ast.literal_eval(f.read())
    else:
        with open('prime', 'w+') as f:
            prime = getPrime(8*len(flag))
            f.write(str(prime))

    if os.path.exists('poly'):
        with open('poly') as f:
            poly = ast.literal_eval(f.read())
            assert poly[0] == bytes_to_long(flag.encode()), "secrets don't match up"
    else:
        with open('poly', 'w+') as f:
            poly = [0] * K
            for i in range(1, K):
                poly[i] = random.randrange(1, prime)
            poly[0] = bytes_to_long(flag.encode())
            f.write(str(poly))

def gen_shares():
    for _ in range(K):
        x = random.randrange(1, prime)
        while x in shares:
            x = random.randrange(1, prime)
        shares.add(x)
        yield x, eval_poly(x)

def main():
    setup()
    assert bytes_to_long(flag.encode()) < prime, "secret out of range"
    assert K == len(poly), "invalid polynomial"
    with open('message', 'wb+') as f:
        f.write(obf(f'p = {prime}'))
        for x, y in gen_shares():
            f.write(obf(f'x = {x}, y = {y}'))

if __name__ == '__main__':
    main()

