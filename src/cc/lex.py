import os
import re
from helper import find_match

class TokenError(Exception):
  def __init__(self, token, message):
    super().__init__(f'{token.src}:{token.line}: {message}')

class LexError(Exception):
  def __init__(self, src, line, message):
    super().__init__(f'{src}:{line}: {message}')

class Token:
  def __init__(self, token_type, text, line=0, src="None", value=0):
    self.token_type = token_type
    self.text = text
    self.line = line
    self.src = src
    self.value = value
  
  def __repr__(self):
    return self.text

class Lex:
  def __init__(self, src):
    file = open(src)
    text = file.read()
    file.close()
    
    self.stack_src = []
    self.src = src
    self.text = text
    self.define = {}
    
    self.macro_depth = 0
    self.macro_line = 0
    self.macro_src = src
    self.macro_type = ""

    self.token = None
    self.line = 1
    self.next()
  
  def next(self):
    while True:
      self.skip_whitespace()
      
      if self.preprocess():
        pass
      elif len(self.text) == 0:
        if len(self.stack_src) > 0:
          src, text, line = self.stack_src.pop()
          self.src = src
          self.text = text
          self.line = line
        else:
          if self.macro_depth > 0:
            raise LexError(self.macro_src, self.macro_line, f"unterminated {self.macro_type}")
          
          self.token = Token("EOF", "EOF", self.line, self.src)
          return self.token
      else:
        for name, value in self.define.items():
          if self.text.startswith(name):
            self.text = value + self.text[len(name):]
        break
    
    self.skip_whitespace()
    
    self.token = find_match([
      lambda : self.match_text(),
      lambda : self.match_number(),
      lambda : self.match_identifier(),
      lambda : self.match_symbol()
    ])
    
    if not self.token:
      print(f"skipping unknown character({self.text[0]})")
      self.text = self.text[1:]
      return self.next()
    
    self.text = self.text[len(self.token.text):]
    
    return self.token
  
  def preprocess(self):
    return find_match([
      lambda : self.pp_include(),
      lambda : self.pp_define(),
      lambda : self.pp_ifdef()
    ])
  
  def pp_ifdef(self):
    
    endif_match = re.match("^\s*#endif\s*$", self.text, flags=re.MULTILINE)
    ifdef_match = re.match("^\s*#ifdef ([a-zA-Z_][a-zA-Z0-9_]*)\s*$", self.text, flags=re.MULTILINE)
    ifndef_match = re.match("^\s*#ifndef ([a-zA-Z_][a-zA-Z0-9_]*)\s*$", self.text, flags=re.MULTILINE)
    
    if endif_match:
      self.macro_depth -= 1
      
      if self.macro_depth < 0:
        raise LexError(self.src, self.line, "#endif without if")
      
      self.eat_line()
      
    elif ifdef_match or ifndef_match:
      start_line = self.line
      macro_type = "#ifdef" if ifdef_match else "#ifndef"
      
      self.eat_line()
      
      name = (ifdef_match or ifndef_match).group(1)
      if ifdef_match and name not in self.define or ifndef_match and name in self.define:
        while not re.match("^\s*#endif\s*$", self.text, flags=re.MULTILINE):
          if not self.pp_ifdef():
            if not self.eat_line():
              raise LexError(self.src, start_line, f"unterminated {macro_type}")
        
        self.text = self.text.split('\n', 1)[1]
      else:
        self.macro_type = macro_type
        self.macro_line = self.line
        self.macro_src = self.src
        self.macro_depth += 1
    else:
      return False
    
    return True
  
  def pp_include(self):
    match = re.match("^\s*#include \"(.*?)\"$", self.text, flags=re.MULTILINE)
    
    if not match:
      return False
    else:
      self.eat_line()
    
    src = os.path.join(os.path.dirname(self.src), match.group(1))
    
    file = open(src)
    text = file.read()
    file.close()
    
    self.stack_src.append((self.src, self.text, self.line))
    
    self.src = src
    self.text = text
    self.line = 1
    
    return True
  
  def pp_define(self):
    match = re.match("^\s*#define ([a-zA-Z_][a-zA-Z0-9_]*) (.*?)$", self.text, flags=re.MULTILINE)
    
    if not match:
      return False
    else:
      self.eat_line()
    
    name = match.group(1)
    value = match.group(2)
    
    self.define[name] = value
    
    return True
  
  def match(self, token_type):
    if self.token == None:
      return None
    
    if self.token.token_type == token_type:
      return self.token
    
    return None
  
  def accept(self, token_type):
    if self.token == None:
      return None
    
    if self.match(token_type):
      return self.pop()
    
    return None
  
  def expect(self, token_type):
    if self.token == None or self.token.token_type != token_type:
      raise TokenError(self.token, f'expected \'{token_type}\' but found \'{self.token.text}\'')
    
    return self.accept(token_type)
  
  def pop(self):
    token = self.token
    self.next()
    return token
  
  def skip_whitespace(self):
    while re.match("^[ \t\n]", self.text):
      if self.text.startswith("\n"):
        self.line += 1
      
      self.text = self.text[1:]
  
  def match_identifier(self):
    match = re.match("^[a-zA-Z_][a-zA-Z0-9_]*", self.text)
    
    keyword = [
      "void",
      "int",
      "char",
      "if",
      "else",
      "while",
      "for",
      "print",
      "return",
      "struct",
      "printf"
    ]
    
    if match:
      if match.group() in keyword:
        return Token(match.group(), match.group(), self.line, self.src)
      
      return Token("Identifier", match.group(), self.line, self.src)
    
    return None
  
  def match_symbol(self):
    symbols = [
      "+=", "-=", "*=", "/=",
      "->", ",", ".",
      "(", ")", "[", "]", "{", "}",
      "||", "&&",
      "==", "!=",
      "<=", ">=", "<", ">",
      "=",
      "+", "-", "*", "/",
      "&",
      "'",
      ";", ":"
    ]
    
    for symbol in symbols:
      if self.text.startswith(symbol):
        return Token(symbol, symbol, self.line, self.src)
    
    return None
  
  def match_text(self):
    match = re.match("^\"(.*?)\"", self.text)
    
    if match:
      return Token("Text", match.group(), self.line, self.src, value=match.group(1))
    
    return None
  
  def match_number(self):
    match = re.match("^[0-9]+", self.text)
    
    if match:
      return Token("Number", match.group(), self.line, self.src, value=int(match.group()))
    
    match = re.match("^'(.*)'", self.text)
    
    if match:
      c = ord(match.group(1)[0])
      return Token("Number", match.group(), self.line, self.src, value=c)
    
    return None
  
  def eat_line(self):
    split = self.text.split('\n', 1)
    
    if len(split) <= 1:
      return False
    
    self.text = split[1]
    self.line += 1
    
    return True
