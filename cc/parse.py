from ast import *
from helper import find_match
from lex import TokenError

class Parse:
  def __init__(self, lex):
    self.lex = lex
    self.scope = Scope()
    self.node = self.function()
  
  def function(self):
    specifier = self.specifier()
    
    if not specifier:
      return None
    
    declarator = None
    
    while self.lex.accept('*'):
      declarator = Pointer(declarator)
    
    data_type = DataType(specifier, declarator)
    
    name = self.lex.expect("Identifier")
    
    self.lex.expect('(')
    param = self.param(self.scope)
    self.lex.expect(')')
    
    body = self.expect(self.compound_statement(), "compound-statement")
    
    return body
  
  def param(self, scope):
    param = []
    
    var = self.var(scope)
    
    if not var:
      return param
    
    param.append(var)
    
    while self.lex.accept(','):
      var = self.expect(self.var(scope), "parameter-declaration")
      param.append(var)
    
    for put_var in reversed(param):
      if not scope.insert_param(put_var):
        raise TokenError(self.lex.token, f"redefinition of '{put_var.name}'")
    
    return param
  
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
      return CompoundStatement([ self.expect(self.statement(), "statement") ])
  
  def statement(self):
    return find_match([
      lambda : self.var_statement(),
      lambda : self.expression_statement()
    ])
  
  def var_statement(self):
    var = self.var(self.scope)
    
    if not var:
      return None
    
    if not scope.insert(var):
      raise TokenError(self.lex.token, f"redefinition of '{var.name}'")
    
    self.lex.expect(';')
    
    return VarStatement(var)
  
  def expression_statement(self):
    expression = self.expression()
    
    if not expression:
      return None
    
    self.lex.expect(";")
    
    return ExpressionStatement(expression)
  
  def var(self, scope):
    specifier = self.specifier()
    
    if not specifier:
      return None
    
    var = self.declarator(specifier)
    
    if not var:
      if specifier.name != "struct":
        raise TokenError(self.lex.token, f"declaration does not declare anything")
      return True
    
    return var
  
  def declarator(self, specifier):
    declarator = None
    
    while self.lex.accept('*'):
      declarator = Pointer(declarator)
    
    if declarator:
      name = self.lex.expect("Identifier")
    elif self.lex.match("Identifier"):
      name = self.lex.pop()
    else:
      return None
    
    while self.lex.accept('['):
      size = self.lex.expect("Number")
      declarator = Array(declarator, int(size.text))
      self.lex.expect(']')
    
    data_type = DataType(specifier, declarator)
    
    if sizeof(data_type) == 0:
      raise TokenError(name, f"aggregate '{data_type} {name}' has incomplete type and cannot be defined") 
    
    return Var(data_type, name.text)
  
  def specifier(self):
    name = find_match([
      lambda : self.lex.accept("int"),
      lambda : self.lex.accept("char"),
      lambda : self.lex.accept("struct")
    ])
    
    if not name:
      return None
    
    struct_scope = None
    
    if name.text == "struct":
      struct_name = self.lex.expect("Identifier")
      struct_scope = self.scope.find_struct(struct_name.text)
      
      if not struct_scope:
        struct_scope = Scope(struct_name.text)
        self.scope.insert_struct(struct_scope)
      
      if self.lex.accept("{"):
        if struct_scope.size > 0:
          raise TokenError(struct_name, "redefinition of 'struct {struct_name}'")
        
        var = self.var(struct_scope)
        
        while var:
          self.lex.expect(';')
          struct_scope.insert(var)
          var = self.var(struct_scope)
        
        self.lex.expect("}")
    
    return Specifier(name.text, struct_scope)
  
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
      return self.unary()
    
    lhs = self.binop_set(set_num + 1)
    
    op = find_match([ (lambda y: (lambda : self.lex.accept(y)))(x) for x in op_set[set_num] ])
    
    if not op:
      return lhs
    
    rhs = self.binop_set(set_num)
    
    if not rhs:
      raise TokenError(op, f"expected 'expression' after '{op}' but found '{self.lex.token.text}'")
    
    if not valid_binop(lhs.data_type, op.text, rhs.data_type):
      raise TokenError(op, f"invalid '{op}' operation between '{lhs.data_type}' and '{rhs.data_type}'")
    
    if op.text == '=' and not islvalue(lhs):
      raise TokenError(op, f"cannot assign to non-lvalue '{lhs}'")
    
    return BinopNode(lhs, op.text, rhs, lhs.data_type)
  
  def unary(self):
    if self.lex.accept("&"):
      return self.address_of()
    elif self.lex.accept("*"):
      return self.dereference()
    else:
      return self.postfix()
  
  def dereference(self):
    base = self.expect(self.unary(), "unary-expression")
    
    if not ispointer(base.data_type):
      raise TokenError(self.lex.token, f"cannot dereference non-pointer '{base}'")
    
    return UnaryNode('*', base, data_type = base_type(base.data_type))
  
  def address_of(self):
    base = self.expect(self.unary(), "unary-expression")
    
    if not islvalue(base):
      raise TokenError(self.lex.token, f"lvalue required as unary '&' operand")
    
    return UnaryNode('&', base, pointer_type(base.data_type))
  
  def postfix(self):
    base = self.primitive()
    
    if not base:
      return None
    
    while True:
      if self.lex.match('['):
        base = self.index(base)
      if self.lex.match('.'):
        base = self.access(base)
      if self.lex.match('->'):
        base = self.access(base, direct=False)
      else:
        return base
  
  def access(self, base, direct=True):
    if direct:
      self.lex.expect(".")
    else:
      self.lex.expect("->")
      
    name = self.lex.expect("Identifier")
    
    if direct:
      if not isstruct(base.data_type):
        raise TokenError(name, f"request for '{name}' from '{base}', which is not a structure")
    else:
      if not ispointer(base.data_type) or not isstruct(base_type(base.data_type)):
        raise TokenError(name, f"indirect request for '{name}' from '{base}', which is not a structure pointer")
    
    struct_scope = base.data_type.specifier.struct_scope
    
    var = struct_scope.find(name.text)
    
    if not var:
      raise TokenError(name, f"'{base.data_type}' has no member named '{name}'")
    
    return AccessNode(base, var, direct, var.data_type)
  
  def index(self, base):
    if not isarray(base.data_type) and not ispointer(base.data_type):
      raise TokenError(self.lex.token, f"cannot index non-array and non-pointer '{base}'")
    
    self.lex.expect('[')
    pos = self.expect(self.expression(), "expression")
    self.lex.expect(']')
    
    return IndexNode(base, pos, base_type(base.data_type))
  
  def primitive(self):
    if self.lex.match("Number"):
      token = self.lex.pop()
      return ConstantNode(int(token.text), type_specifier("int"))
    
    if self.lex.match("Identifier"):
      token = self.lex.pop()
      return self.name(token)
    
    if self.lex.accept("("):
      body = self.expect(self.expression(), "expression")
      self.lex.expect(")")
      return body
    
    return None
  
  def name(self, token):
    var = self.scope.find(token.text)
    
    if not var:
      raise TokenError(token, f"name '{token.text}' is not defined")
    
    return NameNode(var, var.data_type)
  
  def expect(self, value, name):
    if not value:
      raise TokenError(self.lex.token, f"expected '{name}' but found '{self.lex.token}'")
    return value
