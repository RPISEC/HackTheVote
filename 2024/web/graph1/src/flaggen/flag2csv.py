#!/usr/bin/env python3
from pathlib import Path
from subprocess import PIPE, Popen, run

from PIL import Image, ImageDraw, ImageFont, PcfFontFile


FLAG1 = "flag{contrived_scenario}"
FLAG2 = "flag{extreme_csv_parsing}"
FONT = "ProggyTiny.pcf"
FONT_PIL = "ProggyTiny.pil"

# Step 1: create CSVs

if not Path(FONT_PIL).exists():
    with open(FONT, "rb") as fp:
        p = PcfFontFile.PcfFontFile(fp)
        p.save(FONT_PIL)
font = ImageFont.load(FONT_PIL)


def gen_csv(flag, num):
    image = Image.new("1", (1000, 10))
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), flag, 1, font=font)
    image = image.crop(image.getbbox())
    width, height = image.size
    with open(f'flag{num}.csv', 'w') as f:
        for i, v in enumerate(image.getdata()):
            if v:
                f.write(f'{i % width},{height - (i // width)}\n')


gen_csv(FLAG1, 1)
gen_csv(FLAG2, 2)


# Step 2: create PNGs

# This function needs to exactly match the server function, and it needs to be
# run in an environment with the exact same library versions
def gnuplot(in_filename, out_filename, points):
    plot = f"""
set terminal png size 2048,512
set output '{out_filename}'
set nokey
plot '{in_filename}' with {points}
"""
    p = Popen('gnuplot', text=True, stdin=PIPE, stderr=PIPE)
    output = p.communicate(input=plot)[1:]
    return p.returncode, output


def convert(filename):
    with open(filename) as f:
        contents = f.read()
    for line in contents.rstrip('\n').split('\n'):
        if ',' not in line or ' ' in line:
            return False
    with open(filename, 'w') as f:
        f.write(contents)
    out = run(
        ['mlr', '--icsvlite', '--opprint', '-N', 'cat', filename],
        capture_output=True,
    ).stdout
    with open(filename, 'wb') as f:
        f.write(out)
    return filename


gnuplot(convert("flag1.csv"), "flag1.png", "points")
gnuplot(convert("flag2.csv"), "flag2.png", "points")
