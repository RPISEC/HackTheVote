#!/usr/bin/env python2

with open('../handout/warp_speed.jpg', 'rb') as f:
    data = f.read()

# patch the width/height: 1000x250 -> 500x500
data = data.replace('\x00\xFA\x03\xE8', '\x01\xF4\x01\xF4', 1)

with open('flag.jpg', 'wb') as f:
    f.write(data)
