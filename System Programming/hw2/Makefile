CC=gcc
CFLAGS= -Wall -g -I.

# Change the name of source code files 
# assignment2.h 
# assignment2.c
DEPS = assignment2.h
OBJ = assignment2.o 

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

# Change the name of the output binary file to assignment2
assignment2: $(OBJ)
	gcc -o $@ $^ $(CFLAGS)

clean:
	rm -rf *.o assignment2

