#ifndef VM_H
#define VM_H

#include <stdbool.h>

#define MAX_NAME 64
#define MAX_EXPORT 32
#define MAX_SYSCALL 16
#define MAX_STACK 4096
#define MAX_TEXT 4096

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

typedef struct vm_s vm_t;

typedef void (*vm_syscall_t)(vm_t *vm);

typedef struct vm_s {
  vm_syscall_t vm_syscall[MAX_SYSCALL];
  
  vm_export_t vm_export[MAX_EXPORT];
  int num_export;
  
  int sp;
  int fp;
  int ip;
  
  int text_size;
  int data_size;
  char *va_arg;
  
  int text[MAX_TEXT];
  int stack[MAX_STACK];
  
  bool debug;
} vm_t;

bool vm_file(vm_t *vm, const char *path);

void vm_return_int(vm_t *vm, int value);
void vm_return_float(vm_t *vm, float value);
float vm_arg_float(vm_t *vm);
int vm_arg_int(vm_t *vm);

void vm_syscall_bind(vm_t *vm, int status, vm_syscall_t vm_syscall);

bool vm_call(vm_t *vm, const char *name);
void vm_init(vm_t *vm);
void vm_info(vm_t *vm);

#endif
