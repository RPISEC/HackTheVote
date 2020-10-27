#!/usr/bin/python
import os

with open("flag.txt") as f:
	for c in f.read().strip():
		os.system("hb-view --output-file={0}.svg --output-format=svg Inconsolata.otf {0}".format(c))
