#include "vm.h"

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

vm_export_t *vm_find(vm_t *vm, const char *name);
op_t vm_next(vm_t *vm);
void vm_push(vm_t *vm, int n);
int vm_pop(vm_t *vm);
void vm_load(vm_t *vm, int a, int b);
void vm_store(vm_t *vm, int a, int b);
op_t text_op(char *text);
const char *op_text(op_t op);

void vm_init(vm_t *vm)
{
  vm->sp = -1;
  vm->ip = 0;
  vm->debug = false;
  
  memset(vm->stack, 0, sizeof(vm->stack));
}

bool vm_file(vm_t *vm, const char *path)
{
  FILE *file = fopen(path, "rb");
  
  if (!file) {
    perror(path);
    return false;
  }
  
  char word[256];
  
  if (!fscanf(file, "%i", &vm->num_export)) goto vm_load_file_ERROR;
  
  for (int i = 0; i < vm->num_export; i++) {
    if (!fscanf(file, "%255s", vm->vm_export[i].name)) goto vm_load_file_ERROR;
    if (!fscanf(file, "%i", &vm->vm_export[i].pos)) goto vm_load_file_ERROR;
  }
  
  int num_data;
  if (!fscanf(file, "%i", &num_data)) goto vm_load_file_ERROR;
  
  for (int i = 0; i < num_data; i++) {
    if (!fscanf(file, "%255s", word)) goto vm_load_file_ERROR;
    
    if (strcmp(word, "space") == 0) {
      int size;
      if (!fscanf(file, "%i", &size)) goto vm_load_file_ERROR;
      vm->sp += (size + 4) / 4;
    } else if (strcmp(word, "data") == 0) {
      int size;
      if (!fscanf(file, "%i", &size)) goto vm_load_file_ERROR;
      
      fgetc(file);
      char *text = (char*) &vm->stack[vm->sp];
      
      for (int i = 0; i < size; i++) {
        text[i] = fgetc(file);
      }
      
      text[size] = 0;
      vm->sp += (size + 4) / 4;
    } else {
      goto vm_load_file_ERROR;
    }
  }
  
  vm->data_size = vm->sp;
  vm->fp = vm->sp;
  
  vm->ip = 0;
  
  while (fscanf(file, "%255s", word) == 1) {
    op_t op = text_op(word);
    vm->text[vm->ip++] = op;
  }
  
  vm->text_size = vm->ip;
  vm->text[vm->ip++] = VM_INT;
  vm->text[vm->ip++] = VM_EXIT;
  
  return true;
vm_load_file_ERROR:
  fclose(file);
  return false;
}

void vm_printf(vm_t *vm)
{
  char *stack = (char*) vm->stack;
  char *va_arg = (char*) &vm->stack[vm->sp];
  
  char *format = &stack[*((int*) va_arg)];
  va_arg -= 4;
  
  char *c = format;
  
  printf("> ");
  
  while (*c) {
    if (*c == '%') {
      c++;
      switch (*c) {
      case 'i':
        printf("%i", *((int*) va_arg));
        va_arg -= 4;
        break;
      case 'f':
        printf("%f", *((float*) va_arg));
        va_arg -= 4;
        break;
      case 's':
        printf("%s", &stack[*((int*) va_arg)]);
        va_arg -= 4;
        break;
      default:
        putc('%', stdout);
        putc(*c, stdout);
        break;
      }
      
      c++;
    } else {
      putc(*c++, stdout);
    }
  }
  
  putc('\n', stdout);
}

bool vm_call(vm_t *vm, const char *name)
{
  vm_export_t *vm_export = vm_find(vm, name);
  
  if (!vm_export) {
    return false;
  }
  
  vm_push(vm, vm->text_size);
  vm->ip = vm_export->pos;
  
  return true;
}

vm_export_t *vm_find(vm_t *vm, const char *name)
{
  for (int i = 0; i < vm->num_export; i++) {
    if (strcmp(vm->vm_export[i].name, name) == 0) {
      return &vm->vm_export[i];
    }
  }
  
  return NULL;
}

