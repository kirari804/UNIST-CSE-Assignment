#include "mystdio-skel.h"
#include <assert.h>

int main() {
    myFILE *file = myfopen("test_seek.txt", "r+");
    char buffer[BUFSIZE];
    
    assert(myfread(buffer, sizeof(char), BUFSIZE, file)==10);
    myfseek(file, 0, SEEK_SET); // Rewind to the start of the file
    assert(myfread(buffer, sizeof(char), BUFSIZE, file)==10);
    printf("%s", buffer);
    myfclose(file);
    return 0;
}
