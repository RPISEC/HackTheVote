flag = "flag{0b4ma_1s_sT1ll_tH3_Pr3s1D3nT_0f_mY_H34rt}"
from Crypto.PublicKey import RSA
from random import random, randint
import smtplib, sys, os, base64
from pyasn1.type import univ
from pyasn1.codec.der import encoder as der_encoder



def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

try:
    os.rmdir('../handout/emails')
    os.rmdir('../handout/pubkeys')
except:
    pass

try:

    os.mkdir('../handout/emails')
    os.mkdir('../handout/pubkeys')
except:
    pass

e = 97
flagkey = ""
while True:
    flagkey = RSA.generate(1024)
    if egcd((flagkey.p-1)*(flagkey.q-1), e)[0] == 1:
        flagkey.e = 97
        break
flagenc = pow(int(flag.encode('hex'), 16), flagkey.e, flagkey.n)
open("../handout/flag", 'wb').write("(" + str(flagkey.e) + ',' + str(flagenc) + ',' + str(flagkey.n) + ')')
open("flagkey", 'wb').write(str(flagkey.e) + '\n' + str(flagkey.n) + '\n' + str(flagkey.d))

keylen = 2048
e = 17

print len(str(flagkey.d))

fakeflag = ("""Subject: My Fellow DNC Members
Content: Keep this safe <MISSING>"""+ str(flagkey.d)[-110:] + ", that's the key we agreed on.")

print fakeflag

print "email is " + str(len(bin(int(fakeflag.encode('hex'),16))[2:])) + " bits"


class DNCrep:
    def __init__(self, name, p, q):
        self.name = name
        self.p = p
        self.q = q

    def enc(self, s):
        return pow(int(s.encode('hex'), 16), 17, self.p*self.q)


reps = []
used = []

alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVEXYZ1234567890"
#if not os.path.isfile("reps.txt"):
if True:
    while len(reps) < 170:
        curr = ""
        for j in xrange(12):
            curr += alpha[randint(0,len(alpha)-1)]
        if not curr in used:
            while True:
                newkey = RSA.generate(keylen)
                q = newkey.q
                p = newkey.p
                #n = p*q
                phi = (p-1)*(q-1)
                if egcd(phi, 17)[0] == 1:
                    #encs.append([str(e), str(n), str(pow(int(fake.encode('hex'), 16), e, n))])
                    reps.append(DNCrep(curr, p, q))
                    used.append(curr)
                    break
        if len(reps) % 10 == 0:
            print "#reps: " + str(len(reps))

    raw_input("really?")
    f = open("reps.txt", 'wb')
    for rep in reps:
        f.write(rep.name+','+str(rep.p)+','+str(rep.q)+'\n')
    f.close()
else:
    for line in open("reps.txt", 'rb').readlines():
        line = line.split(',')
        reps.append(DNCrep(line[0], int(line[1]), int(line[2])))
try:
    sender = 'hillary@hillaryclinton.com'

    smtpObj = smtplib.SMTP('localhost', 1337)
    
    for j in xrange(10):
       
        finfake = ""
        for i in xrange(len(fakeflag)):
            if random() > 0.5:
                finfake += fakeflag[i]
            else:
                finfake += chr(35)
        
        for i in xrange(17):
            rep = reps[(j*17)+i]
            smtpObj.sendmail(sender, rep.name + '@dnc.gov', "Date: 4/"+str(j+1)+"/16\nEncryption Type: RSA-2048\nContent: "+hex(rep.enc(str(finfake)))[2:-1])
            #print "Successfully sent email from " + rep.name + '@dnc.gov'
except:   
    print "Error: unable to send email"




for line in open("reps.txt", 'rb').readlines():
    line = line.split(',')
    n = int(line[1])*int(line[2])
    
    pkcs1_seq = univ.Sequence()
    pkcs1_seq.setComponentByPosition(0, univ.Integer(n))
    pkcs1_seq.setComponentByPosition(1, univ.Integer(17))

    
    f = open("../handout/pubkeys/" + line[0], "wb")
    f.write('-----BEGIN RSA PUBLIC KEY-----\n')
    f.write(base64.encodestring(der_encoder.encode(pkcs1_seq)))
    f.write('-----END RSA PUBLIC KEY-----')
    f.close()