void vm_info(vm_t *vm)
{
  printf("[ $ip=0x%03x, $sp=%i, $fp=%i ]\n", vm->ip, vm->sp, vm->fp);
  
  int row = 4;
  int col = 8;
  
  for (int i = 0; i < row; i++) {
    printf(" 0x%03x - ", i * col);
    for (int j = 0; j < col; j++) {
      if (i * col + j == vm->sp) {
        printf("(%08x)", vm->stack[i * col + j]);
      } else {
        printf(" %08x ", vm->stack[i * col + j]);
      }
    }
    printf("\n");
  }
}

int vm_exec(vm_t *vm)
{
  int a;
  int b;
  int c;
  
  float x;
  
  while (1) {
    op_t op = vm_next(vm);
    
    switch (op) {
    case VM_CONST:
      vm_push(vm, vm_next(vm));
      break;
    case VM_FP:
      vm_push(vm, vm->fp * 4);
      break;
    case VM_SP:
      vm_push(vm, vm->sp * 4);
      break;
    case VM_ADD:
      b = vm_pop(vm);
      a = vm_pop(vm);
      vm_push(vm, a + b);
      break;
    case VM_SUB:
      b = vm_pop(vm);
      a = vm_pop(vm);
      vm_push(vm, a - b);
      break;
    case VM_MUL:
      b = vm_pop(vm);
      a = vm_pop(vm);
      vm_push(vm, a * b);
      break;
    case VM_DIV:
      b = vm_pop(vm);
      a = vm_pop(vm);
      vm_push(vm, a / b);
      break;
    case VM_FADD:
      b = vm_pop(vm);
      a = vm_pop(vm);
      x = *((float*) &a) + *((float*) &b);
      vm_push(vm, *((int*) &x));
      break;
    case VM_FSUB:
      b = vm_pop(vm);
      a = vm_pop(vm);
      x = *((float*) &a) - *((float*) &b);
      vm_push(vm, *((int*) &x));
      break;
    case VM_FMUL:
      b = vm_pop(vm);
      a = vm_pop(vm);
      x = *((float*) &a) * *((float*) &b);
      vm_push(vm, *((int*) &x));
      break;
    case VM_FDIV:
      b = vm_pop(vm);
      a = vm_pop(vm);
      x = *((float*) &a) / *((float*) &b);
      vm_push(vm, *((int*) &x));
      break;
    case VM_CVTSS2SI:
      a = vm_pop(vm);
      x = *((float*) &a);
      a = x;
      vm_push(vm, a);
      break;
    case VM_CVTSI2SS:
      a = vm_pop(vm);
      x = a;
      vm_push(vm, *((int*) &x));
      break;
    case VM_LW:
      a = vm_pop(vm);
      vm_push(vm, vm->stack[a / 4]);
      break;
    case VM_SW:
      b = vm_pop(vm);
      a = vm_pop(vm);
      vm->stack[b / 4] = a;
      break;
    case VM_LB:
      a = vm_pop(vm);
      vm_push(vm, ((char*) vm->stack)[a]);
      break;
    case VM_SB:
      b = vm_pop(vm);
      a = vm_pop(vm);
      ((char*) vm->stack)[b] = a & 0xff;
      break;
    case VM_LOAD:
      a = vm_pop(vm);
      b = vm_next(vm);
      vm_load(vm, a, b);
      break;
    case VM_STORE:
      a = vm_pop(vm);
      b = vm_next(vm);
      vm_store(vm, a, b);
      break;
    case VM_AND:
      b = vm_pop(vm);
      a = vm_pop(vm);
      vm_push(vm, a & b);
      break;
    case VM_OR:
      b = vm_pop(vm);
      a = vm_pop(vm);
      vm_push(vm, a | b);
      break;
    case VM_NOT:
      a = vm_pop(vm);
      vm_push(vm, ~a);
      break;
    case VM_XOR:
      b = vm_pop(vm);
      a = vm_pop(vm);
      vm_push(vm, a ^ b);
      break;
    case VM_LSH:
      b = vm_pop(vm);
      a = vm_pop(vm);
      vm_push(vm, a << b);
      break;
    case VM_RSH:
      b = vm_pop(vm);
      a = vm_pop(vm);
      vm_push(vm, a >> b);
      break;
    case VM_JMP:
      a = vm_next(vm);
      vm->ip = a;
      break;
    case VM_JLT:
      b = vm_pop(vm);
      a = vm_pop(vm);
      c = vm_next(vm);
      if (a < b) vm->ip = c;
      break;
    case VM_JGT:
      b = vm_pop(vm);
      a = vm_pop(vm);
      c = vm_next(vm);
      if (a > b) vm->ip = c;
      break;
    case VM_JLE:
      b = vm_pop(vm);
      a = vm_pop(vm);
      c = vm_next(vm);
      if (a <= b) vm->ip = c;
      break;
    case VM_JGE:
      b = vm_pop(vm);
      a = vm_pop(vm);
      c = vm_next(vm);
      if (a >= b) vm->ip = c;
      break;
    case VM_JEQ:
      b = vm_pop(vm);
      a = vm_pop(vm);
      c = vm_next(vm);
      if (a == b) vm->ip = c;
      break;
    case VM_JNE:
      b = vm_pop(vm);
      a = vm_pop(vm);
      c = vm_next(vm);
      if (a != b) vm->ip = c;
      break;
    case VM_ALLOC:
      a = vm_next(vm);
      vm->sp += a;
      break;
    case VM_FREE:
      a = vm_next(vm);
      vm->sp -= a;
      break;
    case VM_CALL:
      a = vm_next(vm);
      vm_push(vm, vm->ip);
      vm->ip = a;
      break;
    case VM_RET:
      a = vm_pop(vm);
      vm->ip = a;
      break;
    case VM_ENTER:
      a = vm_next(vm);
      vm_push(vm, vm->fp);
      vm->fp = vm->sp + 1;
      vm->sp += a;
      break;
    case VM_LEAVE:
      vm->sp = vm->fp - 1;
      a = vm_pop(vm);
      vm->fp = a;
      break;
    case VM_INT:
      return vm_next(vm);
    }
    
    if (vm->debug) {
      printf(".%s\n", op_text(op));
      vm_info(vm);
      getchar();
    }
  }
}

