from parse import *

class Gen:
  def __init__(self, parse):
    self.parse = parse
    
    print(parse.node)
    self.emit('main:')
    
    self.emit(f"enter {parse.scope.size // 4}")
    
    self.statement(parse.node)
    self.emit('int 2')
    
    self.emit("leave")
    self.emit('int 1')
  
  def statement(self, node):
    if isinstance(node, ExpressionStatement):
      self.expression(node.body)
    elif isinstance(node, VarStatement):
      pass
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
      self.lvalue(node)
  
  def lvalue(self, node):
    if isinstance(node, IdentifierNode):
      var = self.parse.scope.find(node.name)
      print(var.pos)
  
  def binop(self, node):
    self.expression(node.lhs)
    self.expression(node.rhs)
    
    op_instr_table = {
      '+': 'add',
      '-': 'sub',
      '*': 'mul',
      '/': 'div'
    }
    
    self.emit(op_instr_table[node.op])
  
  def constant(self, node):
    self.emit(f'const {node.value}')
  
  def emit(self, text):
    print(text)
