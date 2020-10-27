#!/usr/bin/env python2
import os
import sys
import tempfile

import src.run as run
import src.protect as protect


print 'Linux Code Singing System:'
print 'Options:'
print '  (1) Sign ELF'
print '  (2) Run ELF'
print '>'

res = int(raw_input())

if res == 1:
    print 'Enter ELF file size:'
    size = int(raw_input())
    to_read = size
    data = ''

    if size < 0 or size > 0x1000*0x1000:
        print 'ELF file is too large!'
        exit(0)

    print 'Enter data:'

    while (to_read > 0):
        data += sys.stdin.read(to_read)
        to_read = size - len(data)

    print 'Got data',len(data)

    tf,elf_path = tempfile.mkstemp()
    with open(elf_path, 'w') as f:
        f.write(data)

    print elf_path

    try:
        protect.check_elf(elf_path)

        with open(elf_path, 'r') as f:
            data = f.read()
            print 'Signed ELF Size:', len(data)
            print 'Signed ELF Data:', data
    except:
        print 'Encounted Error...'
    finally:
        os.close(tf)
        os.unlink(elf_path)
        exit(0)

if res == 2:
    print 'Enter ELF file size:'
    size = int(raw_input())
    to_read = size
    data = ''

    if size < 0 or size > 0x1000*0x1000:
        print 'ELF file is too large!'
        exit(0)

    print 'Enter data:'

    while (to_read > 0):
        data += sys.stdin.read(to_read)
        to_read = size - len(data)

    print 'Got data',len(data)

    tf,elf_path = tempfile.mkstemp()
    with open(elf_path, 'w') as f:
        f.write(data)

    print elf_path

    try:
        run.verify_and_run(elf_path)
    finally:
        os.close(tf)
        os.unlink(elf_path)
        exit(0)



