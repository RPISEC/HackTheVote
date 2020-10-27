#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <dlfcn.h>
#include <sys/select.h>
#include <curses.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/wait.h>

#include "colors.h"

#include "crypto/crypt.c"
#include "sandbox.h"

int load_module_from_file(char* filename, int is_init);
int load_module_from_memory(unsigned char* blob, size_t blob_len);

struct {
    char hash[SHA256_DIGEST_LENGTH];
    char used;
} unique_modules[3] = {
    { {M1HASH}, 0},
    { {M2HASH}, 0},
    { {M3HASH}, 0}
};


uint64_t record_array[32];

int has_gui = 0;

typedef struct {
    unsigned char privlaged : 1;
    unsigned char is_gui : 1;
    unsigned char is_init : 1;
} ipc_flags;

struct pipe {
    int read;
    int write;
} __attribute__((packed));

typedef struct ipc_client {
    union {
        ipc_flags flags;
        char raw;
    } f;
    int pid;
    struct pipe ipc_to_parent;
    struct pipe ipc_to_child;
    int ipc_child[2];
    struct ipc_client* next;
    struct ipc_client** head; // TODO better leak
} ipc_client;

ipc_client* ipc_head = NULL;
int num_procs = 0;

void* map_page = (void*)0x500000;

void clean(ipc_client* client) {
    if (!has_gui)
        printf("[Module %u] Scrubbing process for security\n", getpid());

    ipc_client* cur = ipc_head;
    if (cur != NULL)
        cur = cur->next;
    while (cur != NULL) {
            // Close any other ipc fds so we can't use them
        if (cur != client) {
            //printf("[Module %u] closing %u %u %u %u\n", cur->ipc_to_parent.read,cur->ipc_to_parent.write,cur->ipc_to_child.read,cur->ipc_to_child.write);

            close(cur->ipc_to_parent.read);
            close(cur->ipc_to_parent.write);
            close(cur->ipc_to_child.read);
            close(cur->ipc_to_child.write);
        }
        cur = cur->next;
    }

    asm("mov $0, %r10");
    FILE* f = fopen("/proc/self/maps","r");
    char* line = NULL;
    size_t line_len = 0;

    char buff[32] = {0};
    void* start;

    asm("mov $0, %r10");
    while(getline(&line, &line_len, f) != -1) {
        sscanf(line, "%lx-%*x %*4c %*x %*x:%*x %*u %7s",(unsigned long*)&start, buff);

        free(line);
        line = NULL;

        if (!strcmp(buff,"[stack]"))
            break;
    }

    enable_sandbox();

    register void *sp asm ("sp");

    // Delete any part of the stack after the current stack frame
    asm("xor %%eax, %%eax;"
        "mov %0, %%rdi;"
        "mov %1, %%rcx;"
        "rep stosb (%%rdi)"
        :
        : "r" (start), "r" (sp-start)
        : "rax", "rdi", "rcx");
}


void* map_image(char* blob, size_t blob_len, ipc_client* client) {
    size_t size = (blob_len&(~0xfff)) + 0x1000;

    void (*addr)(void*, void*, ipc_client*) = map_page;

    mmap(addr, size, PROT_EXEC|PROT_READ|PROT_WRITE,
            MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED, 0, 0);

    if (!has_gui)
        printf("DEBUG: Module mapped to %p\n" CL, addr);

    //printf(YELLOW "WARN: copying %u bytes over %p\n" CL, blob_len, addr);
    memcpy(addr, blob, blob_len);

}

void cleanup_ncurses(int sig) {
    endwin();
    printf(RED "GUI Process Crashed with %s\n" CL, sys_siglist [sig]);
    exit(-1);
}

void init_ncurses() {
    initscr();
    cbreak();
    noecho();
    start_color();
    init_pair(1, COLOR_RED, COLOR_BLACK);
    keypad(stdscr, TRUE);
    dlopen("libmenu.so.5", 258);

    // Handle a crash
    signal(SIGSEGV, cleanup_ncurses);
    signal(SIGPIPE, cleanup_ncurses);
    signal(SIGFPE, cleanup_ncurses);
}

