#include "asm.h"

#include <string.h>
#include <stdlib.h>
#include "file.h"

bool asm_load(vm_t *vm, const char *path)
{
  char *text = file_read_all(path);
  
  if (!text) {
    return false;
  }
  
  char *token = strtok(text, " \n");
  
  int ip = 0;
  
  while (token) {
    op_t op = text_op(token);
    vm->text[ip++] = op;
    
    token = strtok(NULL, " \n");
  }
  
  free(text);
}

