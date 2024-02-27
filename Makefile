.PHONY=default run

default: kidou run

kidou: src/*.c
	gcc src/*.c -o kidou

run:
	./kidou