int start_module(char* blob, size_t blob_len, int is_init) {
    if (!has_gui)
        printf("DEBUG: Image Size = %lu bytes\n", blob_len);
    if (blob_len < 2)
        return -1;

    ipc_client* client = calloc(sizeof(ipc_client),1);
    client->next = ipc_head;
    ipc_head = client;

    //printf(RED "NOTE: allocated client at %p size %lu\n" CL, client,sizeof(ipc_client));


    // Save meta data
    client->f.raw = blob[0];
    client->head = (void*)&ipc_head;

    // Unset flag since we don't know if it is true yet
    client->f.flags.is_init = 0;
    num_procs++;

    // Init proc, set flag
    if (is_init) {
        client->f.flags.is_init = 1;
    }

    if (client->f.flags.is_gui) {
        if (!has_gui)
            puts("Starting GUI module, supressing log output");
        has_gui++;
    }

    pipe((int*)&client->ipc_to_parent);
    pipe((int*)&client->ipc_to_child);


    //printf("DEBUG: forking now\n");
    int pid = fork();
    if (pid == 0) {
        if (!has_gui)
            printf("[Module %u] Started Module Load\n", getpid());

        if (client->f.flags.is_gui) {
            // Preload gui libs before sandboxing
            init_ncurses();
        }


        // We have to keep this open so we can do the fake ipc from init
        //close(client->ipc_to_parent.read);
        //close(client->ipc_to_child.write);

        // Child
        void (*addr)(void*, void*, ipc_client*);
        addr = map_image(blob+1, blob_len - 1, client);

        clean(client);

        addr(dlopen, dlsym, client);

        exit(0);
    } else {
        client->pid = pid;

        // We have to keep this open so we can do the fake ipc from init
        //close(client->ipc_to_parent.write);
        //close(client->ipc_to_child.read);
        
        // Parent is done now
        return 1;
    }
}

// XXX clear this out before using?
ipc_client* waiting_for_input = NULL;
size_t input_read_len = 0;

void check_gui_output(char* data, size_t len) {

    // If we have a proc waiting but GUI exited...
    if (data == NULL && waiting_for_input != NULL && !has_gui) {
        puts(YELLOW "WARN: No GUI process, falling back to STDIN" CL);
        char* input = calloc(input_read_len,1);
        fgets(input, input_read_len, stdin);
        write(waiting_for_input->ipc_to_child.write, &input_read_len, 2);
        write(waiting_for_input->ipc_to_child.write, input, input_read_len); 
        free(input);
        waiting_for_input = NULL;
        return;
    }

    if (data == NULL)
        return;

    // If we get gui input but have nothing waiting for it
    if (waiting_for_input == NULL) {
        puts(YELLOW "WARN: GUI process has no pipe connected, data lost" CL);
        return;
    }

    if (len > input_read_len)
        len = input_read_len;

    //printf(RED "NOTE: Writing to fd %u\n" CL, waiting_for_input->ipc_to_child.write);

    write(waiting_for_input->ipc_to_child.write, &len, 2);
    // UAF to control the file descriptor and write to the out of proc module read fd 
    // This will send a fake ipc message which we can use to do something maybe
    write(waiting_for_input->ipc_to_child.write, data, len);
    waiting_for_input = NULL;
}

void process_ipc(ipc_client* client, char* buff, size_t len) {
    //printf("ipc len = %lu\n", len);
    if (len < 4) {
        return;
    }
    uint32_t call_num = *(uint32_t*)(buff);
    //printf("call_num = %u %x\n", call_num, call_num);
    if (call_num == 1) {
        if (has_gui)
            return;

        if (len <= 4)
            return;

        printf("[Module %u] ", client->pid);
        fwrite(buff+4, len-4, 1, stdout);
        return;
    }

    if (call_num == 2) {
        if (waiting_for_input != NULL) {
            // We can only read one at a time, so fail
            size_t zero = 0;
            write(client->ipc_to_child.write, 0, 2);
            return;
        }

        if (len < 4+2)
            return;

        // Set as waiting for gui input
        waiting_for_input = client;
        input_read_len = *(uint16_t*)(buff+4);
        //printf(RED "NOTE: Set module %u to waiting_for_input\n" CL, client->pid);

        // no gui, check right away
        check_gui_output(NULL, 0);

        return;
    }

    // GUI input
    if (call_num == 10) {
        if (!client->f.flags.is_gui) {
            printf(YELLOW "WARN: Module %u does not have permission for command 10\n" CL, client->pid);
            return;
        }
        if (len <= 4)
            return;
        //printf(RED "NOTE: Got GUI read from %u %p len %lu\n" CL, client->pid, buff, len);
        check_gui_output(buff+4, len-4);
    }

    if (call_num == 20) {
        if (len <= 4)
            return;
        char* module_path = strndup(buff+4, len-4);
        if (!has_gui)
            printf("[Module %u] Loading module from '%s'\n",
                    client->pid, module_path);

        load_module_from_file(module_path, 0);
        free(module_path);
        return;
    }

    if (call_num == 21) {
        if (!has_gui)
            printf("[Module %u] Loading module from memory len %lu\n", client->pid, len-4);
        if (len <= 4)
            return;

        load_module_from_memory(buff+4, len-4);
        return;
    }

    if (call_num == 50) {
        if (!client->f.flags.is_init) {
            printf(YELLOW "WARN: Only the init module can call command 50\n" CL);
            return;
        }
        //printf(GREEN "WARN: Calling command 50\n" CL);

        if (len < 4+4+8)
            return;

        int32_t index = *(int32_t*)(buff+4);
        uint64_t value = *(uint64_t*)(buff+4+4);
        if (index >= 32) {
            printf(YELLOW "WARN: Command 50 out of bounds!\n" CL);
            return;
        }

        record_array[index] = value;
        //printf(YELLOW "WARN: map is now %p\n" CL, map_page);
    }
    
    if (call_num == 1337) {
        char flag[64];
        FILE* f = fopen("flag1.txt","r");
        fgets(flag, 64, f);
        fclose(f);

        printf(GREEN "[Module %u] Here is your flag #1: %s\n" CL, client->pid, flag);
        return;
    }
    
    if (call_num == 31337) {
        if (!client->f.flags.privlaged) {
            printf(YELLOW "WARN: Module %u does not have permission for command 31337\n" CL, client->pid);
            return;
        }
        char flag[64];
        FILE* f = fopen("flag2.txt","r");
        fgets(flag, 64, f);
        fclose(f);

        printf(GREEN "[Module %u] Here is your flag #2: %s\n" CL, client->pid, flag);
        return;
    }
}

