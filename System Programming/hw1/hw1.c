
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *s = NULL; // init an empty string
int sz = 1;     // current size
int id = 0;
void ReadInput() // read input
{
    s = (char *)malloc(sz); // init size of string

    while (1)
    {
        char c = getchar(); // read a character from input file
        if (c == EOF)
            break; // break if finished read file
        if (c == '\n')
            continue;     // skip endl
        if (id >= sz - 1) // need more memory space
        {
            sz *= 2;
            s = (char *)realloc(s, sz); // resize
        }
        s[id++] = c;
    }
    id--;
}
unsigned char *convert(int *n) // convert bit string to bytes
{
    int len = strlen(s);
    *n = len / 8;
    unsigned char *bytes = malloc(len);
    int i = 0;
    // convert each 8bit to bytes
    while (i < len)
    {
        int j = i;
        while (j < i + 8)
        {
            bytes[i / 8] = bytes[i / 8] * 2 + (s[j] == '1'); 
            j++;
        }
        i = j;
    }
    return bytes;
}
void reverse(unsigned char *cur, int n) // Little Endian Conversion
{
    for (int i = 0; i < n; i += 8)
    {
        if (i + 7 >= n) // less than 8 bytes
            break;
        for (int j = i; j < i + 4; j++) // reverse cur(i...i+7) -> cur(i+7...i)
        {
            // swap 
            int val = cur[j]; 
            cur[j] = cur[i + 7 - (j - i)];
            cur[i + 7 - (j - i)] = val;
        }
    }
}
void print(unsigned char *cur, int n) // print output
{
    printf("Signed Char: ");
    for (int i = 0; i < n; i++)
        printf("%d ", cur[i]);
    printf("\n");

    printf("ASCII Codes: ");
    for (int i = 0; i < n; i++)
    {
        if (cur[i] < 32 || cur[i] > 126) // not ASCII
        {
            printf(". ");
            continue;
        }
        printf("%c ", cur[i]);
    }
    printf("\n");

    printf("Unsigned Char: ");
    for (int i = 0; i < n; i++)
        printf("%d ", cur[i]);
    printf("\n");

    printf("Signed Int: ");
    for (int i = 0; i < n; i += 4)
    {
        if (i + 3 >= n)
            break;
        signed int res = 0;
        for (int j = 0; j < 4; j++)
            res |= cur[i + j] << (8 * j);
        // merge into 32_bit
        printf("%d ", res);
    }
    printf("\n");

    printf("Unsigned Int: ");
    for (int i = 0; i < n; i += 4)
    {
        if (i + 3 >= n)
            break;
        // similar to signed int, but using unsigned type
        unsigned int res = 0;
        for (int j = 0; j < 4; j++)
            res |= cur[i + j] << (8 * j);
        printf("%d ", res);
    }
    printf("\n");

    printf("Signed Float: ");
    for (int i = 0; i < n; i += 4)
    {
        if (i + 3 >= n) break;
        float res = 0;
        // 4bit
        res = *((float *)(cur + i));
        printf("%.4f ", res);
    }
    printf("\n");

    printf("Signed Double: ");
    for (int i = 0; i < n; i += 8)
    {
        if (i + 3 >= n) break;
        double res = 0;
        // 8bit
        res = *((double *)(cur + i));
        printf("%.4f ", res);
    }
    printf("\n");
}
int main()
{
    freopen("input.txt", "r", stdin); // read input from a file
    freopen("output.txt", "w", stdout); // write to a file

    ReadInput();
    int n;
    unsigned char *cur = convert(&n);
    reverse(cur, n);
    print(cur, n);

    // free up memory
    free(s);
    free(cur);
}