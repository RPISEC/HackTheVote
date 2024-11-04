#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>

int main() {
    int fd = open("/dev/mpy", O_RDWR);
    if (fd < 0) {
        return -1;
    }
    char buf[1024];
    for (;;) {
        puts("ABCD>");
        if (fgets(buf, sizeof(buf), stdin) < 0) {
            return -1;
        }
        if (ioctl(fd, 123, buf) < 0) {
            return -1;
        }
    }
    return 0;
}
