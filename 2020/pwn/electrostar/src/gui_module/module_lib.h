#include <stddef.h>
#include <stdint.h>

#define FOR_EACH_FUNC(v) \
    v(0, libc, int, printf, const char *format, ...) \
    v(1, libc, size_t, write, int fd, const void *buf, size_t count) \
    v(2, libc, size_t, read, int fd, const void *buf, size_t count) \
    v(3, libc, size_t, strlen, const char *s) \
    v(4, nc, void, endwin) \
    v(5, nc, int, getch) \
    v(6, nc, void, refresh) \
    v(7, mu, void*, new_item, char*, char*) \
    v(8, mu, void*, new_menu, void**) \
    v(9, mu, void, post_menu, void*) \
    v(10, mu, void, menu_driver, void*, int) \
    v(11, mu, void, menu_opts_off, void*, int) \
    v(12, mu, void*, current_item, void*) \
    v(13, mu, int, item_index, void*) \
    v(14, mu, int, item_value, void*) \
    v(15, nc, void*, newwin, int, int, int, int) \
    v(16, nc, void, keypad, void*, int) \
    v(17, mu, void, set_menu_win, void*, void*) \
    v(18, mu, void, set_menu_sub, void*, void*) \
    v(19, nc, void*, derwin, void*, int, int, int, int) \
    v(20, mu, void, set_menu_mark, void*, char*) \
    v(21, nc, void, wrefresh, void*) \
    v(22, nc, void, box, void*, int, int) \
    v(23, mu, void, unpost_menu, void*)
//    v(5, nc, void, cbreak) \
//    v(6, nc, void, noecho)


#define FUNC_ENUM_ENTRY(o, lib, ret, name, ...) ordinal_##name,
enum ordinals {
    FOR_EACH_FUNC(FUNC_ENUM_ENTRY)
    ordinal_count
};
#undef FUNC_ENUM_ENTRY

void* func_table[ordinal_count];

#define FUNC_DEF(o, lib, ret, name, ...) \
    extern ret name(__VA_ARGS__);
FOR_EACH_FUNC(FUNC_DEF)
#undef FUNC_DEF

__asm__(".global get_func_table\n" \
        "get_func_table:\n" \
        "lea rax, [rip + 0x2000]\n" \
        "ret\n"\
        );

#define FUNC_JMP(o, lib, ret, name, ...) \
    __asm__(".global " #name "\n" \
            #name ":\n" \
            "call get_func_table\n" \
            "jmp QWORD PTR [rax + " #o "*8]\n"\
            );
FOR_EACH_FUNC(FUNC_JMP)
#undef FUNC_JMP
    
typedef void* (*dlsymfunc)(void*, const char*);
typedef void* (*dlopenfunc)(const char *filename, int flags);

void load_got(dlopenfunc dlopen, dlsymfunc dlsym) {
    void* libc = dlopen("libc.so.6", 258);
    void* nc = dlopen("libncurses.so.5", 258);
    void* mu = dlopen("libmenu.so.5", 258);
#define FUNC_LOOKUP(o, lib, ret, name, ...) \
    func_table[ordinal_##name] = dlsym(lib, #name);
    FOR_EACH_FUNC(FUNC_LOOKUP)
#undef FUNC_LOOKUP
}

typedef struct {
    unsigned char privlaged : 1;
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
} ipc_client;

ipc_client* g_client;



void send_ipc(uint32_t call_code, char* buf, uint16_t len) {
    len += 4;
    write(g_client->ipc_to_parent.write, &len, 2);
    write(g_client->ipc_to_parent.write, &call_code, 4);
    write(g_client->ipc_to_parent.write, buf, len-4);
}

void ipc_fwrite(char* buf, uint16_t len) {
    send_ipc(1, buf, len);
}

void swrite(char* buf) {
    ipc_fwrite(buf, strlen(buf));
}

