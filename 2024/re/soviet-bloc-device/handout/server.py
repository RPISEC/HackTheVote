#!/usr/bin/env python3

import os
import subprocess

from pathlib import Path

BASE_DIR = Path(__file__).parent

for i in range(5):
    challenge = os.urandom(8)
    print(f'challenge: {challenge.hex()}')
    value = input('> ')

    p = subprocess.Popen([str(BASE_DIR / 'challenge'), value], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode == 1:
        print(err.decode(), end='')
        break
    else:
        result = bytes.fromhex(out.decode())
        if result == challenge:
            print('pass')
        else:
            print('fail')
            break

else:
    print(open('/flag').read().strip())
