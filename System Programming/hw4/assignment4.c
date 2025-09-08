#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include <limits.h>
#include <float.h>
#include "assignment4.h"

#define DATA_SIZE 128U

// enum type {
//     char_t,
//     short_t,
//     int_t,
//     long_t,
//     float_t,
//     struct_t,
//     invalid = -1
// };

// struct metadatum {
//     enum type type;
//     enum type struct_types[8];
//     char name[51];
//     unsigned char start;
//     unsigned char stop;
// };

void dump_mem(const char *mem, size_t len) {
    const char *buffer = mem;
    size_t i;
    for (i=0; i<len; i++){
        if (i>0 && i%16 == 0) {
        printf("\n");
        }
        printf("%02x ", buffer[i] & 0xff);
    }
    puts("");
}

enum type define_type(const char* s) {
    if (strcmp(s, "char") == 0) return char_t;
    if (strcmp(s, "short") == 0) return short_t;
    if (strcmp(s, "int") == 0) return int_t;
    if (strcmp(s, "long") == 0) return long_t;
    if (strcmp(s, "float") == 0) return float_t;
    if (strcmp(s, "struct") == 0) return struct_t;
    return invalid;
}

bool check_range(enum type t, const char *val_str) {
    char *endptr;
    errno = 0;

    switch (t) {
        case char_t: {
            return (strlen(val_str)==1);
        }
        case short_t: {
            unsigned long val = strtoul(val_str, &endptr, 10);
            if (errno != 0 || *endptr != '\0') return 0;
            return val <= 32767; 
        }
        case int_t: {
            unsigned long val = strtoul(val_str, &endptr, 10);
            if (errno != 0 || *endptr != '\0') return 0;
            return val <= 2147483647UL; // 2^31 -1
        }
        case long_t: {
            unsigned long long val = strtoull(val_str, &endptr, 10);
            if (errno != 0 || *endptr != '\0') return 0;
            return val <= 9223372036854775807ULL;
        }
        case float_t: {
            float val = strtof(val_str, &endptr);
            if (errno != 0 || *endptr != '\0') return 0;
            return 1; 
        }
        default:
            return false;
    }
}

bool duplicate_name(const char *name, struct metadatum *metadata, int count) {
    for (int i = 0; i < count; i++) {
        if (strcmp(name, metadata[i].name) == 0) {
            return true;
        }
    }
    return false;
}

