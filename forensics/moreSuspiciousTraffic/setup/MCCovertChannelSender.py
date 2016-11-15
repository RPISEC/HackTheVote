__author__ = 'LtDan'

import time
from socket import *
import sys
import base64
import random

# Enter IP Address and Port as arguments
ipAddress = str(sys.argv[1])
port = int(str(sys.argv[2]))

print "IP Address: %s"%(ipAddress)
print "Port: %d" %(port)
print " "

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

# Function to encode message in Morse
def morseEncoder(msg):
    result = []
    i = 0
    for char in msg:
        result.append(CODE[char.upper()])
        i += 1
    return result
# Function to send encoded message
def encodeSend(msg, clientSocket, addr):
    for char in msg:
        for i in char:
            if i == '.': # Short/Dot
                sendShort(clientSocket, addr)
                print "short"
            elif i == '-': # Long/Dash
                sendLong(clientSocket, addr)
                print "long"
            else:
                print "error"
            time.sleep(0.5) # Wait 0.5 seconds between dot/dash
        time.sleep(1) # Wait 1 second between characters
        print "\n"
# Function to send short/dot
def sendShort(clientSocket, addr):
    message = base64.b64encode(bytes(sendMe())) # B64 encode message (because why not?)
    x = 0
    while x < 3: # Send 3 times
        clientSocket.sendto(message, addr)
        x += 1
# Function to send long/dash
def sendLong(clientSocket, addr):
    message = base64.b64encode(bytes(sendMe())) # B64 encode message
    x = 0
    while x < 6: # Send 6 times
        clientSocket.sendto(message, addr)
        x += 1

def sendMe():
    # Previous version sent one of 4 different messages to increase difficulty
    rand = random.randint(0,3)
    if rand == 0:
        return "nottheflag"
    elif rand == 1:
        return "nottheflag"
    elif rand == 2:
        return "nottheflag"
    else:
        return "nottheflag"

def main():  # Main
    # Connect to socket
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(1) #wait up to one second to receive reply
    message = 'FLAG(H4CK7H3PL4N37)'    #message sent
    eof = 'EOF' # End
    addr = (ipAddress, port)

    encoded = morseEncoder(message) # Encode message
    print encoded

    start = time.clock() # get start time, use time.clock for precision
    encodeSend(encoded, clientSocket, addr) # Send encoded message

    # Debug stuff
    clientSocket.sendto(eof, addr)  #send End char
    time.sleep(4)
    clientSocket.sendto(eof, addr)  #send End char
    try:
        data, server = clientSocket.recvfrom(1024)  #get reply
        end = time.clock()   #get end time
        elapsed = (end - start) *1000    #get time elapsed in milliseconds
        print 'Message to <%s> : Time elapsed = <%f>' % (ipAddress, elapsed)
    except timeout: #get timeout and print
        print 'Message to <%s> LOST' % (ipAddress)


    sys.exit()

if __name__ == "__main__":
    main()
