import os
import sys
from elftools.elf.elffile import ELFFile

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as PKCS1

def get_elf_hash(b):
    with open(b, 'rb') as f:
        elf = ELFFile(f)

        hd = ''
        hd += '%08x'%elf.header.e_entry

        hd += 'SEGMENTS'
        # Add program headers
        hd += '%08x'%elf.header.e_phnum

        for seg in elf.iter_segments():
            hd += seg.header.p_type
            hd += '%08x'%seg.header.p_offset
            hd += '%08x'%seg.header.p_vaddr
            hd += '%08x'%seg.header.p_filesz
            hd += '%08x'%seg.header.p_memsz

        # Add section headers
        hd += 'SECTIONS'
        hd += '%08x'%elf.header.e_shnum

        build_id = None

        for sec in elf.iter_sections():
            if sec.header.sh_type == 'SHT_NOTE' and sec.name == '.note.gnu.build-id':
                build_id = sec
                continue

            hd += sec.header.sh_type
            hd += sec.name
            hd += '%08x'%sec.header.sh_addr
            hd += '%08x'%sec.header.sh_offset
            hd += '%08x'%sec.header.sh_size
            hd += sec.data().decode('latin-1')

        if build_id is None:
            print("This binary does not have a build_id section. Please compile with gcc-sig.sh")
            exit(0)

        if len(build_id.data()) < 256+16:
            print("This binary does not a big enough build_id section to hold the signature. Please compile with gcc-sig.sh")
            exit(0)

        current_sig = build_id.data()[16:]

    elf_hash = SHA256.new()
    elf_hash.update(hd.encode('latin-1'))
    print 'ELF hash:', elf_hash.hexdigest()
    return elf_hash, build_id, current_sig

def sign_elf(elf_path, key_path):
    print "Signing ELF..."
    elf_hash, build_id, current_sig = get_elf_hash(elf_path)
    # Generate new key
    if not os.path.exists(key_path):
        key = RSA.generate(2048)
        with open(key_path,'wb') as f:
            f.write(key.exportKey('PEM'))
        pubkey = key.publickey()
        with open(key_path+'.pub','wb') as f:
            f.write(pubkey.exportKey('PEM'))

    else:
        with open(key_path,'rb') as f:
            key = RSA.importKey(f.read())

    signer = PKCS1.PKCS115_SigScheme(key)

    assert(key.can_sign())

    sig = signer.sign(elf_hash)

    with os.fdopen(os.open(elf_path, os.O_RDWR | os.O_CREAT), 'rb+') as f:
        f.seek(build_id.header.sh_offset + 16)
        f.write(sig)
    print "ELF has been signed"

def verify_elf(elf, key_path):
    elf_hash, build_id, current_sig = get_elf_hash(elf)
    with open(key_path,'rb') as f:
        key = RSA.importKey(f.read())

    verifier = PKCS1.PKCS115_SigScheme(key)

    res = verifier.verify(elf_hash, current_sig)

    if not res:
        print "The ELF's signature is invalid!"
        exit(0)
    print "The ELF's signature is valid"

if __name__ == '__main__':
    op = sys.argv[1]
    elf_path = sys.argv[2]
    key_path = sys.argv[3]
    if op == 'sign':
        sign_elf(elf_path, key_path)
    elif op == 'verify':
        verify_elf(elf_path, key_path)


