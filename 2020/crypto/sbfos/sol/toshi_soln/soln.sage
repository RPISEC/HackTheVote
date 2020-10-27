import pickle
import struct
import binascii
from Crypto.Util.number import long_to_bytes as lb
from Crypto.Util.number import bytes_to_long as bl

F = GF(1<<128,name='a',modulus=x^128+x^7+x^2+x+1)
a = F.gen()
P = PolynomialRing(F,'x')
x = P.gen()

def convert_to_blocks(a,length=16):
    try:
        a = a.encode()
    except:
        pass
    if not a:
        return []
    if len(a)%length:
        res = [int.from_bytes(a[i*length:length+i*length],byteorder='big') for i in range(len(a)//length+1)]
    else:
        res = [int.from_bytes(a[i*length:length+i*length],byteorder='big') for i in range(len(a)//length)]
    return res

def int_to_poly(a,x):
    poly = 0
    bin_a = bin(a)[2:].zfill(128)
    for i in range(len(bin_a)):
        poly += int(bin_a[i])*x^i
    return poly

def poly_to_int(poly):
    return int(bin(poly.integer_representation())[2:].zfill(128)[::-1], 2)

    
def build_poly(addtion,cipher,x,a):
    int_a = convert_to_blocks(addtion)
    int_c = convert_to_blocks(cipher)
    A = [int_to_poly(i,a) for i in int_a]
    C = [int_to_poly(i,a) for i in int_c]
    m = len(A)
    n = len(C)
    # 64bits representation
    L = struct.pack(">QQ",len(addtion)*8,len(cipher)*8)
    L = int_to_poly(int.from_bytes(L,byteorder='big'),a)
    poly = 0
    for i in range(m+n+1,0,-1):
        if i>= n+2:
            poly += A[m+n+1-i]*x^i
        elif i>=2:
            poly += C[n+1-i]*x^i
        else:
            poly += L*x
    return poly

def bytes_to_str(a):
    res = ''
    for i in a:
        res += chr(i)
    return res


def bytes_to_polynomial(block, a):
    poly = _sage_const_0  
    bin_block = bin(bl(block))[_sage_const_2  :].zfill(_sage_const_128 )
    for i in range(len(bin_block)):
        poly += a**i * int(bin_block[i])
    return poly

P = b"/* 0 7103816 */++++++++>++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]/* 1 2912108 */<++++++++++++++++++++++++++++++++++++++++++++>++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]/* 2 7304992 */<++++++++++++++++++++++++++++++++>++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]/* 3 6581362 */<++++++++++++++++++++++++++++++++++++++++++++++++++>++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<++++++++++++++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]/* 4 2593 */<+++++++++++++++++++++++++++++++++>+++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<+++++++++++>+<[->[>++<-]>[<+>-]<<]>[<<+>>-]<,---------------------------------------->+++>,------------------------------------------------>+++>,-------------------------------------------------------->+++>,---------------------------------------------------------------->+++>,------------------------------------------------------------------------>+++>++++++++++++++++++++>+>,------------------------------------------------------------------------------------------------>+++++<<<."
C = bytes.fromhex(open("dump.txt", "r").read().replace(" ", ""))

C1 = C[0: 512]
T1 = bytes_to_polynomial( C[512:528], a )
C2 = C[0: 512] + C[528:1040]
T2 = bytes_to_polynomial( C[1040:1056], a )

C_ctxt = b""
for i in range(0, len(C), 512+16):
	C_ctxt += C[i:i+512]
P = P.ljust(len(C_ctxt), b"\x00")
C_ctxt = list(map(lambda x: x[0] ^^ x[1], zip(C_ctxt, P)))

def forge_T(B, H, S):
	addtion = b""
	B = build_poly(addtion, B, x, a)
	T = B(H)+S
	return poly_to_int(T)

def forge_all(B, H, S):
	B = B.ljust(len(C_ctxt), b"\x00")
	B = bytearray( map( lambda x: x[0] ^^ x[1], zip(B, C_ctxt) ) )
	X = b""
	for i in range(0, len(B), 512):
		X += B[i:i+512]
		T = forge_T(B[:i+512], H, S)
		T = binascii.unhexlify("{:032x}".format(T))
		assert len(T) == 16
		X += T
	return X

SHELL = open("prog.txt", "rb").read()
addtion = b""

potential_solutions = []
poly1 = build_poly(addtion,C1,x,a)
poly2 = build_poly(addtion,C2,x,a)
poly = poly1+poly2+T1+T2
for H, _ in poly.roots():
	S = poly1(H)+T1
	X = forge_all(SHELL, H, S)
	soln = ""
	for i in range(0, len(X), 64):
		soln += binascii.hexlify(X[i:i+64]).decode('ascii') + "\n"
	potential_solutions.append(soln)
with open("ctxts.pickle", "wb") as f:
	pickle.dump(potential_solutions, f)
