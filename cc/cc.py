from lex import Lex, TokenError
from parse import Parse
from gen import Gen

try:
  lex = Lex("../test.code")
  parse = Parse(lex)
  gen = Gen(parse)
except TokenError as e:
  print(e)
