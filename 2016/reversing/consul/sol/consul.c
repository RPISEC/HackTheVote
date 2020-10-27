#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

// this is going to become the cipherkey
static int mem = 0;

// some messages
static unsigned char b[] = { 0x26, 0x2C, 0x21, 0x27, 0x3B, 0x37, 0x32, 0x29, 0x34, 0x25, 0x1F, 0x29, 0x2E, 0x1F, 0x22, 0x25, 0x32, 0x2E, 0x29, 0x25, 0xE1, 0x3D};
static unsigned char b0[] = { 0x3F, 0x58, 0x62, 0x61, 0x54, 0x65, 0x57, 0x62, 0x13, 0x37, 0x58, 0x13, 0x43, 0x5C, 0x66, 0x54, 0x32, 0x13, 0x4A, 0x5B, 0x62, 0x1A, 0x66, 0x13, 0x67, 0x5B, 0x54, 0x67, 0xD5, 0x73, 0x86, 0x47, 0x5B, 0x58, 0x13, 0x61, 0x58, 0x6B, 0x67, 0x13, 0x63, 0x65, 0x58, 0x66, 0x5C, 0x57, 0x58, 0x61, 0x67, 0x32, }; // leonardo de pisa?

static unsigned char b1[] = { 0x4B, 0x59, 0x14, 0x58, 0x5D, 0x58, 0x62, 0x1B, 0x68, 0x14, 0x58, 0x59, 0x67, 0x59, 0x66, 0x6A, 0x59, 0x14, 0x36, 0x59, 0x66, 0x62, 0x5D, 0x59, 0x22, 0xCB, 0xB0, 0xA2 };

// flag{write_in_bernie!}

// more messages, can probably just brute force all of these until you see "flag{"
static unsigned char b2[] = { 0x67, 0x68, 0x2D, 0x00, 0x00, 0x13, 0x14, 0x59, 0x03, 0x23, 0x07, 0x01, 0x13, 0x59 };
static unsigned char b3[] = { 0x42, 0x56, 0x53, 0x0E, 0x53, 0x5C, 0x52, 0x0E, 0x57, 0x61, 0x0E, 0x54, 0x5D, 0x60, 0x53, 0x64, 0x53, 0x60, 0x1C, 0x0E, 0x30, 0x63, 0x62, 0x0E, 0x4F, 0x54, 0x62, 0x53, 0x60, 0x0E, 0x62, 0x56, 0x4F, 0x62, 0x1A, 0x0E, 0x67, 0x5D, 0x63, 0x15, 0x60, 0x53, 0x0E, 0x55, 0x5D, 0x5D, 0x52, 0x0E, 0x62, 0x5D, 0x0E, 0x55, 0x5D, 0x1C };
// some random data, jus tto make the calculations in c1,c1_,c2,c3,c5,c8 look meaningful.
// i mean, it does use them to calculate the cipher, but i mean, itd be faster to just bruteforce–probably


// func ptr, hopefully points to malloc
static void *(*m0)(size_t) = NULL;\

// 4 of the same function
char *sub_43E8(char password[], int key) { // decrypt function, just a basic cipher
	char *buf = malloc(strlen(password));
	
	for (unsigned int i = 0; i < strlen(password); i++) {
		buf[i] = password[i] + key;
	}
	
	return buf;
}

char *sub_41F2(char *password, int key) {
	char *buf = m0(strlen(password));
	
	for (unsigned int i = 0; i < strlen(password); i++) {
		buf[i] = password[i] + key;
	}
	
	return buf;
}

char *sub_9F36(char *password) {
	char *buf = m0(strlen(password));
	
	for (unsigned int i = 0; i < strlen(password); i++) {
		buf[i] = password[i] + mem;
	}
	
	return buf;
}

char *sub_198A(char *password, int key) {
	char *buf = m0(strlen(password));
	
	for (unsigned int i = 0; i < strlen(password); i++) {
		buf[i] = password[i] + key;
	}
	
	return buf;
}

// computations, dont go near this. 4 is not a fibonacci number
void c4() {
	int a = 3;
	int b = 3 * a;
	a = b ^ a;
	a = '4' * b;
	for (int i = 0; i < 15; i++) {
		a = 4 * b + a;
	}
	
	a -= 100;
	a ^= 10;
}

// 1 is fibonacci, may want to call this
void c1() {
	mem += b2[11];
}

// 1 is also the second fibonacci number probably should call this too
void c1_() {
	b0[13] += 1;
	mem += b2[1];
	for (int i =0; i < 15; i++) {
		mem -= b2[4];
	}
}

// 2 is also a fibonacci number,
void c2() {
	c4();
	b0[13] += 10;
	b0[13] = b0[13] ^ b[0];
	
}

// 3 too
void c3() {
	b1[13] = b2[13] * 13;
	mem += b1[13] / b2[0];
	mem -= 8 * b1[13] / b2[2];
	mem += b2[3];
}

// 5 definitely
void c5() {
	mem -= b[10];
	mem -= b2[4];
	mem += b2[8];
}

// 8 for sure, but wait this calls to sub_49F36, which should crash, since m0 is null
void c8() {
	mem += 9;
	// solve
	printf("%s\r\n", sub_9F36(b));
}

// 55 is too, but its like, way off, maybe hints that this one behaves a bit differently
// with further analysis, you see that its an infinite loop, but also it sets m0.
// interesting, so it crashes when loading m0 and trying to jump to it in sub_9F36
// so maybe we should set up m0..
void c55() {
	int i = 0;
	while (i < 15) {
		c4();
		usleep(100);
	}
	
	m0 = malloc;
}

// call if you want, just distraction
void dont_call_me() {
	c2();
	printf("%s\r\n", sub_41F2(b2, 1));
	c2();
}

// distractions
void fake_help() {
	printf("%s\r\n", sub_198A(b3, 18));
}

// distractions
void real_help() {
	char *dec = sub_43E8(b0, 13);
	printf("%s\r\n",dec);
	c2();
}

// distractions
void help() {
	printf("%s\r\n", sub_41F2(b1, 12));
}

// distractions
int main(int argc, char **argv) {
	printf("Poor Bernie.\r\n");
	return 0;
}
