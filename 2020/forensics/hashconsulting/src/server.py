import hashlib
import string
import secrets
import socketserver
import struct
import subprocess
import tempfile
from hashlib import sha256

from generate_rules import generate_random_rule


NUM_WORDS = 100
NUM_RULES = 10
NUM_HASHES = 100
SUCCESS_RATE = 0.7

POW_HARDNESS = 9999999


# NUM_WORDS words randomly from /usr/share/dict/words
with open("dictionary.txt") as f:
    DICT = f.read().strip().split("\n")
    assert len(DICT) == NUM_WORDS
with open("dictionary2.txt") as f:
    DICT = f.read().strip().split("\n")
    assert len(DICT) == 1
    assert DICT[0] == "IBOHjYMP4wIvjXw"


def test_pow(chall, solution, hardness):
    h = sha256(chall + struct.pack("<Q", solution)).hexdigest()
    return int(h, 16) < 2 ** 256 / hardness


def printable_bytes(length=10):
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length)).encode()


def challenge(ioin, ioout):
    challenge = printable_bytes()
    ioout.write(challenge + b"\n")
    if not test_pow(challenge, int(ioin.readline().strip()), POW_HARDNESS):
        ioout.write(b"bye\n")
        return
    ioout.write(b"welcome\n")
    rules = [
        "".join([generate_random_rule() for y in range(secrets.randbelow(3) + 1)])
        for x in range(NUM_RULES)
    ]
    print(rules)

    with tempfile.NamedTemporaryFile(mode="w+") as rule_file:
        rule_file.write("\n".join(rules) + "\n")
        rule_file.flush()
        p = (
            subprocess.run(
                ["hashcat", "-r", rule_file.name, "--stdout", "dictionary.txt"],
                capture_output=True,
            )
            .stdout.strip()
            .split(b"\n")
        )
        assert len(p) == NUM_WORDS * NUM_RULES

    passwords = [secrets.choice(p[:-NUM_RULES]) for k in range(NUM_HASHES)]
    hashes = [hashlib.md5(pw + b"ahNgah7d").hexdigest() for pw in passwords]
    ioout.write("\n".join(hashes[:-1]).encode())

    ioout.write(b"\nsend guesses\n")
    recvd = set()
    for x in range(NUM_RULES):
        recvd.add(ioin.readline().strip())
    print(recvd)

    with tempfile.NamedTemporaryFile(mode="w+") as rule_file:
        rule_file.write("\n".join(rules) + "\n")
        rule_file.flush()
        p = (
            subprocess.run(
                ["hashcat", "-r", rule_file.name, "--stdout", "dictionary2.txt"],
                capture_output=True,
            )
            .stdout.strip()
            .split(b"\n")
        )
        assert len(p) == NUM_RULES
        tofind = set(p)
        print(tofind)

    suc = len(tofind & recvd) / len(tofind)
    ioout.write(f"you got {suc}: ".encode())
    if suc >= SUCCESS_RATE:
        print(suc)
        with open("flag.txt", "rb") as f:
            ioout.write(f.read() + b"\n")
    else:
        ioout.write(b"sorry\n")


class MyTCPHandler(socketserver.StreamRequestHandler):

    timeout = 5 * 60

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

    def handle(self):
        challenge(self.rfile, self.wfile)


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        print("run with either stdin or socket")
        exit(1)
    if sys.argv[1] == "stdin":
        challenge(sys.stdin.buffer, sys.stdout.buffer)
    elif sys.argv[1] == "socket":
        with socketserver.ThreadingTCPServer(
            ("0.0.0.0", 50007), MyTCPHandler
        ) as server:
            server.serve_forever()
