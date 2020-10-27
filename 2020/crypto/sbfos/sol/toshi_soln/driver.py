from pwn import *
import pickle

context.log_level = 'DEBUG'

r = remote('sbfos.hackthe.vote', 51889) # process("./sbfos")
r.recvuntil("secure-boot$ ")
r.sendline("dump")
dump = b"\n".join(r.recvuntil("secure-boot$ ").split(b"\n")[:-2])
with open("dump.txt", "bw") as f:
    f.write(dump)

info("GENERATING SOLUTION WITH SAGE (THIS MAY TAKE A WHILE)")
r_sage = process(["sage", "./soln.sage"])
r_sage.wait_for_close()

with open("ctxts.pickle", "br") as f:
    possible_solns = pickle.load(f)

for i in possible_solns:
    r.sendline("load")
    r.send(i)
    if b"Successfully" in r.recvuntil("secure-boot$ "):
        r.sendline("boot")
        r.sendline("/bin//sh")
        r.interactive()
        r.close()
        break
else:
    fatal("Solution script broken, ping toshi or avi")
    r.close()
