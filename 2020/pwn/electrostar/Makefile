.DEFAULT_GOAL := all_modules

src/crypto/public.h: src/crypto/public.pem
	xxd -i src/crypto/public.pem src/crypto/public.h
src/crypto/private.h: src/crypto/private.pem
	xxd -i src/crypto/private.pem src/crypto/private.h

crypto_keys: src/crypto/public.h src/crypto/private.h

bin/signer: src/crypto/public.h src/crypto/private.h src/crypto/signer.c src/crypto/public.h src/crypto/private.h src/crypto/crypt.c include/colors.h
	gcc -o bin/signer src/crypto/signer.c -lcrypto -g -Iinclude

bin/machine: src/crypto/public.h src/crypto/private.h src/machine.c src/crypto/public.h src/crypto/private.h src/crypto/crypt.c include/sandbox.h include/colors.h bin/modules/ballot_module.img.sig bin/modules/init_module.img.sig bin/modules/gui_module.img.sig
	gcc -o bin/machine src/machine.c -lcrypto -ldl -lseccomp -lncurses -Iinclude \
		-DM1HASH="$(shell sha256sum src/ballot_module/ballot_module.img | cut -d " " -f1 | tr -d '\n' | xxd -p -r |xxd -i )" \
		-DM2HASH="$(shell sha256sum src/gui_module/gui_module.img | cut -d " " -f1 | tr -d '\n' | xxd -p -r | xxd -i)" \
		-DM3HASH="$(shell sha256sum src/init_module/init_module.img | cut -d " " -f1 | tr -d '\n' | xxd -p -r | xxd -i)"

bin/modules/ballot_module.img.sig: bin/signer src/ballot_module/ballot_module.c src/ballot_module/module_lib.h src/module_builder.py
	gcc -fpic -nostdlib -o src/ballot_module/ballot_module.o -Tdata 0x2000 src/ballot_module/ballot_module.c -masm=intel -Wno-builtin-declaration-mismatch
	python src/module_builder.py src/ballot_module/ballot_module.o src/ballot_module/ballot_module.img
	bin/signer src/ballot_module/ballot_module.img bin/modules/ballot_module.img.sig

bin/modules/init_module.img.sig: bin/signer src/init_module/init_module.c src/init_module/module_lib.h src/module_builder.py
	gcc -fpic -nostdlib -o src/init_module/init_module.o -Tdata 0x2000 src/init_module/init_module.c -masm=intel -Wno-builtin-declaration-mismatch
	python src/module_builder.py src/init_module/init_module.o src/init_module/init_module.img 1
	bin/signer src/init_module/init_module.img bin/modules/init_module.img.sig

bin/modules/gui_module.img.sig: bin/signer src/gui_module/gui_module.c src/gui_module/module_lib.h src/module_builder.py
	gcc -fpic -nostdlib -o src/gui_module/gui_module.o -Tdata 0x2000 src/gui_module/gui_module.c -masm=intel -Wno-builtin-declaration-mismatch
	python src/module_builder.py src/gui_module/gui_module.o src/gui_module/gui_module.img 2
	bin/signer src/gui_module/gui_module.img bin/modules/gui_module.img.sig

dist: bin/machine bin/modules/* src/flag3_handout.c
	mkdir -p dist
	gcc -o dist/flag3.exe src/flag3_handout.c
	python src/scrub_key.py ./bin/machine src/crypto/private.pem ./dist/machine
	chmod +x ./dist/machine
	rm -rf ./dist/modules
	cp -r ./bin/modules ./dist/modules

handout: dist
	rm -rf handout
	mkdir -p handout
	cp -L -r ./dist/* handout/.


bin/flag3.exe: src/flag3.c
	gcc -o bin/flag3.exe src/flag3.c

all_modules: handout bin/flag3.exe dist bin/machine bin/modules/ballot_module.img.sig bin/modules/init_module.img.sig bin/modules/gui_module.img.sig
