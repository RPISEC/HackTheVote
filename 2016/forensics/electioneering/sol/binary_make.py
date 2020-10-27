from PIL import Image
import binascii

def gen_bin():    
    flag = "IrateAnagramCakeImage "
    bin_flag = "0"
    bin_flag += bin(int(binascii.hexlify(flag), 16))[2:]
    #print bin_flag
    
    return bin_flag

def LSB(binary):
    cover = Image.open("poster.png").convert("RGB")
   
    count = 0
    
    for y in range(4):
        for x in range(42):
            r, g, b = cover.getpixel( (x,y) )

            if count%3 == 1:
                if flag[count] == "1":
                    cover.putpixel((x, y), ((r & 0xfe) | 1, g, b))
                if flag[count] == "0":
                    cover.putpixel((x,y), ((r & 0xfe), g, b))                
                    
            if count%3 == 2:
                if flag[count] == "1":
                    cover.putpixel((x, y), (r, (g & 0xfe) | 1, b))
                if flag[count] == "0":
                    cover.putpixel((x,y), (r, (g & 0xfe), b))  
                    
            if count%3 == 0:
                if flag[count] == "1":
                    cover.putpixel((x, y), (r, g, (b & 0xfe) | 1))
                if flag[count] == "0":
                    cover.putpixel((x,y), (r, g, (b & 0xfe)))                
            count+=1
    cover.save("lsb_poster.png", "PNG")
    
if __name__ == "__main__":
    flag = gen_bin()
    LSB(flag)