from ast import *
from helper import find_match
from lex import TokenError

class Parse:
  def __init__(self, lex):
    self.lex = lex
    self.context = Context()
    self.unit()
  
  def unit(self):
    match = self.external_declaration()
    
    while match:
      match = self.external_declaration()
    
    self.lex.expect("EOF")
  
  def external_declaration(self):
    var = self.var(self.context.scope_global)
    
    if not var:
      return None
    
    var.local = False
    
    if not isfunction(var.data_type):
      self.lex.expect(';')
      return var
    
    if self.lex.accept(';'):
      return var
    
    var.body = FunctionBody(Scope(param=var.data_type.declarator.scope_param, parent=self.context.scope_global))
    self.context.bind(var)
    var.body.body = self.expect(self.compound_statement(), "compound-statement")
    self.context.unbind()
    
    return var
  
  def compound_statement(self):
    if not self.lex.accept('{'):
      return None
    
    body = []
    statement = self.statement()
    
    while statement:
      body.append(statement)
      statement = self.statement()
    
    self.lex.expect('}')
    
    return CompoundStatement(body)
  
  def statement(self):
    return find_match([
      lambda : self.if_statement(),
      lambda : self.while_statement(),
      lambda : self.for_statement(),
      lambda : self.return_statement(),
      lambda : self.print_statement(),
      lambda : self.var_statement(),
      lambda : self.expression_statement(),
      lambda : self.compound_statement()
    ])
  
  def for_statement(self):
    if not self.lex.accept("for"):
      return None
    self.context.scope_fork()
    
    self.lex.expect("(")
    init = self.var_statement() or self.expression_statement() or self.lex.expect(';')
    condition = self.expect(self.expression(), "expression")
    self.lex.expect(';')
    step = self.expression()
    self.lex.expect(")")
    body = self.expect(self.compound_statement(), "for-statement-body")
    
    self.context.scope_join()
    
    node = ForStatement(init, condition, step, body)
    
    return node
  
  def while_statement(self):
    if not self.lex.accept("while"):
      return None
    
    self.lex.expect("(")
    condition = self.expect(self.expression(), "expression")
    self.lex.expect(")")
    
    self.context.scope_fork()
    body = self.expect(self.compound_statement(), "while-statement-body")
    self.context.scope_join()
    
    node = WhileStatement(condition, body)
    
    return node
  
  def if_statement(self):
    if not self.lex.accept("if"):
      return None
    
    self.lex.expect("(")
    condition = self.expect(self.expression(), "expression")
    self.lex.expect(")")
    
    self.context.scope_fork()
    body = self.expect(self.compound_statement(), "if-statement-body")
    self.context.scope_join()
    
    else_if = None
    
    if self.lex.accept("else"):
      else_if = self.if_statement() or self.expect(self.statement(), "else-statement")
    
    node = IfStatement(condition, body, else_if)
    
    return node
  
  def return_statement(self):
    if not self.lex.accept("return"):
      return None
    
    return_type = base_type(self.context.function.data_type)
    
    if self.lex.accept(';'):
      if return_type:
        raise TokenError(self.lex.token, f"return-statement with no value in function returning '{return_type}'")
      
      return ReturnStatement(None)
    else:
      body = self.expect(self.expression(), "expression")
      
      if not c_type_check(body.data_type, '=', return_type):
        raise TokenError(self.lex.token, f"incompatible expression type '{body.data_type}' for return type '{return_type}'")
      
      self.lex.expect(';')
      
      return ReturnStatement(body)
    
  def print_statement(self):
    if not self.lex.accept("printf"):
      return None
    
    arg = self.arg()
    self.lex.expect(';')
    
    return PrintStatement(arg)
  
  def var_statement(self):
    var = self.var(self.context.scope)
    
    if not var:
      return None
    
    self.lex.expect(';')
    
    return VarStatement(var)
  
  def expression_statement(self):
    expression = self.expression()
    
    if not expression:
      return None
    
    self.lex.expect(";")
    
    return ExpressionStatement(expression)
  
  def var(self, scope=None):
    specifier = self.specifier()
    
    if not specifier:
      return None
    
    var = self.declarator(specifier)
    
    if not var:
      if specifier.name != "struct":
        raise TokenError(self.lex.token, f"declaration does not declare anything")
      return Var(DataType(specifier, None), None)
    
    if isstruct(var.data_type) and sizeof(var.data_type) == 0:
      print(var.data_type)
      raise TokenError(self.lex.token, f"declaring '{var.name}' with incomplete type '{var.data_type}'")
    
    if isvoid(var.data_type):
      raise TokenError(self.lex.token, f"cannot declare void variable '{var.name}'")
    
    if scope and not scope.insert(var):
      raise TokenError(self.lex.token, f"redefinition of '{var.name}'")
    
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
    
    if self.lex.accept('('):
      param = self.param()
      self.lex.expect(')')
      
      scope_param = ScopeParam()
      
      for p in param:
        if self.context.scope.find(p) or not scope_param.insert(p):
          raise TokenError(self.lex.token, f"redefinition of '{p.name}'")
      
      declarator = FunctionType(declarator, param, scope_param)
    else:
      while self.lex.accept('['):
        size = self.lex.expect("Number")
        declarator = Array(declarator, size.value)
        self.lex.expect(']')
    
    data_type = DataType(specifier, declarator)
    
    var = Var(data_type, name.text)
    
    if self.lex.accept('='):
      value = self.expect(self.expression(), "expression")
      var.body = ExpressionStatement(self.binop_check(NameNode(var, var.data_type), '=', value))
    
    return var
  
  def param(self):
    param = []
    
    var = self.var()
    
    if not var:
      return param
    
    param.append(var)
    
    while self.lex.accept(','):
      var = self.expect(self.var(), "parameter-declaration")
      param.append(var)
    
    return param
  
  def specifier(self):
    name = find_match([
      lambda : self.lex.accept("int"),
      lambda : self.lex.accept("char"),
      lambda : self.lex.accept("void"),
      lambda : self.lex.accept("struct")
    ])
    
    if not name:
      return None
    
    struct_scope = None
    
    if name.text == "struct":
      struct_name = self.lex.expect("Identifier")
      struct_scope = self.context.scope.find_struct(struct_name.text)
      
      if not struct_scope:
        struct_scope = Scope(name=struct_name.text)
        self.context.scope.insert_struct(struct_name.text, struct_scope)
      
      if self.lex.accept("{"):
        if struct_scope.size > 0:
          raise TokenError(struct_name, "redefinition of 'struct {struct_name}'")
        
        var = self.var(struct_scope)
        
        while var:
          self.lex.expect(';')
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
      [ "||" ],
      [ "&&" ],
      [ "==", "!=" ],
      [ ">=", "<=", "<", ">" ],
      [ "+", "-" ],
      [ "*", "/" ]
    ]
    
    if set_num == len(op_set):
      return self.unary()
    
    lhs = self.binop_set(set_num + 1)
    
    op = find_match([ (lambda y: (lambda : self.lex.accept(y)))(x) for x in op_set[set_num] ])
    
    if op and op.text in op_set[0]:
      rhs = self.expect(self.binop_set(set_num), "expression")
      
      if len(op.text) > 1:
        rhs = self.binop_check(lhs, op.text[:-1], rhs)
      
      lhs = self.binop_check(lhs, '=', rhs)
    else:
      while op:
        if not op:
          return lhs
        
        rhs = self.expect(self.binop_set(set_num + 1), "expression")
        lhs = self.binop_check(lhs, op.text, rhs)
        
        op = find_match([ (lambda y: (lambda : self.lex.accept(y)))(x) for x in op_set[set_num] ])
    
    return lhs
  
  def binop_check(self, lhs, op, rhs):
    if not c_type_check(lhs.data_type, op, rhs.data_type):
      raise TokenError(self.lex.token, f"invalid '{op}' operation between '{lhs.data_type}' and '{rhs.data_type}'")
    
    if op == '=' and not islvalue(lhs):
      raise TokenError(self.lex.token, f"cannot assign to non-lvalue '{lhs}'")
    
    data_type = lhs.data_type
    
    return BinopNode(lhs, op, rhs, data_type)
  
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
      elif self.lex.match('('):
        return self.call(base)
      elif self.lex.match('.'):
        base = self.access(base, True)
      elif self.lex.match('->'):
        base = self.access(base, False)
      else:
        return base
  
  def access(self, base, direct):
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
    if self.lex.match("Text"):
      token = self.lex.pop()
      data_type = DataType(Specifier("char", None), Array(None, len(token.text)))
      return StringNode(token.value, data_type)
    
    if self.lex.match("Number"):
      token = self.lex.pop()
      return ConstantNode(token.value, type_specifier("int"))
    
    if self.lex.match("Identifier"):
      token = self.lex.pop()
      return self.name(token)
    
    if self.lex.accept("("):
      body = self.expect(self.expression(), "expression")
      self.lex.expect(")")
      return body
    
    return None
  
  def call(self, base):
    if not isfunction(base.data_type):
      raise TokenError(self.lex.token, f"cannot call non-function '{base}'")
    
    self.lex.expect("(")
    arg = self.arg()
    self.lex.expect(")")
    
    if len(arg) < len(base.data_type.declarator.param):
      raise TokenError(self.lex.token, f"too few arguments to function '{base}'")
    
    if len(arg) > len(base.data_type.declarator.param):
      raise TokenError(self.lex.token, f"too many arguments to function '{base}'")
    
    for a, b in zip(arg, base.data_type.declarator.param):
      if not c_type_check(a.data_type, '=', b.data_type):
        raise TokenError(self.lex.token, f"incompatible type for argument '{b.name}' of '{base}'") 
    
    return CallNode(base, arg, base_type(base.data_type))
  
  def arg(self):
    arg = []
    
    body = self.expression()
    
    if not body:
      return arg
    
    arg.append(body)
    
    while self.lex.accept(','):
      body = self.expect(self.expression(), "argument-expression")
      arg.append(body)
    
    return arg
  
  def name(self, token):
    var = self.context.scope.find(token.text)
    
    if not var:
      raise TokenError(token, f"name '{token.text}' is not defined")
    
    return NameNode(var, var.data_type)
  
  def expect(self, value, name):
    if not value:
      raise TokenError(self.lex.token, f"expected '{name}' but found '{self.lex.token}'")
    return value
