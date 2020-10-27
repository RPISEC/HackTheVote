First, there is a password protected zip file hidden in the image. Extract it
Next, check the LSB (least significant bits) of the Red, Green, Blue channels of the image. In the upper left of
each channel there's a pattern of dots.
Then, combine each channel's dot pattern (extracted.png). Those represent binary bits where white corresponds
to 1 and black corresponds to 0. Convert the image into binary.
Finally, converty the binary into ascii. The resulting string is the password for the zip.
flag{4nd_th3_w1nn3r_15….}

