#include <stdio.h>

#include <string.h>
#include "vm.h"
#include "asm.h"

typedef enum {
  STATUS_NONE,
  STATUS_EXIT,
  STATUS_PRINT_INT,
  STATUS_PRINT_CHAR,
  STATUS_PRINT_STRING
} status_t;

int main(int argc, char *argv[])
{
  vm_t vm;
  vm_init(&vm);
  
  for (int i = 0; i < argc; i++) {
    if (strcmp(argv[i], "--debug") == 0) {
      vm.debug = true;
    }
  }
  
  asm_load(&vm, ".tmp");
  
  vm.status = STATUS_NONE;
  vm.ip = 0;
  
  while (vm.status != STATUS_EXIT) {
    vm_exec(&vm);
    
    switch (vm.status) {
    case STATUS_PRINT_INT:
      printf("> %i\n", vm_pop(&vm));
      break;
    case STATUS_PRINT_CHAR:
      printf("> %c\n", vm_pop(&vm));
      break;
    case STATUS_PRINT_STRING:
      printf("> %s\n", &((char*) vm.stack)[vm_pop(&vm)]);
      break;
    }
  }
  
  return 0;
}
