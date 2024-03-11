from lex import Lex, TokenError, LexError
from parse import Parse
from gen import Gen
import sys
import os

try:
  if len(sys.argv) < 2:
    print(f"usage: {sys.argv[0]} <file> [--dump]")
    sys.exit(1)
  
  if not os.path.isfile(sys.argv[1]):
    print(f"error: No such file '{sys.argv[1]}'")
    sys.exit(1)
  
  lex = Lex(sys.argv[1])
  parse = Parse(lex)
  gen = Gen(parse)
  
  f = open("a.out", "w")
  f.write(gen.text)
  f.close()
except (LexError, TokenError) as e:
  print(e)
  sys.exit(1)
