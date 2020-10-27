#define _GNU_SOURCE
#include <dlfcn.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

extern long read(int, void*, unsigned long);
extern int close(int);
extern void _exit(int);

long __attribute__((naked)) sys_write(int fd, void* buf, unsigned long count) {
    asm volatile(
            "mov $1, %rax\n"
            "syscall\n"
            "ret\n"
            );
}

long write(int fd, void* buf, unsigned long count) {
    int mapsfd = open("/proc/self/maps", O_RDONLY);
    if (mapsfd == -1)
        _exit(1);
    char mapsbuf[0x2000];
    long nread = read(mapsfd, mapsbuf, sizeof(mapsbuf)-1);
    if (nread == -1)
        _exit(1);
    if (read(mapsfd, mapsbuf, 1) != 0)
        _exit(1);
    mapsbuf[nread] = 0;
    close(mapsfd);

#define NMAPS 64
    unsigned long maps[NMAPS][2];
    int nmaps = 0;
    for (char* str = strtok(mapsbuf, "\n"); str && nmaps < NMAPS; str = strtok(0, "\n"), nmaps++)
        if (sscanf(str, "%lx-%lx", &maps[nmaps][0], &maps[nmaps][1]) != 2)
            _exit(1);

    for (unsigned long i = 0; i < count; i++) {
        unsigned long x = 0;
        for (unsigned long len = 0; i+len < count && len < 8; len++) {
            ((unsigned char*)&x)[len] = *(unsigned char*)(buf+i+len);
            for (int j = 0; j < nmaps; j++)
                if (x >= maps[j][0] && x < maps[j][1]) {
                    memset(buf+i, 0, len+1);
                    break;
                }
        }
    }

    return sys_write(fd, buf, count);
}

void __attribute__((constructor)) init() {
    void* rwrite = dlsym(RTLD_NEXT, "write");
    mprotect((void*)((long)rwrite&~0xfff), 0x1000, PROT_READ|PROT_WRITE|PROT_EXEC);
    *(short*)rwrite = 0xb848;
    *(long*)(rwrite+2) = (long)write;
    *(short*)(rwrite+0xa) = 0xe0ff;
    mprotect((void*)((long)rwrite&~0xfff), 0x1000, PROT_READ|PROT_EXEC);
}
