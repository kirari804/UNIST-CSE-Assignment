#include "mystdio-skel.h"
int main() {
    myFILE *file = myfopen("test_read_write.txt", "w+");
    const char *text = "Sample text to write to file.";
    myfwrite(text, sizeof(char), strlen(text), file);
    myfseek(file, 0, SEEK_SET); // Go back to the start of the file

    unsigned char buffer[BUFSIZE];
    for (size_t i = 0; i<40; i++) {
        printf(" %02x", buffer[i]);
    }
    putchar('\n');
    myfread(buffer, sizeof(char), strlen(text), file);
    for (size_t i = 0; i<40; i++) {
        printf(" %02x", buffer[i]);
    }
    putchar('\n');
    printf("Read from file: %s\n", buffer);
    myfclose(file);
    return 0;
}