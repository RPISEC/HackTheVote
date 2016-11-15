
"""
E:65537
N: 23377710160585068929761618506991996226542827370307182169629858568023543788780175313008507293451307895240053109844393208095341963888750810795999334637219913785780317641204067199776554612826093939173529500677723999107174626333341127815073405082534438012567142969114708624398382362018792541727467478404573610869661887188854467262618007499261337953423761782551432338613283104868149867800953840280656722019640237553189669977426208944252707288724850642450845754249981895191279748269118285047312864220756292406661460782844868432184013840652299561380626402855579897282032613371294445650368096906572685254142278651577097577263
"""



import base64, fractions, random


from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory

#yadda yadda want trump to sign a picture of himself, but he refuses


p = 134955970964761865940031063445510893988020931336273764563587663238225167942471229141862658079736973186051293910510112315349798637074001638538428793630988750767532020668624645312376387154122080395153810344375184336649776190489659134541032865580955021635454896824802459778956948925442053000932601979453509860259
q = 173224719095157225786899267831770772738189531522861416305034600149797318760936205670310937355773865996891313042040172039717396648853788343117712760231902902632812003825299636568110990428350309554023728109708487100522647031668454519099623779640708959085093371736161935801912108953701419293275945472078220407557

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m





N = p*q
phi = (p-1)*(q-1)

e = 65537
d = modinv(e, phi)

tosign = int(open("trump.jpg", "rb").read().encode('hex'), 16)
print len(bin(tosign)[2:])
signed = pow(tosign, d, N)

flagimage = open('trump_signed.jpg', 'rb').read().encode('hex')


failures = [
'You break down in tears at the mere presence of Donald; he gives you 15 years in Guantanamo Bay.',
'You let out a piercing shreik, similar to that of a howler monkey. You earn 15 years in Guantanamo Bay.',
'Before you can say anything, Trump gets flanked by a very angry-looking Grue. Trump is now in the ICU, and the Grue is serving 15 years in Guantanamo Bay.',
'Trump pulls off his mask, to show he is Guantanamo Bay. You serve 15 years in him.'
]

reasons = [
'I already met my quota for Guantanimo Bay inmates today',
'I just hit my goal of 10,000 steps on my FitBit',
'My horoscope said I should'
]

candidates = ['Bernie', 'Hillary', 'Cruz Missile', 'that one dude with the boot']

def fail(challsock):
    challsock.sendLine(failures[random.randint(0,len(failures)-1)])
    challsock.transport.loseConnection()



def getSign(challsock, signit):
    try:
        signit = int(signit)

        if signit == signed:
            success(challsock)
            return
        elif signit != tosign and signit != tosign % N:
            challsock.sendLine('Trump: Here ya go, kid: ' + str(pow(signit, d, N)))
            challsock.sendLine('Trump: Now get lost')
            challsock.sendLine('Wow, you\'ll never make a profit off of that, unless you can pull some magic and turn it in to his signature.')
            challsock.sendLine('Might as well vote for ' + candidates[random.randint(0,len(candidates)-1)])
            challsock.transport.loseConnection()
            return
        else:
            challsock.sendLine('WHADDYA TRYIN TO PULL HERE? I don\'t sign pictures of myself!')
            return
    except:
        fail(challsock)
        return





def success(challsock):
    print "Someone got it"
    challsock.sendLine('Trump looks shocked, appalled by the fact that he\'d sign a picture of himself for such a not-billionaire.')
    challsock.sendLine('Trump sprints away at a blinding 2mph, dropping what he was carrying.')
    challsock.sendLine('It\'s a stack of photos, you pick one up and look at it.')
    challsock.sendLine(flagimage)
    challsock.transport.loseConnection()
    return


class Chall(LineReceiver):
    #delimeter = b'\n'
    def connectionMade(self):
        self.MAX_LENGTH = 8008135
        self.sendLine('You see Donald Trump walking out of your local post office, carrying a large package in his tiny hands.')
        self.sendLine('(You approach Trump.)')
        self.sendLine('Donald Trimp: Whaddya want, huh? A signature?')
        self.sendLine('(This is your big chance)')
        self.transport.write('>')

    def lineReceived(self, data):
        try:
            data = int(data.strip())
            self.sendLine('Duneld Trump: Well, ' + reasons[random.randint(0, len(reasons)-1)] + ', so okay.')
            getSign(self, data)
        
        except:
            fail(self)
        
    def sendLine(self, s):
        self.transport.write(s + '\n')

class ChallFactory(Factory):
    def buildProtocol(self, addr):
        return Chall()


import sys

def main():
    reactor.listenTCP(3609, ChallFactory())
    reactor.run()

if __name__ == '__main__':
    main()


