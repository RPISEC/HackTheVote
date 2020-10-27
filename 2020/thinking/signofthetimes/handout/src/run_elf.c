#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>

int main(int argc, char** argv) {
    if (argc < 3) {
        puts("run_elf <dir> <elf>");
        return -1;
    }

    char* dir = argv[1];
    char* bin = argv[2];

    chdir(dir);
    if (chroot(".") != 0) {
        puts("Could not chroot!");
        return -1;
    }

    if (setgid(65534) != 0){
        puts("Could not setgid!");
        return -1;
    }
    if (setuid(65534) != 0){
        puts("Could not setuid!");
        return -1;
    }

    execve(bin, NULL, NULL);
    puts("Failed to exec elf");
}
