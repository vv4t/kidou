#include <stdio.h>

#include <string.h>
#include "vm.h"

int main(int argc, char *argv[])
{
  vm_t vm;
  vm_init(&vm);
  
  for (int i = 0; i < argc; i++) {
    if (strcmp(argv[i], "--debug") == 0) {
      vm.debug = true;
    }
  }
  
  vm_file(&vm, "a.out");
  
  if (!vm_call(&vm, "main")) {
    return 1;
  }
  
  bool quit = false;
  
  while (!quit) {
    switch (vm_exec(&vm)) {
    case VM_EXIT:
      quit = true;
      break;
    case VM_PRINTF:
      vm_printf(&vm);
      break;
    case 2:
      printf("%i\n", vm_arg_int(&vm));
      vm_return_int(&vm, 3);
      break;
    }
  }
  
  return 0;
}
