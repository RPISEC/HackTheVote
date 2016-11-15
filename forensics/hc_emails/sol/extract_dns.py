#!/usr/bin/env python
"""
Modified version of StalkR's script from
http://blog.stalkr.net/2010/10/hacklu-ctf-challenge-9-bottle-writeup.html

This version doesn't use any Popen calls, and ignores any errors while decoding
- krx
"""

import zlib
from base64 import b64encode, b64decode, b32encode, b32decode
from string import translate, maketrans

from scapy.all import *

from base128_iodine import b128encode, b128decode

infile, outfile = "../handout/hillary.pcap", "extracted.pcap"
tld = ".hillary.clinton.io."

upstream_encoding = 128
# and no downstream encoding (type NULL)

# Translation tables for iodine's encoding
enctrans = {
    32: maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ012345'),
    64: maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/', 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-0123456789+')
}

dectrans = {
    32: maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ012345', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'),
    64: maketrans('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-0123456789+', 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/')
}

# iodine encoders/decoders
encoders = {
    32: lambda x: translate(b32encode(x), enctrans[32]),
    64: lambda x: translate(b64encode(x), enctrans[64]),
    128: b128encode
}

decoders = {
    32: lambda x: b32decode(translate(x, dectrans[32])),
    64: lambda x: b64decode(translate(x, dectrans[64])),
    128: b128decode
}


def encoder(base, encode="", decode=""):  # base=[32,64,128]
    funcmap, data = (encoders, encode) if len(encode) > 0 else (decoders, decode)
    return funcmap[base](data)


def uncompress(s):
    try:
        return zlib.decompress(s)
    except zlib.error:
        return False


def b32_8to5(a):
    return "abcdefghijklmnopqrstuvwxyz012345".find(a.lower())


def up_header(p):
    return {
        "userid": int(p[0], 16),
        "up_seq": (b32_8to5(p[1]) >> 2) & 7,
        "up_frag": ((b32_8to5(p[1]) & 3) << 2) | ((b32_8to5(p[2]) >> 3) & 3),
        "dn_seq": (b32_8to5(p[2]) & 7),
        "dn_frag": b32_8to5(p[3]) >> 1,
        "lastfrag": b32_8to5(p[3]) & 1
    }


def dn_header(p):
    return {
        "compress": ord(p[0]) >> 7,
        "up_seq": (ord(p[0]) >> 4) & 7,
        "up_frag": ord(p[0]) & 15,
        "dn_seq": (ord(p[1]) >> 1) & 15,
        "dn_frag": (ord(p[1]) >> 5) & 7,
        "lastfrag": ord(p[1]) & 1,
    }


# Extract packets from DNS tunnel
# Note: handles fragmentation, but not packet reordering (sequence numbers)
p = rdpcap(infile)
dn_pkt, up_pkt = '', ''
datasent = False
E = []
for i in range(len(p)):
    if i % 1000 == 0:  # Just for progress
        print i

    if not p[i].haslayer(DNS):
        continue
    if DNSQR in p[i]:
        if DNSRR in p[i] and len(p[i][DNSRR].rdata) > 0:  # downstream/server
            d = p[i][DNSRR].rdata
            if datasent:  # real data and no longer codec/fragment checks
                dn_pkt += d[2:]
                if dn_header(d)['lastfrag'] and len(dn_pkt) > 0:
                    u = uncompress(dn_pkt)
                    if u:
                        # Include the packet if decoding succeeded,
                        # ignore it and move on otherwise
                        E += [IP(u[4:])]
                    dn_pkt = ''
        else:  # upstream/client
            d = p[i][DNSQR].qname
            if d[0].lower() in "0123456789abcdef":
                datasent = True
                up_pkt += d[5:-len(tld)].replace(".", "")
                if up_header(d)['lastfrag'] and len(up_pkt) > 0:
                    u = uncompress(encoder(upstream_encoding, decode=up_pkt))
                    if u:
                        # Include the packet if decoding succeeded,
                        # ignore it and move on otherwise
                        E += [IP(u[4:])]
                    up_pkt = ''

wrpcap(outfile, E)
print "Successfully extracted %i packets into %s" % (len(E), outfile)
