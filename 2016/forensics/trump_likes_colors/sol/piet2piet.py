import cv2
import re
import os
import subprocess as sp
import numpy as np

def create_blank(width, height, rgb_color=(0, 0, 0)):
    """Create new image(numpy array) filled with certain color in RGB"""
    # Create black blank image
    image = np.zeros((height, width, 3), np.uint8)

    # Since OpenCV uses BGR, convert the color first
    color = tuple(reversed(rgb_color))
    # Fill image with color
    image[:] = color

    return image

print(cv2.__version__)

column_size =  128
row_size = 128
out_piet = create_blank(column_size,row_size,rgb_color=(0,0,0))
out_file_name = "generated_image.ppm"

count = 0
x = 0
y = 0
os.system("ffmpeg -i ../handout/trump_likes_colors.png 'out_frames/outout%5d.png'")
for filename in sorted(os.listdir('out_frames/'),key=lambda x: (int(re.sub('\D', '', x)), x)):
  process = sp.Popen(["npiet", 'out_frames/'+filename], stdout=sp.PIPE)
  out, err = process.communicate()
  r = int(out[1:3], 16)
  g = int(out[3:5], 16)
  b = int(out[5:7], 16)
  #print filename, ", ", (r, ", ", g, ", ", b)
  #I have no idea why these are switched :/
  out_piet[y,x] = [b, g, r]
  #print out_piet[y,x]
  x += 1
  if x == (128):
      x = 0
      y += 1
      print y
cv2.imwrite(out_file_name, out_piet)
print "Done generating image"
os.system("npiet solved_piet.pnm")
