## Trump\_likes\_colors.png

In this challenge you're given 2 files with extension .png. Further investigation will reveal that these are actually .apng files which each hold 8192 frames of png data. Demuxing these frames takes some care as some popular apng disassemblers (apngdis) will not return the entire frame data. Intended solution uses the correct implementation in ffmpeg as:

`ffmpeg -i out%5d.png trump\_likes\_colors0.png`. 

Each frame of the dumped apng is a piet program which when run through a piet interpreter such as npiet will result in an hex rgb value in the form "#rrggbb".

If you pay attention to the number of frames you might see that they are equal to 128x128. If you treat each color value gotten from the piet frames as an rgb value for a pixel of a new image you can construct a new piet program (see included python script). This piet program is very similar in form to the previous images but is missing the outc instructions. To solve this challenge the player must debug this piet program using the previous images for reference and insert the missing outc commands (see included png).

Doing all this will provide you the flag: `flag{7h15_w45n7_3v3n_4_ch4ll3n63._54d_.}`

-Nihliphobe
