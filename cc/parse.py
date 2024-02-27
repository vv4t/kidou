from ast import *
from helper import find_match
from lex import TokenError

class Scope:
  def __init__(self):
    self.size = 0
    self.var = {}
  
  def insert(self, var):
    if var.name in self.var:
      return False
    
    self.var[var.name] = var
    var.pos = self.size
    self.size += sizeof(var.data_type)
    
    return True

class Parse:
  def __init__(self, lex):
    self.lex = lex
    self.scope = Scope()
    self.node = self.compound_statement()
  
  def compound_statement(self):
    if self.lex.accept('{'):
      body = []
      statement = self.statement()
      
      while statement:
        body.append(statement)
        statement = self.statement()
      
      self.lex.expect('}')
      
      return CompoundStatement(body)
    else:
      return CompoundStatement([ self.statement() ])
  
  def statement(self):
    return find_match([
      lambda : self.var_statement(),
      lambda : self.expression_statement()
    ])
  
  def var_statement(self):
    var = self.var()
    
    if not var:
      return None
    
    self.lex.expect(';');
    
    return BodyStatement(var)
  
  def expression_statement(self):
    expression = self.expression()
    
    if not expression:
      return None
    
    self.lex.expect(";")
    
    return BodyStatement(Expression(expression))
  
  def var(self):
    specifier = self.specifier()
    
    if not specifier:
      return None
    
    declarator = None
    
    while self.lex.accept('*'):
      declarator = Pointer(declarator)
    
    name = self.lex.expect("Identifier")
    
    while self.lex.accept('['):
      size = self.lex.expect("Number")
      declarator = Array(declarator, int(size.text))
      self.lex.expect(']')
    
    data_type = DataType(specifier.text, declarator)
    
    var = Var(data_type, name.text)
    
    if not self.scope.insert(var):
      raise TokenError(name, f"redefinition of '{name}'")
    
    return var
  
  def specifier(self):
    return find_match([
      lambda : self.lex.accept('int'),
      lambda : self.lex.accept('char')
    ])
  
  def expression(self):
    return self.binop()
  
  def binop(self):
    return self.binop_set(0)
  
  def binop_set(self, set_num):
    op_set = [
      [ "+=", "-=", "*=", "/=", "=" ],
      [ "==", "!=" ],
      [ ">=", "<=", "<", ">" ],
      [ "+", "-" ],
      [ "*", "/" ]
    ]
    
    if set_num == len(op_set):
      return self.primitive()
    
    lhs = self.binop_set(set_num + 1)
    
    op = find_match([ (lambda y: (lambda : self.lex.accept(y)))(x) for x in op_set[set_num] ])
    
    if not op:
      return lhs
    
    rhs = self.binop_set(set_num)
    
    if not rhs:
      raise TokenError(op, f"expected 'expression' after '{op}' but found '{self.lex.token.text}'")
    
    return BinopNode(lhs, op.text, rhs)
  
  def primitive(self):
    if self.lex.match("Number"):
      token = self.lex.pop()
      return ConstantNode(int(token.text))
    
    if self.lex.match("Identifier"):
      token = self.lex.pop()
      return IdentifierNode(token.text)
    
    if self.lex.accept("("):
      body = self.expression()
      self.lex.expect(")")
      return Expression(body)
    
    return None

def sizeof(data_type):
  return sizeof_R(data_type.specifier, data_type.declarator)

def sizeof_R(specifier, declarator):
  specifier_size = { "int": 4, "char": 1 }
  
  if not declarator:
    return specifier_size[specifier]
  elif isinstance(declarator, Array):
    return declarator.size * sizeof_R(specifier, declarator.base)
  elif isinstance(declarator, Pointer):
    return specifier_size["int"]
  else:
    raise Exception("unknown")

def declarator_with_name(declarator, name):
  if not declarator:
    return name
  if isinstance(declarator, Array):
    return f"{declarator_with_name(declarator.base, name)}[{declarator.size}]"
  elif isinstance(declarator, Pointer):
    return f"*{declarator_with_name(declarator.base, name)}"
  else:
    return Exception("unknown")

class CompoundStatement:
  def __init__(self, body):
    self.body = body
  
  def __repr__(self, indent=0):
    pad1 = " " * indent
    pad2 = pad1 + "  "
    body = "\n".join([ statement.__repr__(indent=indent + 2) for statement in self.body ])
    return pad1 + "{\n" + body + "\n" + pad1 + "}"

class BodyStatement:
  def __init__(self, body):
    self.body = body
  
  def __repr__(self, indent=0):
    return " " * indent + str(self.body) + ";"

class Var:
  def __init__(self, data_type, name):
    self.pos = 0
    self.data_type = data_type
    self.name = name
  
  def __repr__(self):
    return f"{self.data_type.specifier} {declarator_with_name(self.data_type.declarator, self.name)}"

class DataType:
  def __init__(self, specifier, declarator):
    self.specifier = specifier
    self.declarator = declarator
  
  def __repr__(self):
    if self.declarator:
      return f"{self.specifier}{self.declarator}"
    else:
      return f"{self.specifier}"

class Pointer:
  def __init__(self, base):
    self.base = base
  
  def __repr__(self):
    if not self.base:
      return "*"
    else:
      return f"*{self.base}"

class Array:
  def __init__(self, base, size):
    self.base = base
    self.size = size
  
  def __repr__(self):
    if not self.base:
      return f"[{self.size}]"
    else:
      return f"{self.base}[{self.size}]"
    

class Expression:
  def __init__(self, body):
    self.body = body
  
  def __repr__(self):
    return f'({self.body})'

class BinopNode:
  def __init__(self, lhs, op, rhs):
    self.lhs = lhs
    self.op = op
    self.rhs = rhs
  
  def __repr__(self):
    return f'{self.lhs} {self.op} {self.rhs}'

class ConstantNode:
  def __init__(self, value):
    self.value = value
  
  def __repr__(self):
    return str(self.value)

class IdentifierNode:
  def __init__(self, name):
    self.name = name
  
  def __repr__(self):
    return str(self.name)
