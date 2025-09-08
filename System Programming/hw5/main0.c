#include "mystdio-skel.h"
#include <stdio.h>

#define BUFSIZE 5

int main() {
    myFILE* f = myfopen("/dev/fd/0", "r");
    char buffer[BUFSIZE] = "csdg";
    fgets(buffer, 1, f);
    puts(buffer);
    myfclose(f);
    return 0;
}