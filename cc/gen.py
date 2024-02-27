from parse import *

class Gen:
  def __init__(self, parse):
    self.parse = parse
    
    self.emit('program:')
    
    self.emit(f'enter {parse.scope.size // 4}')
    
    self.statement(parse.node)
    self.emit('int 2')
    
    self.emit('leave')
    self.emit('ret')
    
    self.emit('main:')
    self.emit('enter 1')
    self.emit('const 5')
    self.emit('const 6')
    self.emit('const 7')
    self.emit('call program')
    self.emit('leave 1')
    self.emit('int 1')
  
  def statement(self, node):
    if isinstance(node, VarStatement):
      return
    elif isinstance(node, ExpressionStatement):
      self.expression(node.body)
    elif isinstance(node, CompoundStatement):
      for statement in node.body:
        self.statement(statement)
    else:
      raise Exception("unknown")
  
  def expression(self, node):
    if islvalue(node):
      self.value(node)
    elif isinstance(node, ConstantNode):
      self.constant(node)
    elif isinstance(node, BinopNode):
      self.binop(node)
    elif isinstance(node, UnaryNode):
      self.unary(node)
    else:
      raise Exception("unknown")
  
  def unary(self, node):
    if node.op == '&':
      self.lvalue(node.base)
    else:
      raise Exception("unknown")
  
  def value(self, node):
    self.lvalue(node)
    
    if sizeof(node.data_type) == 1:
      self.emit("lb")
    elif sizeof(node.data_type) == 4:
      self.emit("lw")
    elif isstruct(node.data_type):
      self.emit(f"load {sizeof(node.data_type) // 4}")
    else:
      raise Exception("unknown")
  
  def lvalue(self, node):
    if isinstance(node, NameNode):
      self.name(node)
    elif isinstance(node, IndexNode):
      self.index(node)
    elif isinstance(node, AccessNode):
      self.access(node)
    elif isinstance(node, UnaryNode) and node.op == '*':
      self.expression(node.base)
    else:
      raise Exception("unknown")
  
  def index(self, node):
    self.lvalue(node.base)
    self.expression(node.pos)
    
    size = sizeof(node.data_type)
    
    if size > 1:
      self.emit(f"const {size}")
      self.emit("mul")
    
    self.emit("add")
  
  def access(self, node):
    if node.direct:
      self.lvalue(node.base)
    else:
      self.value(node.base)
    
    if node.var.pos > 0:
      self.emit(f"const {node.var.pos}")
      self.emit("add")
  
  def name(self, node):
    self.emit("fp")
    
    if node.var.pos != 0:
      self.emit(f"const {node.var.pos}")
      self.emit("add")
  
  def binop(self, node):
    lhs_type = node.lhs.data_type
    rhs_type = node.rhs.data_type
    
    if node.op == '=':
      self.assign(node)
    else:
      self.expression(node.lhs)
      self.expression(node.rhs)
      
      op_instr_table = {
        '+': 'add',
        '-': 'sub',
        '*': 'mul',
        '/': 'div'
      }
      
      self.emit(op_instr_table[node.op])
  
  def assign(self, node):
    self.expression(node.rhs)
    self.lvalue(node.lhs)
    
    if sizeof(node.data_type) == 1:
      self.emit("sb")
    elif sizeof(node.data_type) == 4:
      self.emit("sw")
    elif isstruct(node.data_type):
      self.emit(f"store {sizeof(node.data_type) // 4}")
    else:
      raise Exception("unknown")
  
  def constant(self, node):
    self.emit(f'const {node.value}')
  
  def emit(self, text):
    print(text)
