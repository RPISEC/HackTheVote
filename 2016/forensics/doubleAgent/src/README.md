1. Generate SVGs of characters using gensvg.py from flag.txt
2. Add them to Inconsolata.otf with fontforge in alphabetical order starting at
   0x0400 and save as Inconsolata_embedded.otf
3. Use ttx to decompile Inconsolata_embedded.otf
4. Add ligatures from genlig.py to ttx, creating Inconsolata_chall.ttx
5. Recompile into challenge font (in handout directory)

Inspired by https://pixelambacht.nl/2015/sans-bullshit-sans/ (it has more
detailed instructions about a similar process)
