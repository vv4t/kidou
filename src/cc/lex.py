import re
from helper import find_match

class TokenError(Exception):
  def __init__(self, token, message):
    super().__init__(f'{token.src}:{token.line}: {message}')

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
    
    self.src = src
    self.text = text
    self.token = None
    self.line = 1
    self.next()
  
  def next(self):
    self.skip_whitespace()
    
    if len(self.text) == 0:
      self.token = Token("EOF", "EOF", self.line, self.src)
      return None
    
    self.token = find_match([
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
    while re.search("^[ \t\n]", self.text):
      if self.text.startswith("\n"):
        self.line += 1
      
      self.text = self.text[1:]
  
  def match_identifier(self):
    match = re.search("^[a-zA-Z_][a-zA-Z0-9_]*", self.text)
    
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
      "print_int",
      "print_char",
      "print_string"
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
  
  def match_number(self):
    match = re.search("^[0-9]+", self.text)
    
    if match:
      return Token("Number", match.group(), self.line, self.src, value=int(match.group()))
    
    match = re.search("^'(.*)'", self.text)
    
    if match:
      c = ord(match.group(1)[0])
      return Token("Number", match.group(), self.line, self.src, value=c)
    
    return None
