#ifndef ASSIGNMENT4_H
#define ASSIGNMENT4_H

enum type {
    char_t,
    short_t,
    int_t,
    long_t,
    float_t,
    struct_t,
    invalid = -1
};

struct metadatum {
    enum type type;
    enum type struct_types[8];
    char name[51];
    unsigned char start;
    unsigned char stop;
};

void dump_mem(const char *mem, size_t len);
enum type define_type(const char* s);
bool check_range(enum type t, const char *val_str);
bool duplicate_name(const char *name, struct metadatum *metadata, int count);
#endif