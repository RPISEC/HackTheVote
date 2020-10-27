# From binary
flag_bytes = b'\xa2\x8e\x90\x1fG\xf0\xfc\x9f\x87&H\xaf\xa2\xd4,N\xaf\x91\rFt|Yw\xb1\x1fR#<\xe8\x1d\xcc`\xccgW'

def ror(a, b):
	def ror1(n):
		return ((n & 1) << 63) | (n >> 1)
	for i in range(b):
		a = ror1(a)
	return a

rors = []
a = 0x358d0150819cf3c4
for i in range(0, 0x24):
   rors.append(ror(a, i) & 0xff)

flag = ''.join(chr(flag_bytes[i] ^ rors[i]) for i in range(len(flag_bytes)))

assert(flag.startswith("flag"))
print(flag)