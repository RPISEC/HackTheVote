import re
import sys
from pwn import *
import subprocess

with open(sys.argv[1], 'r') as f:
    data = f.read()

with open(sys.argv[2], 'r') as f:
    key = f.read().strip()

start = '-----BEGIN EC PRIVATE KEY-----\n'
end = '\n-----END EC PRIVATE KEY-----'

mkey = key.split(end)[0].split(start)[1]

mkey = 'Private Key Scrubbed'.ljust(len(mkey), ' ')

mkey = start + mkey + end


assert(len(mkey) == len(key))

data = data.replace(key, mkey)

with open(sys.argv[3], 'wb') as f:
    f.write(data)



