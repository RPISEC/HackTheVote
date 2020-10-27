import re
from pandare import Panda

panda = Panda(generic='x86_64')
panda.load_plugin('osi')

# Found using the asidstory plugin with the CLI interface
passwd_asid = 0x3bd7c000

flag_re = re.compile(rb"flag{[a-zA-Z0-9-_]*}")

pass_buf=b""
@panda.cb_virt_mem_after_write(enabled=False)
def mem_write(env, pc, addr, size, buf):
    # Build buffer of memory being written
    try:
        current_write = panda.virtual_memory_read(env, addr, size, fmt='str')
    except: # bad mem read
        return

    global pass_buf
    pass_buf += current_write

    # Search for password every 1k characters
    if len(pass_buf) > 1000:
        matches = flag_re.findall(pass_buf)
        if len(matches):
            print(matches)
        else:
            pass_buf = b""

@panda.cb_asid_changed
def asid_changed(cpu, old_asid, new_asid):
    '''
    Only enable callback when we're in passwd
    '''
    if new_asid == passwd_asid:
        panda.enable_callback('mem_write')
    else:
        panda.disable_callback('mem_write')
    return 0

panda.enable_memcb()
panda.run_replay('vote')
