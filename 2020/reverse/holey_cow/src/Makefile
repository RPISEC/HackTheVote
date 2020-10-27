all: src/chal.c src/alphabet.h
	gcc src/chal.c -o server/chal
	strip -s server/chal
debug: src/chal.c src/alphabet.h
	gcc -g src/chal.c -o server/chal
test: sol/solve.py
	cd sol && python solve.py | ../handout/chal
