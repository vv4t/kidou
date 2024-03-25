#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "vm.h"
#include "sdl.h"

void sdl_f(vm_t *vm)
{
  int width = vm_arg_int(vm);
  int height = vm_arg_int(vm);
  
  sdl_window(width, height);
}

void rand_f(vm_t *vm)
{
  vm_return_int(vm, rand());
}

int main(int argc, char *argv[])
{
  if (argc < 2) {
    fprintf(stderr, "usage: %s <file> [--debug]\n", argv[0]);
    exit(1);
  }
  
  srand(time(NULL));
  
  static vm_t vm;
  vm_init(&vm);
  
  if (argc > 2 && strcmp(argv[2], "--debug") == 0) {
    vm.debug = true;
  }
  
  sdl_init(&vm);
  
  vm_syscall_bind(&vm, 1, sdl_f);
  vm_syscall_bind(&vm, 6, rand_f);
  
  if (!vm_file(&vm, argv[1])) {
    return 1;
  }
   
  vm_call(&vm, "main");
  
  while (sdl_exec());
  
  return 0;
}
