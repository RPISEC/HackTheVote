"""
Solution for 'The Best RSA'

This takes around 20sec to run using sage in my vm
With plain python, it takes <3min

There are two main parts to this problem
    1.  The YUUUUUUGE modulus is actually trivial to factor, all factors turn out
        to be primes <= 251. Using this, we can calculate phi(n) using totient
        function identities:
            phi(a*b) = phi(a) * phi(b)
            phi(p^k) = (p-1) * p^(k-1)
        Once we have phi, d is simply inverse(e, phi)

    2.  We know c, d, and n now, so we can just do pow(c, d, n) right?? :'(
        The second part of the problem is due to the size of c, d, and n. Trying to
        calculate this using typical powmod functions (e.g. mult of squares)
        will take way too long. Instead, since we know the factors of n, we can use
        Chinese Remainder Theorem to drastically speed the decryption up

        code below, references:
            http://www.math-cs.gordon.edu/~kcrisman/mat338/section-25.html
            https://exploringnumbertheory.wordpress.com/2015/11/16/speeding-up-modular-exponentiation-using-crt/
- krx
"""
from sage.all import *


# Copied out of PyCrypto because sage's is broken for some reason
def inverse(u, v):
    """inverse(u:long, v:long):long
    Return the inverse of u mod v.
    """
    u3, v3 = long(u), long(v)
    u1, v1 = 1L, 0L
    while v3 > 0:
        q = divmod(u3, v3)[0]
        u1, v1 = v1, u1 - v1 * q
        u3, v3 = v3, u3 - v3 * q
    while u1 < 0:
        u1 = u1 + v
    return u1


# Read in e, n, c
with open('../handout/best_rsa.txt') as f:
    exec f.read()

print 'Factoring mod...'
pows = list(factor(n))

# Faster to just use the prime factors raised to their powers
factors = [p ** k for p, k in pows]

print 'Calculating phis of factors...'
# These individual phis will be used later in CRT
phis = [pow(p, k - 1) * (p - 1) for p, k in pows]

print 'Calculating phi(n)...'
phi = reduce(lambda a, x: a * x, phis)  # Product of all phis

print 'Calculating d...'
d = inverse(e, phi)

print 'Calculating complements...'
complements = [n // f_i for f_i in factors]

print 'Calculating inverses...'
inverses = [inverse(c_i, f_i) for f_i, c_i in zip(factors, complements)]

print 'Decrypting...'
m = sum([int(pow(c, d % phi_i, f_i)) * c_i * d_i for f_i, c_i, d_i, phi_i in zip(factors, complements, inverses, phis)]) % n
ptxt = hex(m).decode('hex')

print 'Saving to out.gif'
with open('out.gif', 'wb') as f:
    f.write(ptxt)

# flag{s4ved_by_CH1N4_0nc3_aga1n}