op_t vm_next(vm_t *vm)
{
  return vm->text[vm->ip++];
}

void vm_push(vm_t *vm, int n)
{
  vm->stack[++vm->sp] = n;
}

int vm_pop(vm_t *vm)
{
  return vm->stack[vm->sp--];
}

void vm_load(vm_t *vm, int a, int b)
{
  for (int i = 0; i < b; i++) {
    vm_push(vm, vm->stack[a / 4 + i]);
  }
}

void vm_store(vm_t *vm, int a, int b)
{
  for (int i = 0; i < b; i++) {
    vm->stack[a / 4 + b - i - 1] = vm_pop(vm);
  }
}

const char *op_text(op_t op)
{
  const char *text[] = {
    "const",
    "fp",
    "sp",
    "add",
    "sub",
    "mul",
    "div",
    "fadd",
    "fsub",
    "fmul",
    "fdiv",
    "cvtss2si",
    "cvtsi2ss",
    "lw",
    "sw",
    "lb",
    "sb",
    "load",
    "store",
    "and",
    "or",
    "not",
    "xor",
    "lsh",
    "rsh",
    "jmp",
    "jlt",
    "jgt",
    "jle",
    "jge",
    "jeq",
    "jne",
    "alloc",
    "free",
    "enter",
    "leave",
    "call",
    "ret",
    "int"
  };
  
  return text[op];
}

op_t text_op(char *text)
{
  for (op_t i = 0; i <= VM_INT; i++) {
    if (strcmp(op_text(i), text) == 0) {
      return i;
    }
  }
  
  char *endptr;
  
  int result1 = strtol(text, &endptr, 10);
  if (*endptr == '\0') {
    return result1;
  }
  
  float result2 = strtof(text, &endptr);
  if (*endptr == '\0') {
    return *((int*) &result2);
  }
  
  return 0;
}
