.PHONY=default run

default: cc kidou run

kidou: src/vm/*.c
	gcc -Isrc src/common/*.c src/vm/*.c -o kidou

cc: src/cc/*.c
	gcc -Isrc src/common/*.c src/cc/*.c -o cc

run:
	./cc
