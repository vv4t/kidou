.PHONY=default run

default: vm run

vm: src/vm/*.c
	gcc src/vm/*.c -o vm

run:
	./kidou
