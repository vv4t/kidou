.PHONY=default run debug

default: vm run

vm: src/vm/*.c
	gcc src/vm/*.c -o vm

run:
	./cc test/main.c
	./vm a.out

debug:
	./cc test/main.c --dump
	./vm a.out --debug
