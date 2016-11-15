#include <stdio.h>
#include <stdlib.h>
#include <sys/ptrace.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#include "sha1.h"

#define PATH_MAX 4096

int main(int argc, char** argv) {
    if (argc < 2)
        return -1;
    char buff[256];
    snprintf(buff, 255, "/proc/%s/maps",argv[1]);


    FILE* f = fopen(buff,"r");

    while(!feof(f)) {
        char buf[PATH_MAX+100], perm[5], dev[6], mapname[PATH_MAX];
        unsigned long begin, end, size, inode, foo;
        int n;

        if(fgets(buf, sizeof(buf), f) == 0)
            break;
        mapname[0] = '\0';

        sscanf(buf, "%lx-%lx %4s %lx %5s %ld %s", &begin, &end, perm,
            &foo, dev, &inode, mapname);

        size = end - begin;

        printf("Begin %lx, End %lx\n",begin, end);

        int id = atoi(argv[1]);
        ptrace(PTRACE_ATTACH, id, NULL, NULL);
        wait(NULL);


        SHA1 sha1;
        printf("Skipping by %u\n",sizeof(long));
        for (long i = begin; i<end; i+=sizeof(long)) {
            long r = ptrace(PTRACE_PEEKTEXT, id, i, NULL);
            sha1.addBytes((char*)&r, sizeof(long));
        }

        printf("sha1.H0 = %u;\nsha1.H1 = %u;\nsha1.H2 = %u;\nsha1.H3 = %u;\nsha1.H4 = %u;\nsha1.size = %u;\n",sha1.H0, sha1.H1, sha1.H2, sha1.H3, sha1.H4, sha1.size);

        break;

    }
    fclose(f);
}
