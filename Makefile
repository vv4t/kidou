.PHONY=default run debug test

default: vm run

vm: src/vm/*.c
	gcc src/vm/*.c -o vm

run:
	./cc test/main.c
	./vm

debug:
	./cc test/main.c --dump
	./vm --debug

test:
	./kidou test/main.c
	./kidou test/bubble_sort.c
	./kidou test/fib.c
	./kidou test/sieve.c
	./kidou test/vec2.c
