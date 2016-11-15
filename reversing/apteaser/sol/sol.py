#!/usr/bin/python2
import dpkt
import sys
import socket
import base64
import struct

# Shitty MSVC rand implementation
MULTIPLIER = 214013
INCREMENT = 2531011
MODULUS = 2**31
SHIFT_BITS = 16
def msvc_rand(state, a, c, m, masked_bits):
    while(True):
        state = (a * state + c) % m
        yield state >> masked_bits
def from_seed(seed):
    for x in msvc_rand(seed, a=MULTIPLIER, c=INCREMENT, m=MODULUS, masked_bits=SHIFT_BITS):
        yield x

# Open pcap
filename = sys.argv[1]
f = open(filename)
pcap = dpkt.pcapng.Reader(f)
# output file
fout = open('out.bmp', 'wb')

# ctxt is sent here
tgt_dest = '128.213.48.117'

# Parse packets to get (timestamp,ciphertext) pairs to decrypt
is_ctxt = False
ctxt_pkts = []
for ts,buf in pcap:
    eth = dpkt.ethernet.Ethernet(buf)
    if eth.type != dpkt.ethernet.ETH_TYPE_IP:
        continue
    ip = eth.data
    # ignore packets not to tgt_dest
    if ip.p != dpkt.ip.IP_PROTO_TCP or socket.inet_ntoa(ip.dst) != tgt_dest:
        continue
    tcp = ip.data
    # ignore packets without data or with wrong size
    if len(tcp.data) < 2000:
        continue
    # Decrypt ctxt using packet timestamp as msvc rand seed
    seed = int(ts)
    ctxt = tcp.data
    # Seed rng
    rng = from_seed(seed)
    # Decrypt this packet
    for i in range(0, len(ctxt), 4):
        k = next(rng)
        ptxt = struct.unpack("<I", ctxt[i:i+4].zfill(4))[0]^k
        ptxt = struct.pack("<I",ptxt)
        # Write results
        fout.write(ptxt)

f.close()
fout.close()

