#ifndef VM_H
#define VM_H

#include <stdbool.h>

typedef enum {
  VM_CONST,
  
  VM_FP,
  VM_SP,
  
  VM_ADD,
  VM_SUB,
  VM_MUL,
  VM_DIV,
  
  VM_LW,
  VM_SW,
  VM_LB,
  VM_SB,
  VM_LOAD,
  VM_STORE,
  
  VM_AND,
  VM_OR,
  
  VM_NOT,
  VM_XOR,
  VM_NEG,
  
  VM_LSH,
  VM_RSH,
  
  VM_JMP,
  VM_JLT,
  VM_JGT,
  VM_JLE,
  VM_JGE,
  VM_JEQ,
  VM_JNE,
  
  VM_ALLOC,
  VM_FREE,
  
  VM_ENTER,
  VM_LEAVE,
  
  VM_CALL,
  VM_RET,
  
  VM_INT
} op_t;

typedef struct {
  int sp;
  int fp;
  int ip;
  
  int status;
  
  int text[128];
  int stack[128];
  
  bool debug;
} vm_t;

void vm_init(vm_t *vm);
void vm_exec(vm_t *vm);
void vm_info(vm_t *vm);
bool vm_asm(vm_t *vm, const char *path);
int vm_pop(vm_t *vm);

const char *op_text(op_t op);
op_t text_op(char *text);

#endif
