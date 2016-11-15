import sys, random
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory



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



#################SERVER SIDE STUFF



flag = "flag{IV_wh4t_y0u_DiD_Th3r3}"



#IV = [random.randint(128,1337) for x in xrange(9)]

charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=~`{}[]:\";'<>?,./\\|"

seed = ''.join(charset[random.randint(0,len(charset)-1)] for i in xrange(9*random.randint(1,2)))



def fixord(a):
    count = 0
    o = [[0 for i in xrange(3)] for i in xrange(3)]
    for start in xrange(0,3):
        for j in xrange(0, 3):
            o[start][j] = a[j][start]
            count += 1
    return o


def chall(challsock, IV):
    seed = ''.join(charset[random.randint(0,len(charset)-1)] for i in xrange(9*random.randint(1,2)))

    blocks = genBlockMatrix(pad(IV + [ord(c) for c in seed]))

    res = [[0 for i in xrange(3)] for i in xrange(3)]
    for i in xrange(len(blocks)):
        res = fixmatrix(res, blocks[i])


    challsock.sendLine("SEED: " + str(seed))
    for row in res:
        challsock.sendLine(str(row[0]) + " " + str(row[1]) + " " + str(row[2]))


class Chall(LineReceiver):
    def connectionMade(self):
        self.delimeter = '\n'
        self.MAX_LENGTH = 1337

        self.IV = [random.randint(128,1337) for x in xrange(9)]

        chall(self, self.IV)
        reactor.callLater(1, self.transport.loseConnection)

    def sendLine(self, s):
        self.transport.write(str(s) + '\n')

    def dataReceived(self, data):
        data = data.strip().replace('[', '').replace(']', '').replace(' ', '').split(',')
        if len(data) != 9:
            return False

        for i in xrange(len(self.IV)):
            if str(self.IV[i]) != str(data[i]):
                return False

        self.sendLine(flag)


class ChallFactory(Factory):
    def buildProtocol(self, addr):
        return Chall()

def main():
    reactor.listenTCP(4201, ChallFactory())
    reactor.run()


if __name__ == '__main__':
    main()
###########################END SERVER STUFF

