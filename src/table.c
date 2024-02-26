#include "table.h"

#include <string.h>
#include <stdlib.h>

void table_init(table_t *table)
{
  table->num_sym = 0;
}

sym_t *sym_find(table_t *table, const char *name)
{
  for (int i = 0; i < table->num_sym; i++) {
    if (strcmp(name, table->sym[i].name) == 0) {
      return &table->sym[i];
    }
  }
  
  return NULL;
}

void sym_insert(table_t *table, const char *name, int pos)
{
  sym_t *sym = &table->sym[table->num_sym++];
  sym->name = strdup(name);
  sym->pos = pos;
}

void table_free(table_t *table)
{
  for (int i = 0; i < table->num_sym; i++) {
    free(table->sym[i].name);
  }
}
