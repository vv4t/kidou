.PHONY=default

default: kidou-vm

kidou-vm: src/vm/*.c
	gcc src/vm/*.c -lm -lSDL2 -o kidou-vm
