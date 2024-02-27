#include "asm.h"

#include <string.h>
#include <stdlib.h>
#include <common/file.h>

bool asm_load(vm_t *vm, table_t *table, const char *path)
{
  char *text = file_read_all(path);
  
  if (!text) {
    return false;
  }
  
  char *token = strtok(text, " \n");
  
  int ip = 0;
  
  while (token) {
    sym_t *sym = sym_find(table, token);
    
    if (sym) {
      vm->text[ip++] = sym->pos;
    } else if (token[strlen(token) - 1] == ':') {
      token[strlen(token) - 1] = 0;
      sym_insert(table, token, ip);
    } else {
      op_t op = text_op(token);
      vm->text[ip++] = op;
    }
    
    token = strtok(NULL, " \n");
  }
  
  free(text);
}

