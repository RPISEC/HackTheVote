#include <stdio.h>
#include <stdlib.h>

int main() {
    system("chattr -iu /flag");
    system("chmod 777 /flag");
}
