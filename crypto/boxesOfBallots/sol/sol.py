from pwn import *
import string

def block_split(data, block_size):
    return [data[i:i+block_size] for i in range(0, len(data), block_size)]

def BC_ctxt_lookup(get_ctxt):
    known = ''
    block_size = 16
    alphabet = string.ascii_letters+string.digits+'_-{}'
    # Pad input data so we have 1 spot for a new char at end of the last block
    _pad = lambda x,y,z: x*((block_size-1)-len(y)+block_size*z)
    def find_match(known, block_num):
        """Query server and iterate possible byte values"""
        data = _pad(alphabet[1],known,block_num)
        for x in alphabet:
            ctxt = get_ctxt(data,known+x)
            yield (block_split(ctxt,block_size*2)[block_num], (data+known+x)[-16:])
    while True:
        # Calculate the block ID we are leaking a byte from
        block_num = (len(known))/block_size
        # Get ctxt that will leak 1 char of secret
        ctxt = get_ctxt(_pad(alphabet[1],known,block_num),'')
        # Lookup the leaky block to obtain 1 more char from the secret
        try:
            for c,p in find_match(known, block_num):
                if c == block_split(ctxt,block_size*2)[block_num]:
                    known += p[-1]
                    yield known[-1]
                    break
        except KeyError:
            # Lookup failed, probably finished finding secret
            raise StopIteration

def _connect(): return remote('boxesofballots.pwn.republican', 9001, level='error')

def get_ctxt(padding,secret):
    s = _connect()
    data = '{"data": "'+(padding+secret)+'", "op": "enc"}'
    s.send(data+"\n")
    ctxt = s.read(10000).split('"')[-2]
    s.sock.close()
    return ctxt

known = ''
for x in BC_ctxt_lookup(get_ctxt):
    known += x
    print known
    
