
import binascii
from PIL import Image

if __name__ == "__main__":

    binary = Image.open('extracted.png').convert("RGB")
    
    w, h = binary.size
       
    temp = "0b"

    for i in range(h):
        for j in range(w):
            pix, p, r = binary.getpixel( (j, i) )
            if pix == 0: #NOTE! Stegsolve flips the bits for some reason :p
                temp += '0'
            else:
                temp += '1'
    print temp
    
    temp = int(temp, 2)
   
    print binascii.unhexlify('%x' % temp)