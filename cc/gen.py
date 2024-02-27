from parse import *

class Gen:
  def __init__(self, parse):
    self.emit('main:')
    
    self.emit(f"enter {parse.scope.size // 4}")
    
    self.statement(parse.node)
    self.emit('int 2')
    
    self.emit("leave")
    self.emit('int 1')
  
  def statement(self, node):
    if isinstance(node, BodyStatement):
      if isinstance(node.body, Expression):
        self.expression(node.body)
    elif isinstance(node, CompoundStatement):
      for statement in node.body:
        self.statement(statement)
    else:
      raise Exception("unknown")
  
  def expression(self, node):
    if isinstance(node, ConstantNode):
      self.constant(node)
    elif isinstance(node, IdentifierNode):
      self.lvalue(node)
    elif isinstance(node, BinopNode):
      self.binop(node)
    elif isinstance(node, Expression):
      self.expression(node.body)
  
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
