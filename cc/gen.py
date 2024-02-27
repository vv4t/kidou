from parse import *

class Gen:
  def __init__(self, parse):
    self.parse = parse
    
    self.emit('main:')
    
    self.emit(f"enter {parse.scope.size // 4}")
    self.emit("")
    
    self.statement(parse.node)
    self.emit('int 2')
    
    self.emit("leave")
    self.emit('int 1')
  
  def statement(self, node):
    if isinstance(node, VarStatement):
      return
    elif isinstance(node, ExpressionStatement):
      self.expression(node.body)
      self.emit("")
    elif isinstance(node, CompoundStatement):
      for statement in node.body:
        self.statement(statement)
    else:
      raise Exception("unknown")
  
  def expression(self, node):
    if isinstance(node, ConstantNode):
      self.constant(node)
    elif isinstance(node, BinopNode):
      self.binop(node)
    elif islvalue(node):
      self.value(node)
  
  def value(self, node):
    self.lvalue(node)
    
    if sizeof(node.data_type) == 1:
      self.emit("lb")
    elif sizeof(node.data_type) == 4:
      self.emit("lw")
    else:
      raise Exception("unknown")
  
  def lvalue(self, node):
    if isinstance(node, NameNode):
      self.emit("fp")
      self.emit(f"const {node.var.pos}")
      self.emit("add")
    else:
      raise Exception("unknown")
  
  def binop(self, node):
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
    else:
      raise Exception("unknown")
  
  def constant(self, node):
    self.emit(f'const {node.value}')
  
  def emit(self, text):
    print(text)
