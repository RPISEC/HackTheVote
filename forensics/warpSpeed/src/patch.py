#!/usr/bin/env python2

with open('ws.jpg', 'rb') as f:
    data = f.read()

# patch the width/height: 500x500 -> 1000x250
# Just undo this to solve, easier said than done :P
data = data.replace('\x01\xF4\x01\xF4', '\x00\xFA\x03\xE8', 1)

with open('../handout/warp_speed.jpg', 'wb') as f:
    f.write(data)
