#include <stdio.h>

#include "lex.h"

int main(int argc, char *argv[])
{
  lex_t lex;
  
  if (!lex_parse_file(&lex, "test.code")) {
    return false;
  }
  
  lex_dump(&lex);
  
  return 0;
}
