.PHONY=SDL default debug autotest
SHELL=/bin/bash

default: bin/vm

bin/vm: src/vm/*.c
	gcc src/vm/*.c -lm -lSDL2 -o bin/vm

autotest:
	source kidou && kidou test/bubble_sort.c
	source kidou && kidou test/fib.c
	source kidou && kidou test/sieve.c
	source kidou && kidou test/vec2.c
