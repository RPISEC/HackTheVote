#################SERVER SIDE STUFF
import socket, random


def fixord(a):
	count = 0
	o = [[0 for i in xrange(3)] for i in xrange(3)]
	for start in xrange(0,3):
		for j in xrange(0, 3):
			o[start][j] = a[j][start]
			count += 1
	return o

def solve(res, seed):
	firstres = res
	res = []
	for i in xrange(3):
		res += firstres[i]
	blocks = genBlockMatrix(pad(res + [ord(c) for c in seed]))
	res = [[0 for x in xrange(3)] for x in xrange(3)]

	if len(blocks) > 2:
		for i in xrange(len(blocks)):
			res = fixmatrix((res), fixord(blocks[i]))
	else:
		for i in xrange(len(blocks)):
			res = fixmatrix(fixord(res), blocks[i])

	solution = []
	for row in fixord(res):
		solution += row
	return solution

def printmat(matrix):
	for row in matrix:
		for value in row:
			print value,
		print ""
	print ""


def pad(s):
	if len(s)%9 == 0:
		return s
	for i in xrange((9-(len(s)%9))):
		s.append(0)
	return s

def genBlockMatrix(s):
	outm = [[[7 for x in xrange(3)] for x in xrange(3)] for x in xrange(len(s)/9)]
	for matnum in xrange(0,len(s)/9):
		for y in xrange(0,3):
			for x in xrange(0,3):
				outm[matnum][y][x] = s[(matnum*9)+x+(y*3)]
	return outm

def fixmatrix(matrixa, matrixb):
	out = [[0 for x in xrange(3)] for x in xrange(3)]	
	for rn in xrange(3):
		for cn in xrange(3):
			out[cn][rn] = (int(matrixa[rn][cn])|int(matrixb[cn][rn]))&~(int(matrixa[rn][cn])&int(matrixb[cn][rn]))
	return out

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("vermatrix.pwn.democrat", 4201))

remote = True

if remote:
	#s.recv(128) #this is different in remote and local?????? Need this remote
	d = s.recv(128) 
else:
	d = s.recv(128)[32:]

#internet, how do you work?

res = []
print d
for i in xrange(1,4):
	res.append([int(c) for c in d[6:].split("\n")[i].split(" ")])

print d[6:].split("\n")[0].strip()
print res
print d[6:].split("\n")[0].strip()
sol = str(solve(res, d[6:].split("\n")[0].strip())).replace('[', '').replace(']', '')
print sol
s.send(sol + '\n')

print s.recv(128)
