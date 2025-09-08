#include "mystdio-skel.h"
int main() {
    myFILE *file = myfopen("test_flush.txt", "w");
    myfputs("This is a test.", file);
    myfflush(file);
    myfclose(file);
    return 0;
}