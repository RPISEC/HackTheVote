import os
import sys

import signer

from capstone import *
from elftools.elf.elffile import ELFFile

def check_elf(elf_path):
    print "Checking ELF for security..."
    with open(elf_path, 'rb') as f:
        elf = ELFFile(f)

        entry = elf.header.e_entry

        text_sec = None
        for section in elf.iter_sections():
            if section.name == '.text':
                text_sec = section
                break

        if text_sec is None:
            print "Could not find text section"
            exit(0)

        text_data = text_sec.data()
        start_off = entry - text_sec.header.sh_addr 
        if start_off < 0 or start_off > len(text_data):
            print "Invalid entry point"
            exit(0)

    text_data = text_data[start_off:]

    md = Cs(
            CS_ARCH_X86,
            CS_MODE_64 if elf.header.e_machine == 'EM_X86_64' else CS_MODE_32
    )

    has_int3 = False
    print "Scanning assembly for viruses..."
    for i in md.disasm(text_data, len(text_data)):
        print("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))

        if i.mnemonic.lower() == 'int3':
            has_int3 = True
            continue

        if i.mnemonic.lower() in [
                'nop',
                'mov',
                'xor',
                'add',
                'or',
                'and',
                'sub',
                'dec',
                'inc',

                'int3',
                'ud2',
                'halt',
                ]:
            continue

        print("Invalid instruction %s"%i.mnemonic)
        exit(0)

    if not has_int3:
        print("Instructions must end in int3")
        exit(0)


    signer.sign_elf(elf_path, 'real_key')

if __name__ == '__main__':
    check_elf(sys.argv[1])



