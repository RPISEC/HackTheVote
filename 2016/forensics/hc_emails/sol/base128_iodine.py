"""
Horrible looking direct port of
https://github.com/yarrick/iodine/blob/master/src/base128.c
"""

cb128 = \
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" \
    "\274\275\276\277" \
    "\300\301\302\303\304\305\306\307\310\311\312\313\314\315\316\317" \
    "\320\321\322\323\324\325\326\327\330\331\332\333\334\335\336\337" \
    "\340\341\342\343\344\345\346\347\350\351\352\353\354\355\356\357" \
    "\360\361\362\363\364\365\366\367\370\371\372\373\374\375"
rev128 = {ord(c): i for i, c in enumerate(cb128)}


def b128encode(data):
    data = map(ord, data)
    size = len(data)

    iin = 0
    buf = ''

    while 1:
        if iin >= size:
            break
        buf += cb128[((data[iin] & 0xfe) >> 1)]

        if iin >= size:
            break
        buf += cb128[((data[iin] & 0x01) << 6) | (((data[iin + 1] & 0xfc) >> 2) if (iin + 1 < size) else 0)]
        iin += 1

        if iin >= size:
            break
        buf += cb128[((data[iin] & 0x03) << 5) | (((data[iin + 1] & 0xf8) >> 3) if (iin + 1 < size) else 0)]
        iin += 1

        if iin >= size:
            break
        buf += cb128[((data[iin] & 0x07) << 4) | (((data[iin + 1] & 0xf0) >> 4) if (iin + 1 < size) else 0)]
        iin += 1

        if iin >= size:
            break
        buf += cb128[((data[iin] & 0x0f) << 3) | (((data[iin + 1] & 0xe0) >> 5) if (iin + 1 < size) else 0)]
        iin += 1

        if iin >= size:
            break
        buf += cb128[((data[iin] & 0x1f) << 2) | (((data[iin + 1] & 0xc0) >> 6) if (iin + 1 < size) else 0)]
        iin += 1

        if iin >= size:
            break
        buf += cb128[((data[iin] & 0x3f) << 1) | (((data[iin + 1] & 0x80) >> 7) if (iin + 1 < size) else 0)]
        iin += 1

        if iin >= size:
            break
        buf += cb128[(data[iin] & 0x7f)]
        iin += 1

    return buf


def b128decode(data):
    data = map(ord, data)
    size = len(data)

    iin = 0
    buf = ''
    while 1:
        if iin + 1 >= size or data[iin] == 0 or data[iin + 1] == 0:
            break
        buf += chr(((rev128[data[iin]] & 0x7f) << 1) | ((rev128[data[iin + 1]] & 0x40) >> 6))
        iin += 1

        if iin + 1 >= size or data[iin] == 0 or data[iin + 1] == 0:
            break
        buf += chr(((rev128[data[iin]] & 0x3f) << 2) | ((rev128[data[iin + 1]] & 0x60) >> 5))
        iin += 1

        if iin + 1 >= size or data[iin] == 0 or data[iin + 1] == 0:
            break
        buf += chr(((rev128[data[iin]] & 0x1f) << 3) | ((rev128[data[iin + 1]] & 0x70) >> 4))
        iin += 1

        if iin + 1 >= size or data[iin] == 0 or data[iin + 1] == 0:
            break
        buf += chr(((rev128[data[iin]] & 0x0f) << 4) | ((rev128[data[iin + 1]] & 0x78) >> 3))
        iin += 1

        if iin + 1 >= size or data[iin] == 0 or data[iin + 1] == 0:
            break
        buf += chr(((rev128[data[iin]] & 0x07) << 5) | ((rev128[data[iin + 1]] & 0x7c) >> 2))
        iin += 1

        if iin + 1 >= size or data[iin] == 0 or data[iin + 1] == 0:
            break
        buf += chr(((rev128[data[iin]] & 0x03) << 6) | ((rev128[data[iin + 1]] & 0x7e) >> 1))
        iin += 1

        if iin + 1 >= size or data[iin] == 0 or data[iin + 1] == 0:
            break
        buf += chr(((rev128[data[iin]] & 0x01) << 7) | (rev128[data[iin + 1]] & 0x7f))
        iin += 2

    return buf
