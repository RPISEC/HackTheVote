import ast
import fontTools.ttx as ttx
import xml.etree.ElementTree as ET
from Crypto.Util.number import long_to_bytes
from pdfminer.high_level import *
from pdfreader import PDFDocument
from tempfile import NamedTemporaryFile as TmpFile

def lagrange(shares, prime):
    secret = 0
    for i, s in shares:
        prod = 1
        for j, _ in shares:
            if i != j:
                prod *= j * pow(j - i, -1, prime)
        secret += s * prod
    return secret % prime

glyph_names = ["space", "exclam", "quotedbl", "numbersign", "dollar", "percent", "ampersand", "quotesingle", "parenleft", "parenright", "asterisk", "plus", "comma", "hyphen", "period", "slash", "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "colon", "semicolon", "less", "equal", "greater", "question", "at", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "bracketleft", "backslash", "bracketright", "asciicircum", "underscore", "grave", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "braceleft", "bar", "braceright", "asciitilde"]

with open('message', 'rb') as f, TmpFile() as dejavu_ttx:
    ttx.ttDump('DejaVuSansMono.ttf', dejavu_ttx.name, ttx.Options('', 0))
    dejavu = ET.parse(dejavu_ttx.name)

    # Map glyph shapes to their names
    glyphs = {}
    for glyph in dejavu.getroot().findall('glyf/TTGlyph'):
        if glyph.attrib['name'] in glyph_names:
            name = glyph.attrib['name']
            glyph.attrib['name'] = ''
            glyphs[ET.tostring(glyph).strip()] = name

    shares = []
    data = b''
    glyphOrder = []
    i = 0
    prime = None
    for line in f:
        data += line
        if line == b'%%EOF\n':
            with TmpFile() as pdf, TmpFile() as fontfile, TmpFile() as ttxfile:
                pdf.write(data)

                # Convert font to xml and extract character map
                font = next(PDFDocument(pdf).pages()).Resources.Font['F2+0'].FontDescriptor.FontFile2.filtered
                fontfile.write(font)
                ttx.ttDump(fontfile.name, ttxfile.name, ttx.Options('', 0))
                scrambled = ET.parse(ttxfile.name).getroot()
                cmap = scrambled.find('.//cmap/cmap_format_6')

                # Match glyphs to their names based on their shape
                for c in cmap.findall('map'):
                    code = int(c.attrib['code'], 16)
                    if 0x20 <= code <= 0x7e:
                        name = c.attrib['name']
                        scrambled_glyph = scrambled.find(f'.//glyf/TTGlyph[@name="{name}"]')
                        scrambled_glyph.attrib['name'] = ''
                        glyphOrder.append(glyphs[ET.tostring(scrambled_glyph).strip()])

                # Unscramble text based on glyph order
                text = ''
                scrambled_text = ''.join(extract_text(pdf).splitlines()).strip()
                for c in scrambled_text:
                    text += chr(glyph_names.index(glyphOrder[ord(c)- 0x20]) + 0x20)
                if i == 0:
                    prime = int(text.split()[-1])
                else:
                    x, y = [int(s.split()[-1]) for s in text.split(', ')]
                    shares.append((x, y))

            data = b''
            glyphOrder = []
            i += 1

    flag = lagrange(shares, prime)
    print(long_to_bytes(flag))
