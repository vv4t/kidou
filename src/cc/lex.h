#ifndef LEX_H
#define LEX_H

#include <stdbool.h>

typedef enum {
  TK_EOF = 256,
  
  TYPE_TOKEN_KEYWORD,
  TK_INT = TYPE_TOKEN_KEYWORD,
  TK_CHAR,
  TK_IF,
  TK_WHILE,
  TK_FOR,
  TK_RETURN,
  
  TYPE_TOKEN_SYMBOL,
  EQ_OP = TYPE_TOKEN_SYMBOL,
  NE_OP,
  LE_OP,
  GE_OP,
  TK_AND_OP,
  TK_OR_OP,
  
  TYPE_TOKEN_OBJECT,
  TK_NAME = TYPE_TOKEN_OBJECT,
  TK_CONSTANT,
  TK_TEXT,
  TYPE_TOKEN_UNKNOWN
} type_token_t;

typedef struct token_s {
  type_token_t type_token;
  char *text;
  struct token_s *next;
  const char *src;
  int line;
} token_t;

typedef struct {
  token_t *token;
  token_t *now;
} lex_t;

bool lex_parse_file(lex_t *lex, const char *path);
bool lex_match(lex_t *lex, type_token_t type_token);
token_t *lex_eat(lex_t *lex);
token_t *lex_accept(lex_t *lex, type_token_t type_token);
token_t *lex_expect(lex_t *lex, type_token_t type_token);
void lex_dump(lex_t *lex);

void print_token(const token_t *token);
void print_type_token(type_token_t type_token);

#endif
