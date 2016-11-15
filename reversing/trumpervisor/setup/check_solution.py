"""
written by Aaron, 08/03/2016!
run this on a port, the challenge is to determine a register state via RE
that will produce the "correct_solution" dword

the math and the "correct_solution" should be reversed out of the driver, 
this script only checks the register states and that the math was RE'd correctly
fake_flag = "flag{..........................}"
encoded fake flag = "\xd6\xff\x72\xe7\xcb\xbd\x3d\xae\x9e\xbd\x3d\xae\x9e\xbd\x3d\xae\x9e\xbd\x3d\xae\x9e\xbd\x3d\xae\x9e\xbd\x3d\xae\x9e\xbd\x3d\xfd"

example solution registers
    RAX = 0x0
    RBX = 0xffffd000247f0000
    RCX = 0xffffd000247f00e0
    RDX = 0x400
    RSI = 0xffffd00022131740
    RDI = 0x1aa000
    R8  = 0xffffd000247f0000
    R9  = 0xffffd00022131750
    R10 = 0xffffd00022131760
    R11 = 0x1
    R12 = 0x0
    R13 = 0xfffff80339adeb64
    R14 = 0xfffff80339d37180
    R15 = 0x0
"""
import binascii
import struct
import ctypes
correct_solution = 0x801393b0
flag = "flag{HyP3rv1s04z_aRe_T3h_fuTuR3}"

def myrshift(foo, bar):
	if (bar > 63):
		return 0
	else:
		return foo >> bar
def mylshift(foo, bar):
	if (bar > 63):
		return 0
	else:
		return foo << bar
#first chunk of math
def math_1(foo):
	foo = RCX - R8
	foo = foo - (foo & R11)
	return foo
#second chunk of math
def math_2(foo):
	foo = foo - myrshift(foo,R13)
	foo = foo + R12
	foo = mylshift(foo,3)
	return foo
#third chunk of math
def math_3(foo) :
	bar = struct.pack("<Q",foo)
	for i in xrange(0,8) :
		baz = ord(bar[i]) | ord(bar[i % 3])
		foo |= mylshift(baz,(i * 8))
	return foo
#4th chunk of math
def math_4(foo):
	foo = foo + (RDI - (RBX+RDX))
	foo = foo - RSI
	return foo
#5th chunk of math
def math_5(foo):
	for i in xrange(0,RDX):
		foo = myrshift(foo,R15)
		foo = foo - R10
 	return foo
#6th chunk of math
def math_6(foo): 
	foo = mylshift(foo,R15)
	foo = foo + R9
	foo = foo - R8
	return foo
#7th chunk of math
def math_7(foo): 
	foo += R14
	foo = foo - RCX
	return foo

def eval_regs():

	foo = 0;
	#perform all of the math found in the driver
	foo = ctypes.c_uint64(math_1(foo)).value
	foo = ctypes.c_uint64(math_2(foo)).value
	foo = ctypes.c_uint64(math_3(foo)).value	
	foo = ctypes.c_uint64(math_4(foo)).value
	foo = ctypes.c_uint64(math_5(foo)).value
	foo = ctypes.c_uint64(math_6(foo)).value
	foo = ctypes.c_uint64(math_7(foo)).value
	return ctypes.c_uint64(foo & 0x00000000ffffffff).value

#xor the flag with the 4 byte result from eval_regs
def encode_flag(flag, solution):

	foo = struct.pack("<I",solution)
	result = ""

	for i in xrange(0,32):
		result += chr(ord(flag[i]) ^ ord(foo[i % 4]))

	return result

print "please enter values as unsigned decimal"
RAX = int(raw_input("rax = "))
RBX = int(raw_input("rbx = "))
RCX = int(raw_input("rcx = "))
RDX = int(raw_input("rdx = "))
RSI = int(raw_input("rsi = "))
RDI = int(raw_input("rdi = "))
R8  = int(raw_input("r8 = "))
R9  = int(raw_input("r9 = "))
R10 = int(raw_input("r10 = "))
R11 = int(raw_input("r11 = "))
R12 = int(raw_input("r12 = "))
R13 = int(raw_input("r13 = "))
R14 = int(raw_input("r14 = "))
R15 = int(raw_input("r15 = "))

solution = eval_regs()
#print binascii.hexlify(encode_flag(fake_flag,solution))
print hex(solution)
if (solution == correct_solution) :
	print flag
