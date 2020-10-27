#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include "crypt.c"

int has_gui = 0;

int main(int argc, char** argv) {

    init_ec();

    FILE* f = fopen(argv[1],"r");

    size_t len = 0;
    unsigned char* data = load_data_from_file(f, &len);
    fclose(f);

    printf("Read %u bytes\n",len);

    f = fopen(argv[2],"w");
    sign_and_dump_blob(data, len, f);
    fclose(f);
}


