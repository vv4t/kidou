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
  srand(time(NULL));
  
  static vm_t vm;
  vm_init(&vm);
  
  sdl_init(&vm);
  
  vm_syscall_bind(&vm, 1, sdl_f);
  vm_syscall_bind(&vm, 5, rand_f);
  
  if (!vm_file(&vm, "a.out")) {
    return 1;
  }
   
  vm_call(&vm, "main");
  
  while (sdl_exec());
  
  return 0;
}
