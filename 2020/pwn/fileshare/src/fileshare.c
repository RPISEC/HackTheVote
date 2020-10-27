#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>
#include <sys/socket.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <netinet/in.h>
#include <errno.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <sys/eventfd.h>
#include <poll.h>
#include <sys/sendfile.h>
#include <sys/signal.h>
#include <linux/futex.h>
#include <grp.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <asm/prctl.h>
#include <sys/prctl.h>
int arch_prctl(int, unsigned long*);

void die(char* s) {
    perror(s);
    _exit(1);
}

#define STACK_SIZE 0x4000
#define MAX_CONNS 8
// must be multiple of 8
#define MAX_FSZ 0x400

#define FREE 0
#define DEAD 1
#define IDLE 2
#define DOWNLOAD 3
#define UPLOAD 4
#define DOWNLOAD_SEC 5
struct ipc {
    unsigned char state;
    int cfd;
    int efd_req;
    int efd_acc;
    int tid;
    void* stack;
    char* path;
    char* buf;
    unsigned long buflen;
    char* encbuf;
    char* privkey;
    unsigned long privkeylen;
};

void handler() {
    syscall(SYS_exit, 1);
}

void write_str(int cfd, char* s) {
    write(cfd, s, strlen(s));
}

void seccomp_init() {
    unsigned char filter[] = {32,0,0,0,4,0,0,0,21,0,0,7,62,0,0,192,32,0,0,0,0,0,0,0,21,0,6,0,0,0,0,0,21,0,5,0,1,0,0,0,21,0,4,0,60,0,0,0,21,0,0,2,9,0,0,0,32,0,0,0,16,0,0,0,21,0,1,0,0,0,0,0,6,0,0,0,0,0,0,0,6,0,0,0,0,0,255,127};
    struct sock_fprog rule = {sizeof(filter)>>3, (struct sock_filter*)filter};
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1 || prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &rule) == -1)
        die("seccomp");
}

void banner(int cfd) {
    write_str(cfd, "* * * * * * * * OOOOOOOOOOOOOOOOOOOOOOOOOOOOOO\n");
    write_str(cfd, " * * * * * * *  ::::::::::::::::::::::::::::::\n");
    write_str(cfd, "* * * * * * * * OOOOOOOOOOOOOOOOOOOOOOOOOOOOOO\n");
    write_str(cfd, " * * * * * * *  ::::::::::::::::::::::::::::::\n");
    write_str(cfd, "* * * * * * * * OOOOOOOOOOOOOOOOOOOOOOOOOOOOOO\n");
    write_str(cfd, " * * * * * * *  ::::::::::::::::::::::::::::::\n");
    write_str(cfd, "* * * * * * * * OOOOOOOOOOOOOOOOOOOOOOOOOOOOOO\n");
    write_str(cfd, "::::::::::::::::::::::::::::::::::::::::::::::\n");
    write_str(cfd, "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO\n");
    write_str(cfd, "::::::::::::::::::::::::::::::::::::::::::::::\n");
    write_str(cfd, "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO\n");
    write_str(cfd, "::::::::::::::::::::::::::::::::::::::::::::::\n");
    write_str(cfd, "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO\n");
    write_str(cfd, "                                              \n");
    write_str(cfd, "  You have logged into the nation's premier   \n");
    write_str(cfd, "          document sharing service.           \n");
    write_str(cfd, "          Please share responsibly.           \n");
    write_str(cfd, "                                              \n");
}

void menu(int cfd) {
    write_str(cfd, "[U]pload file\n");
    write_str(cfd, "[D]ownload file\n");
    write_str(cfd, "U[p]load secure file\n");
    write_str(cfd, "D[o]wnload secure file\n");
    write_str(cfd, "[Q]uit\n");
    write_str(cfd, ">>> ");
}

void read_line(int cfd, char* dst, unsigned long sz) {
    while (sz) {
        if (sz == 1) {
            *dst = 0;
            break;
        }
        if (read(cfd, dst, 1) != 1)
            syscall(SYS_exit, 1);
        if (*dst == '\n') {
            *dst = 0;
            break;
        }
        sz--;
        dst++;
    }
}

