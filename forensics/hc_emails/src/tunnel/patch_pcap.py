#!/usr/bin/env python2
"""
scapy is fucked, so gotta do this myself
"""

pname = 'tun.pcap'
with open(pname, 'rb') as f:
    pcap = f.read()

nullify = [
    '\x2d\x37\xb2\x4f',  # IP of the email server 45.55.178.79
    'email'  # Partial hostname of email server
]

pcap = reduce(lambda pcp, x: pcp.replace(x, '\x00' * len(x)), nullify, pcap)
with open('../../hillary.pcap', 'wb') as f:
    f.write(pcap)
