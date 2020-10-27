.DEFAULT_GOAL := all

current_dir = $(shell pwd)

src/run_elf: src/run_elf.c
	gcc -o src/run_elf src/run_elf.c

diff.patch: src/* ../signofthetimes/src/*
	truncate diff.patch --size 0
	/bin/echo -e '\e[1m--- a/src/signer.py' >> ./diff.patch
	/bin/echo -e '+++ b/src/signer.py\e[m' >> ./diff.patch
	(cd /tmp && git diff --no-index --color=always $(current_dir)/../signofthetimes/src/signer.py $(current_dir)/src/signer.py | tail -n +5 >> $(current_dir)/diff.patch)
	/bin/echo -e '\e[1m--- a/src/protect.py' >> ./diff.patch
	/bin/echo -e '+++ b/src/protect.py\e[m' >> ./diff.patch
	(cd /tmp && git diff --no-index --color=always $(current_dir)/../signofthetimes/src/protect.py $(current_dir)/src/protect.py | tail -n +5 >> $(current_dir)/diff.patch)

all: server/src/run_elf server/diff.patch
