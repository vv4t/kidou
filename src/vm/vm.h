#ifndef VM_H
#define VM_H

#include <stdbool.h>

typedef enum {
  VM_EXIT,
  VM_PRINTF,
} status_t;

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
  
  VM_FADD,
  VM_FSUB,
  VM_FMUL,
  VM_FDIV,
  
  VM_CVTSS2SI,
  VM_CVTSI2SS,
  
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
  
  int text_size;
  int data_size;
  char *va_arg;
  
  int text[1024];
  int stack[1024];
  
  bool debug;
} vm_t;

bool vm_file(vm_t *vm, const char *path);

void vm_printf(vm_t *vm);

void vm_return_int(vm_t *vm, int value);
void vm_return_float(vm_t *vm, float value);
int vm_arg_int(vm_t *vm);
float vm_arg_float(vm_t *vm);

bool vm_call(vm_t *vm, const char *name);
void vm_init(vm_t *vm);
int vm_exec(vm_t *vm);
void vm_info(vm_t *vm);

#endif
