#define _GNU_SOURCE
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <poll.h>
#include <string.h>

#define die(s) do { perror(s); exit(1); } while(0)

void handler() {
    exit(1);
}

int main(int argc, char** argv) {
    char tmpdir[] = "/tmp/fileshare.XXXXXX";
    if (!mkdtemp(tmpdir))
        die("mkdtemp");
    if (chdir(tmpdir) == -1)
        die("chdir");
    if (chown(tmpdir, 65534, 65534) == -1)
        die("chown");

    system("cp /flag-* ./");
    system("cp /fileshare ./");
    system("tar xf /libs.tar.gz");
    system("mkdir proc files && chown nobody:nogroup files");

    char* args[] = {"unshare", "-p", "-f", "--mount-proc", "-R", tmpdir, "-w", "files", "/fileshare", 0, 0, 0};
    if (argc == 3 && !strcmp(argv[1], "-p")) {
        args[9] = argv[1];
        args[10] = argv[2];
    }
    signal(SIGCHLD, handler);
    int pid = fork();
    if (pid == -1)
        die("fork");
    if (!pid) {
        execvpe(args[0], args, 0);
        die("execvpe");
    }
    // if they close this main connection, kill the descendant process group
    struct pollfd pollfd = {0, POLLRDHUP, 0};
    poll(&pollfd, 1, -1);
    // test this actually works (doesnt leave dangling processes) when deploying
    kill(-getpgid(0), SIGKILL);
    return 0;
}