int read_ipc(ipc_client* client) {
    uint16_t len = 0;
    int num_read = read(client->ipc_to_parent.read, &len, 2);
    if (num_read == 0) {
        //printf("%u exited via no data sent\n",client->pid);
        return 0;
    }
    //printf("Len = %u\n", len);
    if (len == 0) {
        //printf("%u exited via empty ipc sent\n",client->pid);
        return 0;
    }
    void * buf = calloc(len,1);
    if (buf == NULL) {
        //printf("%u exited via not enough memory\n",client->pid);
        return 0;
    }
    size_t amt_read = 0;
    while  (amt_read < len) {
     amt_read += read(client->ipc_to_parent.read, buf+amt_read, len-amt_read);
    }
    process_ipc(client, buf, len);
    return 1;
}

void module_exited(ipc_client* prev, ipc_client* client) {
    printf(YELLOW "WARN: Module %u Exited\n" CL, client->pid);

    // Unlink client
    if (client == ipc_head)
        ipc_head = client->next;
    else
        prev->next = client->next;

    if (client->f.flags.is_gui) {
        has_gui--;
        if (!has_gui) {
            puts(YELLOW "WARN: GUI lost, resuming log output" CL);
            // If we lost gui, check output
            check_gui_output(NULL, 0);
        }
    }
    num_procs--;

    if (client->f.flags.is_init) {
        puts(RED "ERROR: Init exited, exiting..." CL);
        exit(0);
    }
    // If only init is left, exit
    if (num_procs == 1 && ipc_head->f.flags.is_init) {
        puts(YELLOW "WARN: all modules except init exited, quitting..." CL);
        exit(0);
    }
    
    // Close pipe
    close(client->ipc_to_parent.read);
    close(client->ipc_to_parent.write);
    close(client->ipc_to_child.read);
    close(client->ipc_to_child.write);
    
    //printf(RED "NOTE: freeing %u at %p\n" CL, client->pid, client);
    free(client);

}

int ipc_main() {
    fd_set rfds;

    FD_ZERO(&rfds);

    unsigned int num_fds = 0;

    ipc_client* client = ipc_head;
    while (client != NULL) {
        int fd = client->ipc_to_parent.read;
        FD_SET(fd, &rfds);
        if (fd > num_fds)
            num_fds = fd;
        client = client->next;
    }

    //printf("num_fds %u\n",num_fds);
    if (num_procs == 0) {
        puts(YELLOW "WARN: No more modules running, exiting..." CL);
        exit(0);
    }

    //printf("Running select\n");
    struct timeval tv = {1, 0};
    int ret = select(num_fds + 1, &rfds, NULL, NULL, &tv);
    //printf(YELLOW "ticking %u ...\n" CL, ret);
    //printf("select ret = %u\n",ret);

    ipc_client* prev = NULL;
    client = ipc_head;

    // Look for client with given fd
    while (client != NULL) {

        int fd = client->ipc_to_parent.read;
        //printf("%u checking fd %u\n",client->pid,fd);
        if (ret > 0 && FD_ISSET(fd, &rfds)) {
            //printf("%u says %u is set\n",client->pid,fd);

            if (!read_ipc(client)) {
                // Grab ref before freeing
                ipc_client* tmp = client->next;
                module_exited(prev, client);
                client = tmp;
                continue;
            }
        }

        // Check if still alive
        if (waitpid(client->pid, NULL, WNOHANG)) {
            // Grab ref before freeing
            ipc_client* tmp = client->next;
            module_exited(prev, client);
            client = tmp;
            continue;
        }

        prev = client;
        client = client->next;
    }
    return 1;
}

