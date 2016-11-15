'''
Category: Crypto
Challenge Name: Boxes of Ballots
Points: 200
Author: Unix-Dude
Flag: flag{Source_iz_4_noobs}
'''

from twisted.internet import reactor, protocol
from Crypto.Cipher import AES
import traceback
import json

PORT = 9001

KEYSIZE = 16
SECRET = "flag{Source_iz_4_noobs}"

def pad(instr, length):
        if(length == None):
            pass  
        elif(len(instr) % length == 0):
                return instr
        else:
                return instr + ' ' * (length - (len(instr) % length ))

def encrypt_block(key, plaintext):
        encobj = AES.new(key, AES.MODE_ECB)
        return encobj.encrypt(plaintext).encode('hex')

def decrypt_block(key, ctxt):
        decobj = AES.new(key, AES.MODE_ECB)
        return decobj.decrypt(ctxt).encode('hex')

def xor_block(first,second):
        '''
        Return a string containing a XOR of bytes in first with second
        '''
        if(len(first) != len(second)):
                return -1

        first = list(first)
        second = list(second)
        for i in range(0,len(first)):
                first[i] = chr(ord(first[i]) ^ ord(second[i]))
        return ''.join(first)

def encrypt_cbc(key,IV, plaintext):
        '''
        High Level Function to encrypt things in AES CBC Mode.
        1: Pad plaintext if necessary. 
        2: Split plaintext into blocks of length <keysize>
        3: XOR Block 1 w/ IV
        4: Encrypt Blocks, XOR-ing them w/ the previous block. 
        '''
        if(len(plaintext) % len(key) != 0):
                plaintext = pad(plaintext,len(key))
        blocks = [plaintext[x:x+len(key)] for x in range(0,len(plaintext),len(key))]
        for i in range(0,len(blocks)):
                if (i == 0):
                        ctxt = xor_block(blocks[i],IV)
                        ctxt = encrypt_block(key,ctxt)
                else:
                        tmp = xor_block(blocks[i],ctxt[-1 * (len(key) * 2):].decode('hex'))     #len(key) * 2 because ctxt is an ASCII string that we convert to "raw" binary.          

                        ctxt = ctxt + encrypt_block(key,tmp)
        return ctxt

def decrypt_cbc(key,IV,ctxt):
        '''
        High Level function to decrypt thins in AES CBC mode.
        1: Split Ciphertext into blocks of len(Key)
        2: Decrypt block.
        3: For the first block, xor w/ IV. For the others, xor with last ciphertext block.
        '''
        ctxt = ctxt.decode('hex')
        if(len(ctxt) % len(key) != 0):
                return -1
        blocks = [ctxt[x:x+len(key)] for x in range(0,len(ctxt),len(key))]
        for i in range(0,len(blocks)):
                if (i == 0):
                        ptxt = decrypt_block(key,blocks[i])
                        ptxt = xor_block(ptxt.decode('hex'),IV)
                else:
                        tmp = decrypt_block(key,blocks[i])
                        tmp = xor_block(tmp.decode('hex'),blocks[i-1])
                        ptxt = ptxt + tmp
        return ptxt



class MyServer(protocol.Protocol):
    
    def encrypt_data(self, encData):
        try:
            if (self.debug):
                enc = encrypt_cbc(self.key, self.iv, encData['data'])
            else:
                 enc = encrypt_cbc(self.key, self.iv, encData['data'] + SECRET)
        
            resp = {'Status':'ok','data':enc}
            self.transport.write(json.dumps(resp))
        except:
            if (self.debug):
                self.transport.write(traceback.format_exc())
            self.transport.loseConnection()
                
    def dataReceived(self,data):
        try:
            encData = json.loads(data)
            if 'debug' in encData:
                self.debug = encData['debug']
                self.transport.write("[+] Remote Debugging Enabled\n")
            if (self.debug):
                self.key = encData['key']

            op = encData['op']
            self.ops[op](encData) # just enc 4 now
        except:
            if (self.debug):
                self.transport.write(traceback.format_exc())
            self.transport.loseConnection()

    def connectionMade(self):
        self.key = open("./key","rb").read()
        self.iv = open("./iv","rb").read()
        self.ops = {}
        self.ops['enc'] = self.encrypt_data
        self.debug = False

class MyServerFactory(protocol.Factory):
    protocol = MyServer

factory = MyServerFactory()
reactor.listenTCP(PORT, factory)
reactor.run()
