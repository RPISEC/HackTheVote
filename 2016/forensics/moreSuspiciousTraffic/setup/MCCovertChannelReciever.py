__author__ = 'LtDan'
import random
from socket import *
import time
import base64

# Morse Code mapping
# Could not match flag{} format as { and } could not be found, used () instead
CODE = {'A': '.-',     'B': '-...',   'C': '-.-.',
        'D': '-..',    'E': '.',      'F': '..-.',
        'G': '--.',    'H': '....',   'I': '..',
        'J': '.---',   'K': '-.-',    'L': '.-..',
        'M': '--',     'N': '-.',     'O': '---',
        'P': '.--.',   'Q': '--.-',   'R': '.-.',
        'S': '...',    'T': '-',      'U': '..-',
        'V': '...-',   'W': '.--',    'X': '-..-',
        'Y': '-.--',   'Z': '--..',   ':': '---...',
        '(': '-.--.',  ')': '-.--.-', '0': '-----',
        '1': '.----',  '2': '..---',  '3': '...--',
        '4': '....-',  '5': '.....',  '6': '-....',
        '7': '--...',  '8': '---..',  '9': '----.'
       }
# Decode message
inverseCODE = dict((v,k) for (k,v) in CODE.items())
# Open socket
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', 23284)) # Wikipedia says port 23284 is registered to TimeTracker. Funny easter egg telling you to look at the time.
start = time.time() # Record start time
# Lame variables
tp = 0
x = 1
y = 1
a = 0
b = 0
decode = ""
char = ''
while True:
    #rand = random.randint(0, 10)
    #message, address = serverSocket.recvfrom(1024)
    t = time.time() - start
    #message = message.upper()
    #print message
    #print t

    #
    if (t-tp)<0.1:
        x += 1
        tp = t
    elif (t - tp)<0.6:
        if x == 6: # Long/Dash
            char += '-'
            #print "long"
        elif x == 3: # Short/Dot
            char += '.'
            #print "short"
        x = 1
        tp = t

    elif (t-tp)<3.5:
        print "Recieving Message..."
        if x == 6: # Long/Dash
            char += '-'
            #print "long"
        elif x == 3: # Short/Dot
            char += '.'
            #print "short"
        x = 1
        tp = t

        if char != '':
            # Added decoded character to decoded message
            decode = decode + inverseCODE[char]
        char = ''

    else:
        print "Decoded message: " + decode + '\n'
        x = 1
        tp = t
        print "----------"
        char = ''
        decode = ""

    #  Recieve message (Message doesn't matter, just when it was recieved)
    message, address = serverSocket.recvfrom(1024)
    # Send ACK
    ack = base64.b64encode(bytes("ACK"))
    serverSocket.sendto(ack, address)


#    if rand >= 4:
#    serverSocket.sendto(message, address)

