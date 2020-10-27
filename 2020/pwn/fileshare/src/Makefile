all:
	gcc fileshare.c -o fileshare -Wall -Wextra -pie -fstack-protector -Wl,-z,relro,-z,now -lpthread -O1
	strip fileshare
	gcc wrapper.c -o wrapper -Wall -Wextra -pie -fstack-protector -Wl,-z,relro,-z,now
	strip wrapper
