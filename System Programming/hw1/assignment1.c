#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include "assignment1.h"

int main()
{
  char byte[9];
  FILE *f = fopen("input.txt", "r");
  int c;
  signed char *line = NULL;
  size_t length = 0;
  while (c = fgetc(f), c != EOF) {
    ungetc(c, f);
    while (c = fgetc(f), c != EOF && c != '\n') {
      ungetc(c, f);
      length += 8;
      line = realloc(line, length);
      for (size_t i = length - 8; i < length; i++) {
        fgets(byte, 9, f);
        line[i] = strtol(byte, NULL, 2);
      }
    }
  }
  
  fclose(f);
  for (size_t i = 0; i < length/2; i++) {
    signed char temp = line[i];
    line[i] =  line[length -i -1];
    line[length -i -1] = temp;
  }
  f = fopen("output.txt", "w");
  
  fprintf(f, "Signed Char: ");
  for (size_t i = 0; i < length; i++) {
    fprintf(f, "%hhd ", line[i]);
  }
  
  fprintf(f, "\nASCII Codes: ");
  for (size_t i = 0; i < length; i++) {
    fprintf(f, "%c ", isprint(line[i]) ? line[i] : '.');
  }
  
  fprintf(f, "\nUnsigned Char: ");
  for (size_t i = 0; i < length; i++) {
    fprintf(f, "%hhu ", line[i]);
  }
  
  fprintf(f, "\nSigned Int: ");
  for (size_t i = 0; i < length; i+=4) {
    fprintf(f, "%d ", *(signed int *) (line+i));
  }
  
  fprintf(f, "\nUnsigned Int: ");
  for (size_t i = 0; i < length; i+=4) {
    fprintf(f, "%u ", *(unsigned int *) (line+i));
  }
  
  fprintf(f, "\nSigned Float: ");
  for (size_t i = 0; i < length; i+=4) {
    fprintf(f, "%0.4f ", *(float *) (line+i));
  }
  
  fprintf(f, "\nSigned Double: ");
  for (size_t i = 0; i < length; i+=8) {
    fprintf(f, "%0.4f ", *(double *) (line+i));
    }

  free(line);
  fclose(f);
  return 0;
}
