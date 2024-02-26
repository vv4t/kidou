#include <stdio.h>

#include "vm.h"
#include "asm.h"
#include "table.h"

typedef enum {
  STATUS_NONE,
  STATUS_EXIT,
  STATUS_PRINT
} status_t;

int main(int argc, char *argv[])
{
  table_t table;
  table_init(&table);
  
  vm_t vm;
  vm_init(&vm);
  
  asm_load(&vm, &table, "code.kd");
  
  sym_t *sym = sym_find(&table, "main");
  
  if (!sym) {
    fprintf(stderr, "kidou: no entry point 'main' found.\n");
    return 1;
  }
  
  vm.status = STATUS_NONE;
  vm.ip = sym->pos;
  
  while (vm.status != STATUS_EXIT) {
    vm_exec(&vm);
    
    switch (vm.status) {
    case STATUS_PRINT:
      printf("> %i\n", vm_pop(&vm));
      break;
    }
  }
  
  vm_info(&vm);
  
  printf("status: %i\n", vm.status);
  
  return 0;
}
