#include "module_lib.h"

int result_index = 0;
char results[0x100] = {};

//void hack() {
//    asm("int3");
//    asm("    /* call syscall(28, 93824994340864, 4096, 4) */\n    push 0x1c\n    pop rax\n    mov rdi, 0x101010101010101 /* 93824994340864 == 0x555555757000 */\n    push rdi\n    mov rdi, 0x101545454747101\n    xor [rsp], rdi\n    pop rdi\n    push 4\n    pop rdx\n    mov esi, 0x1010101 /* 4096 == 0x1000 */\n    xor esi, 0x1011101\n    syscall\n");
//}

/*
size_t shit_strncpy(char* dest, char* src, size_t len) {
   for (size_t i = 0; i < len; i++) {
       if (src[i] == '\0')
           return i;
       dest[i] = src[i];
   }
   return len;
}
*/

void process_input(char* x) {
    char num_votes = x[0];
    char buf[num_votes];
    size_t len = num_votes < 100u ? num_votes : 100u;
    memcpy(buf, x+1, len);

    //asm("int3");
    unsigned char max = 0;
    for(size_t i=0; i<len; i++)  {
        if ((unsigned int)buf[i] > (unsigned char)max)
            max = buf[i];
    }
    //asm("int3");
    results[(result_index++)&0xff] = max;
}

void _start(void* handle, dlsymfunc dlsym, ipc_client* client) {
    g_client = client;
    load_got(handle, dlsym);
    swrite("Initalizing Ballot Casting Module...\n");
    swrite("Done!\n");

    while (1) {
        swrite("Waiting for input from GUI...\n");
        char* x = ipc_fgets(100);
        //swrite(x);

        process_input(x);
        free(x);
    }
}

void get_flag() {
    swrite("Dumping Flag!\n");
    send_ipc(1337, NULL, 0);
}

