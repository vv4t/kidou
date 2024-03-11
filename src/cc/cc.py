from lex import Lex, TokenError, LexError
from parse import Parse
from gen import Gen
import sys

try:
  if len(sys.argv) < 2:
    sys.exit(1)
  
  lex = Lex(sys.argv[1])
  parse = Parse(lex)
  gen = Gen(parse)
  
  f = open("a.out", "w")
  f.write(gen.text)
  f.close()
except (LexError, TokenError) as e:
  print(e)