int check_for_unique_modules(char* hash) {
    for (int i=0; i<3; i++) {
        if (memcmp(unique_modules[i].hash, hash, SHA256_DIGEST_LENGTH))
            continue;

        if (unique_modules[i].used)
            return -1;

        // Mark as used so we can only load once
        unique_modules[i].used = 1;
    }
    return 1;
}

int load_module_from_memory(unsigned char* blob, size_t blob_len) {
    char* hash;

    int res = validate_blob(blob, &blob_len, &hash);
    if (res != 1) {
        // Error validating blob
        puts("ERROR: Could not load module: Invalid image");
        free(hash);
        return -1;
    }

    if (check_for_unique_modules(hash) != 1) {
        // Error validating blob
        puts("ERROR: Could not load module: Module is unique and can only be loaded once");
        free(hash);
        return -1;
    }
    free(hash);

    if (!has_gui)
        puts(GREEN "Image Signature Validated" CL);

    if (start_module(blob, blob_len, 0) == -1) {
        puts(RED "ERROR: Could not load module: Image too small" CL);
        return -1;
    }

    return 0;
}

int load_module_from_file(char* filename, int is_init) {
    FILE* f = fopen(filename,"r");
    if (f == NULL) {
        puts(RED "ERROR: Could not load module: Could not open image" CL);
        return -1;
    }

    size_t blob_len = 0;

    char* hash;

    unsigned char* blob = load_and_validate_blob(f, &blob_len, &hash);
    if (blob == NULL) {
        puts(RED "ERROR: Could not load module: Invalid image" CL);
        fclose(f);
        free(hash);
        return -1;
    }

    if (check_for_unique_modules(hash) != 1) {
        // Error validating blob
        puts("ERROR: Could not load module: Module is unique and can only be loaded once");
        fclose(f);
        free(hash);
        return -1;
    }

    free(hash);

    if (start_module(blob, blob_len, is_init) == -1) {
        puts(RED "ERROR: Could not load module: Image too small" CL);
        fclose(f);
        return -1;
    }
    fclose(f);

    return 0;
}

void change_dir() {
    char path[256];
    readlink("/proc/self/exe",path,255);
    *strrchr(path,'/') = 0;
    chdir(path);
}

void sign_module(char* module) {
    char* scrub = "Private Key Scrubbed";
    if (!strncmp(private_pem+31, scrub, strlen(scrub))) {
        fprintf(stderr, RED "ERROR: Could not sign module: Private Key Not Found!\n" CL);
        return;
    }
    FILE* f = fopen(module,"r");
    if (f == NULL) {
        fprintf(stderr, RED "ERROR: Could not sign module: Could not open image!\n" CL);
        fclose(f);
        return;
    }

    size_t len = 0;
    unsigned char* data = load_data_from_file(f, &len);
    fclose(f);

    char signed_module[strlen(module)+5];

    strcpy(signed_module, module);
    strcat(signed_module, ".sig");

    f = fopen(signed_module,"w");
    sign_and_dump_blob(data, len, f);
    fclose(f);

    fprintf(stderr, GREEN "Signed module written to %s\n" CL, signed_module);
}

int main(int argc, char** argv) {
    if (argc < 2) {
        fprintf(stderr, "machine modules/<signed image>\n");
        fprintf(stderr, "machine sign <image file>\n");
        return -1;
    }

    init_ec();

    if (!strcmp(argv[1],"sign")) {
        if (argc < 3) {
            fprintf(stderr, "machine sign <image file>\n");
            return -1;
        }
        sign_module(argv[2]);
        return 0;
    }

    change_dir();

    puts(
        "   ______        __           ______          \n"\
        "  / __/ /__ ____/ /________  / __/ /____ _____\n"\
        " / _// / -_) __/ __/ __/ _ \\_\\ \\/ __/ _ `/ __/\n"\
        "/___/_/\\__/\\__/\\__/_/  \\___/___/\\__/\\_,_/_/   (tm)");
    puts("Electrionic Balloting System");
    puts("Copyright 2011\n");



    puts("Booting Primary Module");

    int res = load_module_from_file(argv[1], strcmp(argv[1], "modules/init_module.img.sig") == 0);

    if (res != 0)
        return res;

    while(ipc_main()) {};

    return 0;

}
