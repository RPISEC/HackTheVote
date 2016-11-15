#!/usr/bin/python

svg = {
	'a': '00',
	'e': '01',
	'f': '02',
	'g': '03',
	'h': '04',
	'i': '05',
	'l': '06',
	'n': '07',
	'r': '08',
	's': '09',
	't': '0A',
	'u': '0B',
	'{': '0C',
	'}': '0D',
}

with open("flag.txt") as f:
	for i, c in enumerate(f.read().strip()):
		print('<LigatureSet glyph="{0}">\n'
				'  <Ligature components="{0},{0},{0}" glyph="{1}"/>\n'
				'</LigatureSet>'.format(chr(65 + i), 'uni04' + svg[c]))
