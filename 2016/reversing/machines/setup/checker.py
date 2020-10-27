#!/usr/bin/env python2
import sys
import os
import time
import binascii

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

print "your inputs should be keypad presses, in the range of 00..0F each (no spaces) :)\n"

sys.stdout.write("...ready")
for i in xrange(0,5):
	sys.stdout.write(".")
	time.sleep(1)

print "?\n"

#flag = open("./flag",'r',).read()
flag = "flag{bu7_7h3y_sa1d_1t_w4s_pr0v4bly_s3cur3}"

for i in xrange(0,5):
	daily_iv = ord(open("/dev/urandom",'r').read(1)) 

	print "Machine %d has the switches set to: %s" % (i+1,bin(daily_iv)[2:])

	inp_bytes = raw_input("Can you tell us the code pls? Here: ")

	if(len(inp_bytes) < 2):
		print "nah."
		sys.exit()
	elif(len(inp_bytes) < 32):
		print "It just beeped a little at me, wtf?"
		sys.exit()

	try:
		inp = binascii.unhexlify(inp_bytes)
	except:
		print "don't make binascii sad pls. something's wrong with your input."
		sys.exit()

	final = daily_iv

	for i in range(0, 16):
		if ord(inp[i]) > 0xF:
			print "there is no %s key" % hex(ord(inp[i]))[2:]
			sys.exit()
		if i&1 or i == 0:
			final = (final & 0xF0) | ((final & 0x0F) ^ ord(inp[i]))
		else:
			final = (final & 0x0F) | (final  ^ ord(inp[i]) << 4)
		final &= 0xFF
	if final != 0xA8:
		print "...That can't be right. Good thing this is just a test run, right?"
		sys.exit()


print "oh cool - there's this neat flag I got you: " + flag
