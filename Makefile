.PHONY=default run

default: kidou run

kidou: vm/*.c
	gcc vm/*.c -o kidou

run:
	./kidou
