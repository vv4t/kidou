from lex import Lex, TokenError
from parse import Parse
from gen import Gen

try:
  lex = Lex("../test.code")
  parse = Parse(lex)
  gen = Gen(parse)
  
  f = open("../code.kd", "w")
  f.write(gen.text)
  f.close()
except TokenError as e:
  print(e)
