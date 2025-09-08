#ifndef MYSTDIO_H
#define MYSTDIO_H	1

#include <fcntl.h>
#include <sys/file.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>

#define BUFSIZE     1024    /* Default buffer size: 1024 bytes  */
#define EOF         -1      /* to indicate the end of the file. */

#define SEEK_SET    0       /* Seek from beginning of file.     */
#define SEEK_CUR    1       /* Seek from current position.      */
#define SEEK_END    2       /* Seek from end of file.           */

#define STDIN_FD    0
#define STDOUT_FD   1
#define STDERR_FD   2

#define OP_NONE  -1
#define FILE_READ  0
#define FILE_WRITE  1

typedef struct _myFILE{
	int fd;                 /* file descriptor of this file     */
    char wrbuffer[BUFSIZE]; /* write buffer of this file        */
    size_t buffer_length;
    int mode_flag;          /* flag to describe opened mode     */
    int offset;             /* current position of a file (file position indicator) */
    int last_operation;     /* last operation for this file (read or write) */
} myFILE;


myFILE *myfopen(const char *pathname, const char *mode);
int myfclose(myFILE *stream);
int myfseek(myFILE *stream, int offset, int whence);
int myfread(void *ptr, int size, int nmemb, myFILE *stream);
int myfwrite(const void *ptr, int size, int nmemb, myFILE *stream);
int myfflush(myFILE *stream);
int myfputs(const char* str, myFILE* stream);
char* myfgets(char* str, int num, myFILE* stream);


/* ************************
 *  Implement after here. *
 * ************************ */

/* fopen mode: "r", "r+", "w", "w+", "a", "a+" */
myFILE *myfopen(const char *pathname, const char *mode){
    int flag = 0;
    int mode_flag = 0;
    if (strcmp(mode, "r")==0){
        flag = O_RDONLY;
        mode_flag = O_RDONLY;
    } else if (strcmp(mode,"r+")==0) {
        flag = O_RDWR;
        mode_flag = O_RDWR;
    } else if (strcmp(mode,"w")==0) {
        flag = O_WRONLY| O_CREAT | O_TRUNC;
        mode_flag = O_WRONLY;
    } else if (strcmp(mode,"w+")==0) {
        flag = O_RDWR|O_CREAT|O_TRUNC;
        mode_flag = O_RDWR;
    } else if (strcmp(mode, "a")==0) {
        flag = O_WRONLY|O_CREAT|O_APPEND;
        mode_flag = O_WRONLY;
    } else if (strcmp(mode, "a+")==0) {
        flag = O_RDWR|O_CREAT|O_APPEND;
        mode_flag = O_RDWR;
    } else
        return NULL;

    int fd = open(pathname, flag, 0644);

    if (fd == -1) {
        struct stat sb;
        if (errno == EACCES) {
            const char *error = "Permission Denied\n";
            write(STDERR_FD, error, strlen(error));
            return NULL;
        } else { //including false positive
            const char *error = "File Format Error\n"; 
            write(STDERR_FD, error, strlen(error));
            return NULL;
        }
    }
    myFILE *file = malloc(sizeof(myFILE));
    if (!file) {
        close(fd);
        return NULL;
    }
    file->fd = fd;
    file->mode_flag = mode_flag;
    file->offset = 0;
    file->last_operation = OP_NONE;
    file->buffer_length = 0;
    return file;
}

int myfflush(myFILE * stream);

int myfclose(myFILE *stream) {
    if (stream == NULL)
        return EOF;
    if (myfflush(stream) == EOF) {
        return EOF;
    }
    if (close(stream->fd)==-1) {
        free(stream);
        return EOF;
    }
    free(stream);
    return 0;
}

int myfseek(myFILE *stream, int offset, int whence){
    if (stream == NULL)
        return -1;
    if (stream->last_operation == FILE_WRITE) {
        if(myfflush(stream) == EOF)
            return -1;
    }
    off_t seek = lseek(stream->fd, offset, whence);
    if (seek == -1)
        return -1;
    // stream->offset = seek;
    stream->last_operation= OP_NONE;
    return 0;
}

int myfread(void *ptr, int size, int nmemb, myFILE *stream){
    if (stream->mode_flag==O_WRONLY)    return 0;
    if (stream==NULL||ptr==NULL||size<=0||nmemb<=0) return 0;

    int total = nmemb*size;
    if (stream->last_operation == FILE_WRITE) {
        if (myfflush(stream) == EOF)
            return 0;
    }
    ssize_t read_byte = read(stream->fd, ptr, total);
    if (read_byte < 0) { // error
        return 0;
    }
    stream->last_operation = FILE_READ;
    return read_byte/size;
}

int myfwrite(const void *ptr, int size, int nmemb, myFILE *stream){
    if (stream->mode_flag == O_RDONLY)
        return 0;
    if (stream == NULL || ptr == NULL || size <= 0 || nmemb <= 0)
        return 0;
    int total = nmemb * size;
    const char *start = (const char *)ptr;
    const char *stop = start + total;
    while (stop > start) {
        size_t remaining = BUFSIZE - stream->buffer_length;
        size_t copy_size = (remaining > stop - start) ? (stop - start) : remaining;
        memcpy(stream->wrbuffer + stream->buffer_length, start, copy_size);
        stream->buffer_length += copy_size;
        start += copy_size;
        stream->last_operation = FILE_WRITE;
        if (remaining == copy_size && myfflush(stream) == EOF)
            return 0;
    }
    return nmemb;
}

int myfflush(myFILE *stream){
    if (stream==NULL)
        return EOF;
    switch (stream->last_operation) {
    case OP_NONE:
        return 0;
    case FILE_READ:
        stream->buffer_length = 0;
        return 0;
    case FILE_WRITE:
        if (stream->buffer_length > 0) {
            ssize_t w = write(stream->fd, stream->wrbuffer, stream->buffer_length);
            // if (w != w_bytes)
            if (w != stream->buffer_length)
                return EOF;
            stream->buffer_length = 0;
        }
        return 0;
    }
    /*
     * unreachable, which is standardized in C23
     * but that is too new for Ubuntu 22.10
     */
    return EOF;
}

int myfputs(const char* str, myFILE* stream){
    int length = strlen(str);
    return (myfwrite(str, sizeof(char), length, stream) == length) ? 0 : EOF;
}

char* myfgets(char *str, int num, myFILE* stream){
    if (stream == NULL || str == NULL || num < 1)
        return NULL;
    if (stream->mode_flag == O_WRONLY)
        return NULL;
    char c;
    int count = 0;

    while (count < num-1) {
        ssize_t r = myfread(str, sizeof(char), 1, stream);
        if(r == 0) //EOF
            break;
        else if (r < 0)
            return NULL;
        str[count++] = c;
        if (c = '\n')
            break;
    }

    if (count == 0 && num>1) //EOF cannot be reached with num=1
        return NULL; 

    str[count] = '\0';
    stream->last_operation = FILE_READ;
    return str;
}

#endif // mystdio.h included