import os
import sys
import signer
import tempfile
import shutil
import subprocess

def verify_and_run(elf_path):
    signer.verify_elf(elf_path, 'real_key.pub')

    elf_name = os.path.basename(elf_path)
 
    root = tempfile.mkdtemp()
    os.chmod(root, 0775)

    try:
        new_elf_path = os.path.join(root, elf_name)
        shutil.copyfile(elf_path, new_elf_path)
        os.chmod(new_elf_path, 0555)

        flag_path = os.path.join(root, 'flag')
        shutil.copyfile('flag', flag_path)
        #os.makedirs(os.path.join(root,'lib'))
        #shutil.copyfile('/lib/ld-linux.so.2',
        #        os.path.join(root,'lib','/lib/ld-linux.so.2'))

        os.chmod(flag_path, 0444)


        # Run in a setuid sandbox
        subprocess.call([
            os.path.join(os.path.dirname(__file__),'./run_elf'), root, elf_name])
    finally:
        shutil.rmtree(root)

if __name__ == '__main__':
    verify_and_run(sys.argv[1])

