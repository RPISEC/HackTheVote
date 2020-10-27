#!/usr/bin/env python
# Modified from https://mathiasbynens.be/notes/pbkdf2-hmac

import hashlib
import itertools
import string

TOTAL_LENGTH = 65
PREFIX = b""  # idk...

prefix_length = len(PREFIX)
brute_force_length = TOTAL_LENGTH - prefix_length
passwords = itertools.product(
    string.ascii_uppercase.encode(), repeat=brute_force_length
)
base_hasher = hashlib.md5()
base_hasher.update(PREFIX)
printable = string.printable.encode()

for item in passwords:
    hasher = base_hasher.copy()
    hasher.update(bytes(item))
    sha1_hash = hasher.digest()
    if all((c in printable for c in sha1_hash)):
        print(PREFIX + bytes(item), sha1_hash)
