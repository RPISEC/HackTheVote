#!/usr/bin/env python2
"""
Example solution for TOPKEK
"""

# Split up the kek string
with open('../handout/kek.txt') as f:
    kekked = f.read().split()

# Translating to binary
keks = {'KEK': '0', 'TOP': '1'}

# Convert to binary
binmsg = ''.join([keks[kek[:3]] * len(kek[3:]) for kek in kekked])

# Convert to ascii and print
print hex(int(binmsg, 2))[2:-1].decode('hex')
