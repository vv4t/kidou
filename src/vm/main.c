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
  
  vm_load_file(&vm, "a.out");
  vm_export_t *export_main = vm_find_export(&vm, "main");
  vm_call_export(&vm, export_main);
  
  return 0;
}
