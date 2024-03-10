#ifndef VM_H
#define VM_H

#include <stdbool.h>

#define MAX_NAME 64
#define MAX_EXPORT 32

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
  char name[MAX_NAME];
  int pos;
} vm_export_t;

typedef struct {
  vm_export_t vm_export[MAX_EXPORT];
  int num_export;
  
  int sp;
  int fp;
  int ip;
  
  int status;
  int text_size;
  int data_size;
  
  int text[1024];
  int stack[1024];
  
  bool debug;
} vm_t;

bool vm_load_file(vm_t *vm, const char *path);
vm_export_t *vm_find_export(vm_t *vm, const char *name);
void vm_call_export(vm_t *vm, vm_export_t *vm_export);
void vm_init(vm_t *vm);
void vm_exec(vm_t *vm);
void vm_info(vm_t *vm);
int vm_pop(vm_t *vm);

const char *op_text(op_t op);
op_t text_op(char *text);

#endif
