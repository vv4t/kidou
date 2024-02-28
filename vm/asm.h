#ifndef CODE_H
#define CODE_H

#include "vm.h"
#include "table.h" 
#include <stdbool.h>

bool asm_load(vm_t *vm, table_t *table, const char *path);

#endif
