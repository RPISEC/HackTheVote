import socket
import sys

#DOMAIN = "trumptrump.pwn.republican"
DOMAIN = "35.162.1.137"
PORT = 3609

#DOMAIN = "localhost"
#PORT=1337

tosign = int(open("../handout/trump.jpg", "rb").read().encode("hex"), 16)
n = int(open("../handout/trumpkey").readlines()[1].split()[1])
#create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((DOMAIN, PORT))

s.recv(1024)

#s.send(str(tosign) + '\r\n')
#print s.recv(4096)
s.send(str((pow(2,65537,n)*tosign)%n) + '\r\n')
r = s.recv(4096)
r = r[r.index("kid: ")+5:]
r = int(r[:r.index('\n')])
s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((DOMAIN, PORT))
s.send(str((r/2)%n) + '\r\n')

while True:
    sys.stdout.write(s.recv(1).strip())
    sys.stdout.flush()