int main()
{
    char data[DATA_SIZE] = {0};
    struct metadatum metadata[DATA_SIZE];
    struct metadatum meta;
    size_t data_ptr = 0;
    int count = 0;
    while (true) {
        int opt;
        printf("Do you want to allocate data (1) or deallocate data (2) ?\n");
        assert(scanf("%d", &opt) == 1);

        if (opt == 1) { 
            char types[80];
            puts("Input the type of data you want to allocate and the name of the data");
            assert(scanf("%s%s", types, meta.name) == 2);
            if (duplicate_name(meta.name, metadata, count)) {
                printf("Name is duplicated\n");
                continue;
            }
            getchar();
            meta.type = define_type(types);
            if (meta.type== invalid) {
                printf("Invalid type\n");
                continue;
            }

            if (meta.type == struct_t) {
                int n;
                printf("How many data should be in the struct\n");
                assert(scanf("%d", &n) == 1);
                getchar();
                if (n>8 || n<1){
                    printf("Struct should have at most 8 types and at least 1 type\n");
                    continue;
                }
                printf("Please input type each type and its value \n");
                meta.start = data_ptr;
                size_t original_ptr = data_ptr;
                int valid = 1;
                for (int i=0; i<n; i++) {
                    char line[1000];
                    assert(fgets(line, sizeof(line), stdin));
                    char* t = strtok(line, " ");
                    char* val = strtok(NULL, " ");
                    val[strcspn(val, "\n")] = 0;
                    enum type sub_type = define_type(t);
                    if (sub_type== invalid) {
                        printf("Invalid type\n");
                        valid = 0;
                        break;
                    }
                    if(!check_range(sub_type, val)) {
                        printf("There is invalid input\n");
                        valid = 0;
                        break;
                    }


                    if (sub_type == char_t) {
                        if((data_ptr+1) > DATA_SIZE) {
                            printf("There is not enough memory for the data you require, you can only use %zu byte(s)\n", DATA_SIZE - data_ptr);
                            valid = 0;
                            break;
                        }
                        unsigned char v = (unsigned char)val[0];
                        data[data_ptr++] = v;
                    } else if (sub_type == short_t) {
                        if((data_ptr+ sizeof(unsigned short)) > DATA_SIZE) {
                            printf("There is not enough memory for the data you require, you can only use %zu byte(s)\n", DATA_SIZE - data_ptr);
                            valid = 0;
                            break;
                        }
                        unsigned short v = (unsigned short)strtoul(val, NULL, 10);
                        memcpy(&data[data_ptr], &v, sizeof(v));
                        data_ptr += sizeof(v);
                    } else if (sub_type == int_t) {
                        if((data_ptr+ sizeof(unsigned int)) > DATA_SIZE) {
                            printf("There is not enough memory for the data you require, you can only use %zu byte(s)\n", DATA_SIZE - data_ptr);
                            valid = 0;
                            break;
                        }
                        unsigned int v = (unsigned int)strtoul(val, NULL, 10);
                        memcpy(&data[data_ptr], &v, sizeof(v));
                        data_ptr += sizeof(v);
                    } else if (sub_type == long_t) {
                        if((data_ptr+ sizeof(unsigned long long) > DATA_SIZE)) {
                            printf("There is not enough memory for the data you require, you can only use %zu byte(s)\n", DATA_SIZE - data_ptr); 
                            valid = 0;
                            break;
                        }
                        unsigned long long v = strtoull(val, NULL, 10);
                        memcpy(&data[data_ptr], &v, sizeof(v));
                        data_ptr += sizeof(v);
                    } else if (sub_type == float_t) {
                        if((data_ptr+ sizeof(float)) > DATA_SIZE) {
                            printf("There is not enough memory for the data you require, you can only use %zu byte(s)\n", DATA_SIZE - data_ptr);
                            valid = 0;
                            break;
                        }
                        float v = strtof(val, NULL);
                        memcpy(&data[data_ptr], &v, sizeof(v));
                        data_ptr += sizeof(v);
                    } 
                }
                if (!valid) {
                    memset(&data[original_ptr], 0, data_ptr - original_ptr);
                    data_ptr = original_ptr;
                    continue;
                }
            } else {
                char val_str[100];
                printf("Please input a value for the data type\n");
                assert(fgets(val_str, sizeof(val_str), stdin));
                val_str[strcspn(val_str, "\n")] = 0; 
                

                if (!check_range(meta.type, val_str)) {
                    printf("There is invalid input\n");
                    continue;
                }

                meta.start = data_ptr;
                if (meta.type == char_t) {
                    if((data_ptr+1) > DATA_SIZE) {
                        printf("There is not enough memory for the data you require, you can only use %zu byte(s)\n", DATA_SIZE - data_ptr);
                        continue;
                    }
                    unsigned char c = (unsigned char) val_str[0];
                    data[data_ptr++] = (unsigned char)c;
                }
                if (meta.type == short_t) {
                    if((data_ptr+ sizeof(unsigned short)) > DATA_SIZE) {
                        printf("There is not enough memory for the data you require, you can only use %zu byte(s)\n", DATA_SIZE - data_ptr);
                        continue;
                    }
                    unsigned short shrt =  (unsigned short)strtoul(val_str, NULL, 10);
                    memcpy(&data[data_ptr], &shrt, sizeof(shrt));
                    data_ptr += sizeof(shrt);
                }
                if (meta.type==int_t) {
                    if((data_ptr+ sizeof(unsigned int)) > DATA_SIZE) {
                        printf("There is not enough memory for the data you require, you can only use %zu byte(s)\n", DATA_SIZE - data_ptr);
                        continue;
                    }
                    unsigned int i=(unsigned int)strtoul(val_str, NULL, 10);
                    memcpy(&data[data_ptr], &i, sizeof(i));
                    data_ptr += sizeof(i);
                }
                if (meta.type == float_t) {
                    if((data_ptr+ sizeof(float)) > DATA_SIZE) {
                        printf("There is not enough memory for the data you require, you can only use %zu byte(s)\n", DATA_SIZE - data_ptr);
                        continue;
                    }
                    float v=strtof(val_str, NULL);
                    memcpy(&data[data_ptr], &v, sizeof(v));
                    data_ptr += sizeof(v);
                }
                if (meta.type == long_t) {
                    if((data_ptr+ sizeof(unsigned long long) > DATA_SIZE)) {
                        printf("There is not enough memory for the data you require, you can only use %zu byte(s)\n", DATA_SIZE - data_ptr); 
                        continue;
                    }
                    unsigned long long l = strtoull(val_str, NULL, 10);
                    memcpy(&data[data_ptr], &l, sizeof(l));
                    data_ptr += sizeof(l);
                }
            }

            meta.stop = (unsigned char)data_ptr;
            metadata[count++] = meta;
            
            printf("There is memory dump!\n");
            dump_mem(data, DATA_SIZE);

            printf("\n-----Data you have now-----\n");
            for (int i = 0; i < count; i++) {
                printf("%s \n", metadata[i].name);
            }
        } else if (opt == 2) { //deallocate
            char remove[100];
            printf("Input the name of data you want to deallocate \n");
            assert(scanf("%s", remove) == 1);
            getchar(); 
            int found = 0;
            for (int i=0; i<count; i++) {
                if (strcmp(metadata[i].name, remove)==0) {
                    found = 1;
                    int start = metadata[i].start;
                    int stop = metadata[i].stop;
                    int size = stop-start;

                    if(stop ==data_ptr) { //last in heap
                        memset(&data[start], 0 , size);
                        data_ptr = start;
                    }
                    else {
                        int n_shift = data_ptr - stop;
                        memmove(&data[start], &data[stop], n_shift);
                        memset(&data[data_ptr-size], 0 , size);
                        for (int j=i+1; j<count; j++) {
                            metadata[j].start -=size;
                            metadata[j].stop -= size;
                        }
                        data_ptr -= size;
                    }
                    for (int j=i; j < count - 1; j++) 
                        metadata[j] = metadata[j + 1];
                    count--;
                    printf("%s has been deallocated\n", remove);
                    break;
                }
            }
            if (!found) {
                printf("Deallocating wrong data\n");
            }
            printf("There is memory dump!\n");
            dump_mem(data, DATA_SIZE);

            printf("\n-----Data you have now-----\n");
            for (int i = 0; i < count; i++) {
                printf("%s \n", metadata[i].name);
            }
        }
    }
    return 0;
}