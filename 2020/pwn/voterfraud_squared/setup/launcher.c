// Taken from https://github.com/pwning/docs/blob/master/fork_accept.c

// A sample forking/listening CTF binary (shamelessly reverse engineered
// from an old Ghost in the Shellcode challenge). You don't have to use
// this exact code, but make sure that your forking/listening servers
// are not susceptible to the problems mentioned in the comments.
#define _GNU_SOURCE
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <signal.h>
#include <unistd.h>
#include <errno.h>
#include <pwd.h>
#include <fcntl.h>

#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <grp.h>

#include <sys/ioctl.h>

const uint16_t port = 44061;

// Remember to check return values carefully in this function.
// Don't want to accidentally give people root :-)
int drop_privs(char *username) {
    struct passwd *pw = getpwnam(username);
    if (pw == NULL) {
        fprintf(stderr, "User %s not found\n", username);
        return 1;
    }

    if (chdir(pw->pw_dir) != 0) {
        perror("chdir");
        return 1;
    }

    // Don't forget to drop supplemental groups. Forgetting this
    // has led to people escalating to root in some past CTFs :-)
    if (setgroups(0, NULL) != 0) {
        perror("setgroups");
        return 1;
    }

    if (setgid(pw->pw_gid) != 0) {
        perror("setgid");
        return 1;
    }

    if (setuid(pw->pw_uid) != 0) {
        perror("setuid");
        return 1;
    }

    return 0;
}

// It is recommended to have wrappers like this around send and recv.
// Remember that send/recv can return without reading all n requested
// bytes.
ssize_t recvlen(int fd, char *buf, size_t n) {
    ssize_t rc;
    size_t nread = 0;
    while (nread < n) {
        rc = recv(fd, buf + nread, n - nread, 0);
        if (rc == -1) {
            if (errno == EAGAIN || errno == EINTR) {
                continue;
            }
            return -1;
        }
        if (rc == 0) {
            break;
        }
        nread += rc;
    }
    return nread;
}

ssize_t sendlen(int fd, const char *buf, size_t n) {
    ssize_t rc;
    size_t nsent = 0;
    while (nsent < n) {
        rc = send(fd, buf + nsent, n - nsent, 0);
        if (rc == -1) {
            if (errno == EAGAIN || errno == EINTR) {
                continue;
            }
            return -1;
        }
        nsent += rc;
    }
    return nsent;
}

ssize_t sendstr(int fd, const char *str) {
    return sendlen(fd, str, strlen(str));
}

// The connection handling function.
// Put your vulnerable code here :-)
// return value is the exit code
int handle(int fd, char* binary, char* flag) {
    int pipe_fds[2];

    if (pipe(&pipe_fds[0]) == -1) {
        return -1;
    }

    pid_t pid = fork();
    if (pid == 0) {
        // Close the write end
        (void) close(pipe_fds[1]);

        if (dup2(pipe_fds[0], STDIN_FILENO) == -1) {
            abort();
        }
        if (dup2(fd, STDOUT_FILENO) == -1) {
            abort();
        }
        (void) close(STDERR_FILENO);

        char *argv[] = {
            binary,
            NULL
        };
        char *envp[] = {
            NULL
        };
        execve(binary, argv, envp);
        abort();
    } else if (pid == -1) {
        // fork failed
        return pid;
    }

    // Close the read end
    (void) close(pipe_fds[0]);

    {
        size_t length = strlen(flag);
        // Write the flag into the process
        if (write(pipe_fds[1], flag, length) == -1) {
            return -1;
        }
        if (write(pipe_fds[1], "\n", 1) == -1) {
            return -1;
        }
        // wait until the child reads the bytes
        // splice locks up the buffer, which prevents the child from reading the flag
        // until the user inputs something
        while (1) {
            int nleft = length;
            ioctl(pipe_fds[1], FIONREAD, &nleft);
            if (!nleft)
                break;
            usleep(1000);
        }
    }

    // Now ensure child stdin is the socket
    if (splice(fd, NULL, pipe_fds[1], NULL, UINT_MAX, SPLICE_F_MOVE) == -1) {
        return -1;
    }

/*
    if (wait(NULL) == -1) {
        return -1;
    }
*/

    (void) close(pipe_fds[1]);

    return 0;
}

int main(int argc, char **argv) {
    int rc;
    int opt;
    int sockfd;
    int clientfd;
    pid_t pid;
    struct sockaddr_in saddr = {0};
    char* binary;
    char flag[32];

    if (argc != 3) {
        fprintf(stderr, "launcher /path/to/binary /path/to/flag.txt");
        return 1;
    }

    binary = argv[1];
    {
        FILE* fp = fopen(argv[2], "r");
        if (fp == NULL) {
            fprintf(stderr, "Unable to open: %s\n", argv[3]);
            return 1;
        }

        fgets(&flag[0], sizeof(flag), fp);
        {
            char *newline = strchr(&flag[0], '\n');
            if (newline != NULL) {
                *newline = '\0';
            }
        }

        if (strlen(&flag[0]) == 0) {
            fprintf(stderr, "Unable to read flag\n");
            return 1;
        }

        fclose(fp);
    }

    // Setting the SIGCHLD handler to SIG_IGN prevents child
    // processes from becoming zombies (so you do not need to
    // call wait() on them).
    if (signal(SIGCHLD, SIG_IGN) == SIG_ERR) {
        fputs("Failed to set SIGCHLD handler.", stderr);
        return 1;
    }

    sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sockfd == -1) {
        perror("socket");
        return 1;
    }

    // Set SO_REUSEADDR. Otherwise, if the server crashes for
    // any reason, you will have to wait for sockets to time
    // out before you can reuse the port.
    opt = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt,
                   sizeof(opt)) != 0) {
        perror("setsockopt");
        return 1;
    }

    saddr.sin_family = AF_INET;
    saddr.sin_addr.s_addr = htonl(INADDR_ANY);
    saddr.sin_port = htons(port);

    if (bind(sockfd, (struct sockaddr *) &saddr,
             sizeof(saddr)) != 0) {
        perror("bind");
        return 1;
    }

    if (listen(sockfd, 20) != 0) {
        perror("listen");
        return 1;
    }

    while (1) {
        clientfd = accept(sockfd, NULL, NULL);
        if (clientfd == -1) {
            perror("accept");
            continue;
        }

        pid = fork();
        if (pid == -1) {
            perror("fork");
            close(clientfd);
            continue;
        }

        if (pid == 0) {
            // Avoid tons of long-running processes sticking around.
            alarm(120);

            // If you do not close the socket fd, someone who
            // exploits the service could call accept() on it and
            // hijack other people's connections.
            close(sockfd);

            // The server is started as root and drops privileges
            // after forking and before handling the request.
            // Otherwise, someone who exploits the service can
            // kill, ptrace, or otherwise interfere with the server.
            // XXX FIXME
            //rc = drop_privs("problemuser");
            rc = 0;
            if (rc == 0) {
                rc = handle(clientfd, binary, &flag[0]);
            }

            close(clientfd);
            _exit(rc);
        }

        // If you forget to close the client fd,  you could run
        // out of file descriptors (it also makes the connection fd
        // hard to predict, which can be annoying for someone
        // writing an exploit - if you want to do this on purpose,
        // use dup2 with a random fd instead :-P).
        close(clientfd);
    }

    return 0;
}
