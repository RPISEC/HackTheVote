all:
	gcc main.c -o primaries -Wall -Wextra -pie -fstack-protector-all -Wl,-z,relro,-z,now
	strip primaries

debug:
	gcc main.c -o primaries -Wall -Wextra -pie -fstack-protector-all -Wl,-z,relro,-z,now -g
