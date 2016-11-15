#!/usr/bin/env python2
import sys
import os
from binascii import *

# made easier, can now do it with two bytes and 14 00's, assuming some
# creativity in REing the design
# ... lol this is short

while True:

	daily_iv = int(raw_input("IV? "),2)

	print "00%02x%02x" % (0xF & (daily_iv^8), (daily_iv>>4)^10) + "00"*13 
