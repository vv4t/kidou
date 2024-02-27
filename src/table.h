#ifndef SYM_H
#define SYM_H

typedef struct {
  char *name;
  int pos;
} sym_t;

typedef struct {
  sym_t sym[64];
  int num_sym;
} table_t;

void table_init(table_t *table);
void table_free(table_t *table);

sym_t *sym_find(table_t *table, const char *name);
void sym_insert(table_t *table, const char *name, int pos);

#endif
