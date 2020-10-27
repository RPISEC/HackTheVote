#!/usr/bin/env python2


def binpad(c):
    # Makes sure the binary is 8 bits
    b = bin(ord(c))[2:]
    return '0' * (8 - len(b)) + b


def binchunk(b):
    # ex: '1101110011' -> ['11', '0', '111', '00', '11']
    chunks = []
    buf = ''
    for c in b:
        if len(buf) == 0 or c == buf[0]:
            buf += c
        else:
            chunks.append(buf)
            buf = c
    if buf != '':
        chunks.append(buf)
    return chunks


# Translating to kek
keks = {'0': 'KEK', '1': 'TOP'}

flag = "flag{T0o0o0o0o0P______1m_h4V1nG_FuN_r1gHt_n0W_4R3_y0u_h4v1ng_fun______K3K!!!}"
kekked = ' '.join(['{}{}'.format(keks[chnk[0]], '!' * len(chnk)) for chnk in binchunk(''.join(map(binpad, flag)))])

with open('../handout/kek.txt', 'w') as f:
    f.write(kekked)
print kekked
