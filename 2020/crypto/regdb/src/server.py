import secrets
import socketserver
import string

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


PLAINTEXTS = [
    b"Sandra R. Jackson;reg2;1728 Goldie Lane",
    b"Leo N. Shatley;reg1;2251 Sunburst Drive",
    b"Faye S. Ramsey;reg2;3186 Froebre Street",
    b"Charles C. Felix;reg3;2726 Locust Court",
]


with open("flag.txt", "rb") as f:
    PLAINTEXTS.append(f.read().strip())


def challenge(ioin, ioout):
    ioout.write(b"hello\n")
    key = secrets.token_bytes(nbytes=None)
    salt = secrets.token_bytes(nbytes=16)
    aesgcm = AESGCM(key)
    attempted_nonces = list()
    for attempt in range(len(PLAINTEXTS)):
        nonce = ioin.readline().strip()
        if (
            len(nonce) < 10
            or len(nonce) > 100
            or nonce in attempted_nonces
            or not all([c in string.printable.encode() for c in nonce])
        ):
            ioout.write(b"no\n")
            return
        attempted_nonces.append(nonce)
        ioout.write(
            aesgcm.encrypt(
                PBKDF2HMAC(
                    algorithm=hashes.MD5(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                    backend=default_backend(),
                ).derive(nonce),
                secrets.choice(PLAINTEXTS),
                None,
            )
            .hex()
            .encode()
            + b"\n"
        )


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
        with socketserver.ThreadingTCPServer(("0.0.0.0", 50007), MyTCPHandler) as server:
            server.serve_forever()
