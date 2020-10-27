import sys
import html
import random
import subprocess
import fontTools.ttx as ttx
import xml.etree.ElementTree as ET
from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.platypus import *
from reportlab.pdfbase import *
from reportlab.pdfbase.ttfonts import *
from reportlab.lib.styles import *
from tempfile import NamedTemporaryFile as TmpFile

tree = None
names = []

def scramble(text, scheme):
    res = ''
    for c in text:
        if c == ' ':
            res += c
            continue
        for i, (code, name) in enumerate(scheme):
            if code == ord(c):
                res += chr(0x21 + i)
                break
        else:
            raise
    return res

def create_pdf(s, fontfile):
    with TmpFile() as pdf, TmpFile() as output, open(fontfile, 'rb') as scrambled_ttf:
        doc = SimpleDocTemplate(pdf.name, pageCompression=1)
        pdfmetrics.registerFont(TTFont('PDFScramble Mono', scrambled_ttf.name, validate=False))
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Scrambled', fontName=f'PDFScramble Mono', fontSize=10))
        p1 = Paragraph(s, styles['Scrambled'])
        doc.build([p1])
        overlay = PageMerge().add(PdfReader('grid.pdf').pages[0])[0]
        original = PdfReader(pdf.name)
        for page in original.pages:
            PageMerge(page).add(overlay).render()
        PdfWriter(output.name, trailer=original).write()
        return output.read()


# this is very much a hack, but I don't know how to unregister fonts in reportlab
# otherwise all pdfs after the first one were using the wrong font, so I spawn a new
# process every time I want a pdf, that way every pdf is the first one
def obfuscate(s):
    global tree, names
    if tree is None:
        tree = ET.parse('DejaVuSansMono_cmap.ttx')
        for c in tree.getroot().find('cmap/cmap_format_12').findall('map'):
            code = int(c.attrib['code'], 16)
            if 0x21 <= code <= 0x7e:
                names.append((code, c.attrib['name']))
    random.shuffle(names)
    for c in tree.getroot().find('cmap/cmap_format_12').findall('map'):
        code = int(c.attrib['code'], 16)
        if 0x21 <= code <= 0x7e:
            c.attrib['name'] = names[code-0x21][1]

    with TmpFile() as scrambled_ttx, TmpFile() as scrambled_ttf:
        tree.write(scrambled_ttx.name, xml_declaration=True)
        ttx.ttCompile(scrambled_ttx.name, scrambled_ttf.name, ttx.Options([('-m', 'DejaVuSansMono.ttf')], 1))
        text = html.escape(scramble(s, names))
        return subprocess.check_output(['python', 'obfuscate.py', text, scrambled_ttf.name])

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'Usage: python {sys.argv[0]} str names')
    else:
        x, y = sys.argv[1:]
        sys.stdout.buffer.write(create_pdf(x, y))
