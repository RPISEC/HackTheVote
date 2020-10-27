# TOPKEK

This is an encoding of a binary string with two parts:

1. `TOP` and `KEK` translate to `1` and `0` respectively
2. The number of `!`'s after a `TOP` of `KEK` is how many `1`'s or `0`'s there

So for example, `11010011` is encoded as:

```
TOP!! KEK! TOP! KEK!! TOP!!
```

And going backwards:

```
TOP!! -> 11
KEK!  -> 0
TOP!  -> 1
KEK!! -> 00
TOP!! -> 11

= 11010011
```

Example solution:
```python
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
```
