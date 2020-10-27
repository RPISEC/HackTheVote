#!/usr/bin/env python2
from PIL import Image


def read(path):
    with open(path, 'rb') as f:
        return f.read()


def binpad(c):
    # Makes sure the binary is 8 bits
    b = bin(ord(c))[2:]
    return '0' * (8 - len(b)) + b


# Get the 7z pass
with open('truecrypt/pass.txt') as f:
    password = f.read().strip()

# Prepare the picks image by embedding the 7z pass in lsb
binpass = map(int, ''.join(map(binpad, password)))
img = Image.open('picks.png').convert('RGB')
w, h = img.size
for y in xrange(h):
    if len(binpass) > 0:
        for x in xrange(w):
            if len(binpass) > 0:
                r, g, b = img.getpixel((x, y))
                img.putpixel((x, y), (r, g, (b & 0xfe) | binpass.pop(0)))
img.save('picks_lsb.png', 'PNG')

picks = read('picks_lsb.png')
data7z = read('truecrypt/S3CR3T.7z')
keys = read('truecrypt/keys.png')

# Hide 7z from carvers
data7z = '8' + data7z[1:]  # >:DDDDD

# Create the final image
with open('../handout/lockpick.png', 'wb') as f:
    f.write(picks + data7z + keys)
