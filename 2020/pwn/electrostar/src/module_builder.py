import sys
from pwn import *
import subprocess
from elftools.elf.elffile import ELFFile

b = sys.argv[1]

for l in subprocess.check_output(['readelf','-h',b]).split('\n'):
    l = l.strip()
    if l.startswith('Entry point address:'):
        entry = int(l.split()[-1], 16)
        break


syms = {}

for l in subprocess.check_output(['readelf','-s',b]).split('\n'):
    l = l.strip().split()
    if len(l) == 0:
        continue
    if l[-1] == 'func_table' and not 'func_table' in syms:
        syms['func_table'] = int(l[1], 16)
    if l[-1] == 'get_func_table' and not 'get_func_table' in syms:
        syms['get_func_table'] = int(l[1], 16)

sections = []

with open(b,'rb') as f:
    elf = ELFFile(f)

    for section in elf.iter_sections():
        if section.name in ['.text','.data','.rodata','.bss']:
            sections.append({
                'size':section.header['sh_size'],
                'offset':section.header['sh_addr'],
                'data':section.data()
                })

sections.sort(key=lambda x:x['offset'])


context.arch='amd64'

if len(sys.argv) > 3:
    meta = chr(int(sys.argv[3]))
else:
    meta = chr(0)

out = asm("lea rax, [rip+%u]\n jmp rax"%(entry-7))

for s in sections:
    out = out.ljust(s['offset'],'\xcc')
    out += s['data']

jmp_off = syms['get_func_table'] + 3
rip_rel = syms['func_table'] - syms['get_func_table'] - 7
out = out[:jmp_off] + p32(rip_rel) + out[jmp_off+4:]

with open(sys.argv[2],'w') as f:
    f.write(meta + out)
