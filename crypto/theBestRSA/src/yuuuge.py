#!/usr/bin/env python2
"""
Generates a new e,n,c for 'The Best RSA'
"""

from Crypto.Util.number import *
from random import choice

# Only use primes to calculate our mod
primes = [i for i in xrange(3, 2 ** 8) if isPrime(i)]
pows = {p: 0 for p in primes}

# Generate n
max_bits = 2 ** 19
n = 1
while True:
    c = choice(primes)
    if len(bin(n * c)[2:]) > max_bits:
        break

    n *= c
    pows[c] += 1

# Throwing out any unused primes
pows = [(k, v) for k, v in pows.iteritems() if v > 0]
print 'n =', n
print 'pows =', pows

# Calculate phi using the factors
phi = 1
for p, k in pows:
    phi *= pow(p, k - 1) * (p - 1)
print 'phi =', phi

# Make sure our e is ok with this
e = 0x10001
assert GCD(e, phi) == 1
print 'e =', e

# Read in our ptxt (flag)
with open('flag.gif', 'rb') as f:
    m = int(f.read().encode('hex'), 16)
    print 'm =', m

    assert m < n
    assert GCD(m, n) == 1

# Calculate d
d = inverse(e, phi)
print 'd =', d

c = pow(m, e, n)
print 'c =', c

# === VERIFYING IT WORKS ===
print '\nTrying to decrypt with d'
# print 'm:', pow(c, d, n)
# ^ Takes way too damn long

# CRT to the rescue!
# I already know the factors, so...
# No need to individually do this with all factors, can just raise them here
print 'Getting factors...'
factors = [p ** k for p, k in pows]

print 'Calculating phis...'
phis = [pow(p, k - 1) * (p - 1) for p, k in pows]

print 'Calculating complements...'
complements = [n / f_i for f_i in factors]

print 'Calculating inverses...'
inverses = [inverse(c_i, f_i) for f_i, c_i in zip(factors, complements)]

print 'Decrypting...'
dec_m = sum([pow(c, d % phi_i, f_i) * c_i * d_i for f_i, c_i, d_i, phi_i in zip(factors, complements, inverses, phis)]) % n

print 'dec', dec_m
assert dec_m == m  # pleeeaaaase

print '\nIf we made it here it worked!!'
print 'Saving to best_rsa.txt'
with open('../handout/best_rsa.txt', 'w') as f:
    f.write('e = {}\n'.format(e))
    f.write('n = {}\n'.format(n))
    f.write('c = {}\n'.format(c))
