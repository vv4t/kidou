from ast import *
from helper import find_match
from lex import TokenError

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
    
    return VarStatement(var)
  
  def expression_statement(self):
    expression = self.expression()
    
    if not expression:
      return None
    
    self.lex.expect(";")
    
    return ExpressionStatement(expression)
  
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
      lambda : self.lex.accept("int"),
      lambda : self.lex.accept("char")
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
    
    if not valid_binop(lhs.data_type, op.text, rhs.data_type):
      raise TokenError(op, f"invalid '{op}' operation between '{lhs.data_type}' and '{rhs.data_type}'")
    
    return BinopNode(lhs, op.text, rhs, lhs.data_type)
  
  def primitive(self):
    if self.lex.match("Number"):
      token = self.lex.pop()
      return ConstantNode(int(token.text), DataType("int", None))
    
    if self.lex.match("Identifier"):
      token = self.lex.pop()
      return self.name(token)
    
    if self.lex.accept("("):
      body = self.expression()
      self.lex.expect(")")
      return body
    
    return None
  
  def name(self, token):
    var = self.scope.find(token.text)
    
    if not var:
      raise TokenError(token, f"name '{token.text}' is not defined")
    
    return NameNode(var, var.data_type)