void read_ex(int cfd, char* dst, unsigned long sz) {
    while (sz) {
        long nread = read(cfd, dst, sz);
        if (nread <= 0)
            syscall(SYS_exit, 1);
        dst += nread;
        sz -= nread;
    }
}

void xor(char* s, unsigned long sz, char* key, unsigned long keysz) {
    for (unsigned long i = 0; i < sz; i++)
        s[i] ^= key[i % keysz];
}

void* client_func(void* arg) {
    struct ipc* ipc = (struct ipc*)arg;
    ipc->tid = syscall(SYS_gettid);
    signal(SIGSEGV, handler);
    signal(SIGPIPE, handler);
    seccomp_init();
    int cfd = ipc->cfd;
    banner(cfd);
    char op[8] = {0};
    char path[0x100];
    char buf[MAX_FSZ];
    long efd_val = 1;
    int nuploads = 0;
    unsigned long privkeylen = 0;
    char* privkey = 0;
    int secure;
    while (1) {
        menu(cfd);
        read_line(cfd, op, sizeof(op));
        secure = 0;
        switch (op[0]) {
            case 'P':
            case 'p':
                secure = 1;
                if (!privkeylen) {
                    while (!privkeylen) {
                        char lenstr[16] = {0};
                        write_str(cfd, "Enter the length of your private key: ");
                        read_line(cfd, lenstr, sizeof(lenstr));
                        privkeylen = strtoul(lenstr, 0, 10);
                    }
                    privkey = mmap(0, privkeylen, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
                    if (privkey == MAP_FAILED) {
                        write_str(cfd, "Sorry, private key too large\n");
                        ipc->state = DEAD;
                        syscall(SYS_exit, 1);
                    }
                    ipc->privkey = privkey;
                    ipc->privkeylen = privkeylen;
                    write_str(cfd, "Enter private key:\n");
                    read_ex(cfd, privkey, privkeylen);
                }
                // fall through
            case 'U':
            case 'u':
                memset(buf, 0, sizeof(buf));
                write_str(cfd, "Please input file contents to upload:\n");
                long nread = read(cfd, buf, sizeof(buf));
                if (nread <= 0)
                    syscall(SYS_exit, 1);
                if (secure)
                    xor(buf, nread, privkey, privkeylen);
                ipc->buf = buf;
                ipc->buflen = nread;
                snprintf(path, sizeof(path), "user%d-%d", ipc->tid, nuploads);
                if (secure)
                    strcat(path, ".enc");
                nuploads++;
                ipc->path = path;
                ipc->state = UPLOAD;
                write(ipc->efd_req, &efd_val, sizeof(efd_val));
                read(ipc->efd_acc, &efd_val, sizeof(efd_val));
                write_str(cfd, "File ");
                write_str(cfd, path);
                write_str(cfd, " uploaded.\n");
                ipc->state = IDLE;
                break;
            case 'D':
            case 'd':
                memset(path, 0, sizeof(path));
                write_str(cfd, "File to download: ");
                read_line(cfd, path, sizeof(path));
                ipc->path = path;
                ipc->state = DOWNLOAD;
                write_str(cfd, "======== FILE CONTENTS ========\n");
                write(ipc->efd_req, &efd_val, sizeof(efd_val));
                read(ipc->efd_acc, &efd_val, sizeof(efd_val));
                write_str(cfd, "\n============= EOF =============\n");
                ipc->state = IDLE;
                break;
            case 'O':
            case 'o':
                if (!privkeylen)
                    write_str(cfd, "No secure files uploaded yet.\n");
                else {
                    memset(path, 0, sizeof(path));
                    write_str(cfd, "Secure file to download: ");
                    read_line(cfd, path, sizeof(path));
                    if (strchr(path, '/'))
                        write_str(cfd, "No such file.\n");
                    else {
                        ipc->path = path;
                        ipc->state = DOWNLOAD_SEC;
                        write(ipc->efd_req, &efd_val, sizeof(efd_val));
                        read(ipc->efd_acc, &efd_val, sizeof(efd_val));
                        // couldnt get it to inline memcpy... and libc memcpy does weird backwards copy
                        //if (ipc->buflen)
                            asm volatile(
                                    "mov %0, %%rdi\n"
                                    "mov %1, %%rsi\n"
                                    "mov %2, %%rcx\n"
                                    "rep movsb\n"
                                    :
                                    : "r" (buf), "r" (ipc->encbuf), "r" (ipc->buflen)
                                    : "memory", "cc", "rdi", "rsi", "rcx"
                                    );
                        xor(buf, ipc->buflen, privkey, privkeylen);
                        write_str(cfd, "======== FILE CONTENTS ========\n");
                        write(cfd, buf, ipc->buflen);
                        write_str(cfd, "\n============= EOF =============\n");
                    }
                }
                ipc->state = IDLE;
                break;
            case 'Q':
            case 'q':
                write_str(cfd, "Thank you for using our system. Goodbye.\n");
                ipc->state = DEAD;
                syscall(SYS_exit, 0);
                break;
        }
    }
    return 0;
}

void spawn_client(struct ipc* ipc, int cfd) {
    ipc->state = IDLE;
    ipc->cfd = cfd;
    ipc->tid = 0;
    int efd_req = eventfd(0, 0);
    if (efd_req == -1)
        die("eventfd");
    ipc->efd_req = efd_req;
    int efd_acc = eventfd(0, 0);
    if (efd_acc == -1)
        die("eventfd");
    ipc->efd_acc = efd_acc;
    pthread_t thr;
    pthread_attr_t thr_attr;
    pthread_attr_init(&thr_attr);
    pthread_attr_setdetachstate(&thr_attr, PTHREAD_CREATE_DETACHED);
    void* stack = mmap(0, STACK_SIZE+0x2000, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    if (stack == MAP_FAILED)
        die("mmap");
    if (mprotect(stack, 0x1000, PROT_NONE) == -1 || mprotect(stack+STACK_SIZE+0x1000, 0x1000, PROT_NONE) == -1)
        die("mprotect");
    ipc->stack = stack;
    pthread_attr_setstack(&thr_attr, stack+0x1000, STACK_SIZE);
    if (pthread_create(&thr, &thr_attr, client_func, (void*)ipc))
        die("pthread_create");
    //XXX is there really no better way to not have pthreads cache the stack
    unsigned long tls = 0;
    if (arch_prctl(ARCH_GET_FS, &tls) == -1)
        die("arch_prctl");
    for (unsigned long l = thr; 1; l+=8)
        if (*(unsigned long*)l-tls == l-thr) {
            unsigned long** ll = (unsigned long**)l;
            ll[0][1] = (unsigned long)ll[1];
            ll[1][0] = (unsigned long)ll[0];
            break;
        }
}

void handle_download(struct ipc* ipc) {
    int fd = open(ipc->path, O_RDONLY);
    sendfile(ipc->cfd, fd, 0, MAX_FSZ);
    close(fd);
}

void handle_upload(struct ipc* ipc) {
    int fd = open(ipc->path, O_WRONLY|O_CREAT|O_TRUNC, 0600);
    write(fd, ipc->buf, ipc->buflen);
    close(fd);
}

void handle_download_sec(struct ipc* ipc) {
    if (!ipc->encbuf)
        ipc->encbuf = malloc(MAX_FSZ);
    int fd = open(ipc->path, O_RDONLY);
    if (fd == -1) {
        ipc->buflen = 0;
        return;
    }
    long nread = read(fd, ipc->encbuf, MAX_FSZ);
    ipc->buflen = nread;
    close(fd);
}

void handle_req(struct ipc* ipc) {
    long efd_val = 0;
    read(ipc->efd_req, &efd_val, sizeof(efd_val));
    switch (ipc->state) {
        case DOWNLOAD:
            handle_download(ipc);
            break;
        case UPLOAD:
            handle_upload(ipc);
            break;
        case DOWNLOAD_SEC:
            handle_download_sec(ipc);
            break;
        case DEAD:
        case FREE:
        case IDLE:
            break;
    }
    write(ipc->efd_acc, &efd_val, sizeof(efd_val));
}

int reap_dead(struct ipc* ipcs, struct pollfd* pollfd) {
    int ret = 0;
    //XXX could change this as a hint....
    for (int i = 0; i < MAX_CONNS; i++) {
        struct ipc* ipc = &ipcs[i];
        if (ipc->tid && kill(ipc->tid, 0) == -1 && errno == ESRCH) {
            if (ipc->state != DEAD)
                fprintf(stderr, "client %d terminated unexpectedly\n", ipc->tid);
            close(ipc->cfd);
            close(ipc->efd_req);
            close(ipc->efd_acc);
            munmap(ipc->stack, STACK_SIZE+0x2000);
            ipc->tid = 0;
            free(ipc->encbuf);
            ipc->encbuf = 0;
            if (ipc->privkey) {
                munmap(ipc->privkey, ipc->privkeylen);
                ipc->privkey = 0;
                ipc->privkeylen = 0;
            }
            ipc->state = FREE;
            pollfd[i].fd = -1;
            ret++;
        }
    }
    return ret;
}

int main(int argc, char** argv) {
    close(0);
    close(1);

#define UID 65534
    if (setgroups(0, 0) == -1 || setresgid(UID, UID, UID) == -1 || setresuid(UID, UID, UID) == -1)
        die("drop privs");

    int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
    if (sock == -1)
        die("socket");
    if (argc == 3 && !strcmp(argv[1], "-p")) {
        struct sockaddr_in addr = {0};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(atoi(argv[2]));
        int tmp = 1;
        setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &tmp, sizeof(tmp));
        if (bind(sock, (struct sockaddr*)&addr, sizeof(addr)) == -1)
            die("bind");
    }
    if (listen(sock, 3) == -1)
        die("listen");
    struct sockaddr_in sockaddr;
    socklen_t sockaddrlen = sizeof(sockaddr);
    if (getsockname(sock, (struct sockaddr*)&sockaddr, &sockaddrlen) == -1)
        die("getsockname");
    fprintf(stderr, "started server on port %d...\n", ntohs(sockaddr.sin_port));

    struct pollfd pollfd[MAX_CONNS+1] = {0};
    pollfd[MAX_CONNS].fd = sock;
    pollfd[MAX_CONNS].events = POLLIN;
    for (int i = 0; i < MAX_CONNS; i++) {
        pollfd[i].fd = -1;
        pollfd[i].events = POLLIN;
    }

    struct ipc* ipc = calloc(MAX_CONNS, sizeof(*ipc));
    int nidx = 0;
    int nalive = 0;
    int timeout = -1;

    while (1) {
        if (poll(pollfd, MAX_CONNS+1, timeout) == -1)
            die("poll");
        if (pollfd[MAX_CONNS].revents & POLLIN) {
            int cfd = accept(sock, 0, 0);
            if (cfd == -1)
                die("accept");
            spawn_client(&ipc[nidx], cfd);
            pollfd[nidx].fd = ipc[nidx].efd_req;
            for (nidx = 0; nidx < MAX_CONNS && ipc[nidx].state != FREE; nidx++);
            if (nidx == MAX_CONNS)
                pollfd[MAX_CONNS].fd = -1;
            nalive++;
            if (timeout == -1)
                timeout = 1000;
        }
        for (int i = 0; i < MAX_CONNS; i++)
            if (pollfd[i].revents & POLLIN)
                handle_req(&ipc[i]);
        int ndead = reap_dead(ipc, pollfd);
        if (ndead) {
            nalive -= ndead;
            if (!nalive)
                timeout = -1;
            if (nidx == MAX_CONNS) {
                for (nidx = 0; nidx < MAX_CONNS && ipc[nidx].state != FREE; nidx++);
                if (nidx != MAX_CONNS)
                    pollfd[MAX_CONNS].fd = sock;
            }
        }
    }

    return 0;
}
