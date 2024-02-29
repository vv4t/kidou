import math
from parse import *

class Gen:
  def __init__(self, parse):
    self.parse = parse
    self.num_label = 0
    self.text = ""
    self.ip = 0
    self.label = {}
    self.current_function = None
    self.return_label = None
    
    self.emit('call program')
    self.emit('int 1')
    
    self.unit(parse.node)
    
    # self.dump()
    
    for label, pos in self.label.items():
      self.text = self.text.replace(label, str(pos))
  
  def dump(self):
    label_map = {}
    
    for k, v in self.label.items():
      if v not in label_map:
        label_map[v] = [k]
      else:
        label_map[v].append(k)
    
    ip = 0
    for line in self.text.split("\n"):
      if ip in label_map:
        line_label = '\n  '.join([ str(label) + ":" for label in label_map[ip] ])
        print(f"  {line_label}")
      
      print(ip, line)
      ip += 1 + line.count(" ")
  
  def unit(self, node):
    for function in node.function:
      self.function(function)
  
  def function(self, node):
    self.emit_label(node.name)
    self.emit(f'enter {math.ceil(node.scope.size / 4)}')
    
    self.current_function = node
    self.return_label = self.label_new()
    
    self.statement(node.body)
    self.emit_label(self.return_label)
    self.emit('leave')
    self.emit('ret')
    
    self.return_label = None
    self.current_function = None
  
  def statement(self, node):
    if isinstance(node, VarStatement):
      pass
    elif isinstance(node, PrintStatement):
      self.print(node)
    elif isinstance(node, IfStatement):
      self.if_statement(node)
    elif isinstance(node, ReturnStatement):
      self.return_statement(node)
    elif isinstance(node, ExpressionStatement):
      self.expression(node.body)
    elif isinstance(node, CompoundStatement):
      for statement in node.body:
        self.statement(statement)
    else:
      raise Exception("unknown")
  
  def if_statement(self, node):
    label_body = self.label_new()
    label_end = self.label_new()
    
    self.logical_or(node.condition, label_body, label_end)
    self.emit_label(label_body)
    self.statement(node.body)
    self.emit_label(label_end)
  
  def logical_or(self, node, label_body, label_end):
    if isinstance(node, BinopNode) and node.op == '||':
      label_next = self.label_new()
      self.logical_or(node.lhs, label_body, label_next)
      self.emit(f"jmp {label_body}")
      self.emit_label(label_next)
      self.logical_or(node.rhs, label_body, label_end)
    else:
      self.logical_and(node, label_end)
  
  def logical_and(self, node, label_end):
    if isinstance(node, BinopNode) and node.op == '&&':
      self.comparison(node.lhs, label_end)
      self.comparison(node.rhs, label_end)
    else:
      self.comparison(node, label_end)
  
  def comparison(self, node, label_end):
    if isinstance(node, BinopNode) and node.op in [ '>', '>=', '<', '<=', '==', '!=' ]:
      self.expression(node.lhs)
      self.expression(node.rhs)
      
      if node.op == ">":
        self.emit(f'jle {label_end}')
      elif node.op == ">=":
        self.emit(f'jlt {label_end}')
      elif node.op == "<":
        self.emit(f'jge {label_end}')
      elif node.op == "<=":
        self.emit(f'jgt {label_end}')
      elif node.op == "==":
        self.emit(f'jne {label_end}')
      elif node.op == "!=":
        self.emit(f'jeq {label_end}')
    else:
      self.expression(node)
      self.emit("const 0")
      self.emit(f"jeq {label_end}")
  
  def print(self, node):
    self.expression(node.body)
    
    if node.print_type == "print_int":
      self.emit("int 2")
    elif node.print_type == "print_char":
      self.emit("int 3")
    elif node.print_type == "print_string":
      self.emit("int 4")
    else:
      raise Exception("unknown")
  
  def return_statement(self, node):
    if node.body:
      self.expression(node.body)
      return_pos = -8 - self.current_function.scope.param_size - sizeof(self.current_function.data_type)
      self.emit("fp")
      self.emit(f"const {return_pos}")
      self.emit("add")
      
      if sizeof(self.current_function.data_type) <= 4:
        self.emit("sw")
      else:
        self.emit(f"store {sizeof(self.current_function.data_type) // 4}")
    
    self.emit(f"jmp {self.return_label}")
  
  def expression(self, node):
    if islvalue(node):
      self.value(node)
    elif isinstance(node, ConstantNode):
      self.constant(node)
    elif isinstance(node, BinopNode):
      self.binop(node)
    elif isinstance(node, UnaryNode):
      self.unary(node)
    elif isinstance(node, CallNode):
      self.call(node)
    else:
      raise Exception("unknown")
  
  def call(self, node):
    return_size = sizeof(node.function.data_type)
    
    if return_size > 0:
      self.emit(f"alloc {math.ceil(return_size / 4)}")
    
    for arg in node.arg:
      self.expression(arg)
    
    self.emit(f"call {node.function.name}")
    
    arg_size = math.ceil(node.function.scope.param_size / 4)
    if arg_size > 0:
      self.emit(f'free {arg_size}')
  
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
    if ispointer(node.base.data_type):
      self.value(node.base)
    elif isarray(node.base.data_type):
      self.lvalue(node.base)
    else:
      raise Exception("unknown")
    
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
  
  def label_new(self):
    self.num_label += 1
    return "." + str(self.num_label)
  
  def emit_label(self, label):
    if label in self.label:
      raise Exception(f"label redefinition '{label}'")
    
    self.label[label] = self.ip
  
  def emit(self, text):
    self.text += text + "\n"
    self.ip += 1 + text.count(" ")
