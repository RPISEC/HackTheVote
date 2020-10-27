#include "module_lib.h"

void _start(void* handle, dlsymfunc dlsym, ipc_client* client) {
    g_client = client;
    load_got(handle, dlsym);
    swrite("[Init] Started Init Module\n");

    swrite("[Init] Starting GUI Module...\n");
    sleep(2);
    load_module("./modules/gui_module.img.sig");

    swrite("[Init] Starting Ballot Module...\n");
    load_module("./modules/ballot_module.img.sig");

    sleep(1000);

    return;

}
