import hashlib
import os
import secrets
import socket
import string
import sys
import threading

from pwn import process

class NcPowser:
    def __init__(self, difficulty=6, prefix_length=16):
        self.difficulty = difficulty
        self.prefix_length = prefix_length

    def get_challenge(self):
        return (
            secrets.token_urlsafe(self.prefix_length)[: self.prefix_length]
            .replace("-", "b")
            .replace("_", "a").encode()
        )

    def verify_hash(self, prefix: bytes, answer: bytes):
        return hashlib.sha256(prefix+answer).hexdigest().endswith('0'*self.difficulty)


QEMU_CMD = """qemu-system-x86_64 -kernel ./bzImage -initrd ./rootfs.cpio.gz --append "rootfs=/dev/ram console=ttyS0" -nographic -m 200M""",
START_INPUT = b"ABCD>"
BLACKLIST = [b"__", b"import", b"globals", b"locals", b"open", b"dir", b"help"]

MENU = b"""[advanced console]
  add_fake_votes(state, candidate, N)  ; it's really this simple
  create_distraction(magnitude)        ; just in case
  destroy_all_records()                ; ...
"""

PRE_CMDS = """globals().clear();locals().clear();add_fake_votes=lambda x,y,z: True;create_distraction=lambda x: True;destroy_all_records=lambda: True"""


def do_chall(p: process, sock: socket.socket):
    p.writeline(PRE_CMDS)
    while True:
        try:
            line = p.readline().strip()
        except EOFError:
            return
        if line == START_INPUT:
            break
        if not line:
            continue

    sock.send(MENU)
    while True:
        sock.send(b"> ")
        inp = sock.recv(1024)
        if not inp:
            return
        inp = inp.strip()
        invalid = False
        for b in BLACKLIST:
            if b in inp:
                sock.send(b"[ERROR] illegal word:  " + b + b"\n")
                invalid = True
                break
        if invalid:
            continue

        if not all(chr(byte) in string.printable and byte >= 32 for byte in inp):
            sock.send(b"[ERROR] non-printable character\n")
            continue

        p.writeline(inp)

        while True:
            try:
                line = p.readline().strip()
            except EOFError:
                return
            if line == START_INPUT:
                break
            if not line or line == inp:
                continue
            if not b" MPY:" in line:
                sock.send(line + b"\n")
                continue
            sock.send(line.split(b" MPY:", 1)[1] + b"\n")


def do_pow(sock: socket.socket):
    p = NcPowser()
    chall = p.get_challenge()
    sock.send(
        f"Give me input where sha256({chall.decode()} + input).hexdigest().endswith('0'*{p.difficulty})\nAnswer (limit 1024 bytes)> ".encode()
    )
    answer = sock.recv(1024).strip()
    return p.verify_hash(chall, answer)


class ChildProc:
    def __init__(self, sock: socket.socket):
        self.p = None
        self.sock = sock
        self.solved_pow = False

    def run(self):
        assert self.sock is not None
        threading.Timer(60, self.pow_timer).start()
        if do_pow(self.sock):
            self.solved_pow = True
            threading.Timer(60 * 5, self.qemu_timer).start()
            self.sock.send(b"initializing challenge...\n")
            self.p = process(QEMU_CMD, shell=True)
            self.p.recvuntil(START_INPUT)
            try:
                do_chall(self.p, self.sock)
            except:
                self.end()

        else:
            if self.sock:
                self.sock.send(b"PoW failed\n")

    def end(self):
        assert self.sock is not None
        self.sock.close()
        self.sock = None
        if self.p:
            self.p.kill()
        sys.exit()

    def pow_timer(self):
        assert self.sock is not None
        if not self.solved_pow:
            print("pow timeout")
            self.sock.send(b"\nPoW timeout reached\n")
            self.end()

    def qemu_timer(self):
        assert self.sock is not None
        print("qemu timeout")
        self.sock.send(b"\ntimeout reached\n")
        self.end()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ssock:
        ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ssock.bind(("0.0.0.0", 31337))
        ssock.listen(1)
        print("listening...")
        while True:
            csock, addr = ssock.accept()
            if os.fork() == 0:
                cp = ChildProc(csock)
                cp.run()
                sys.exit()
            else:
                # parent
                csock.close()


if __name__ == "__main__":
    main()
