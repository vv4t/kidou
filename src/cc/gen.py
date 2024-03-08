import math
import sys
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
    self.ax = 0
    
    self.emit('call .main')
    self.emit('int 1')
  
    self.unit()
    
    if '--dump' in sys.argv:
      self.dump()
    
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
    
    for line in self.text.split("\n")[:-1]:
      if ip in label_map:
        line_label = '\n  '.join([ str(label) + ":" for label in label_map[ip] ])
        print(f"  {line_label}")
      
      print(hex(ip), line)
      
      ip += 1 + line.count(" ")
  
  def unit(self):
    for var in self.parse.context.scope_global.var.values():
      if isfunction(var.data_type):
        self.function(var)
  
  def function(self, node):
    self.current_function = node
    
    self.emit_label(f".{node.name}")
    self.emit(f'enter {math.ceil(node.body.scope.size / 4)}')
    
    self.current_function = node
    self.return_label = self.label_new()
    
    self.statement(node.body.body)
    self.emit_label(self.return_label)
    self.emit('leave')
    self.emit('ret')
    
    self.return_label = None
    self.current_function = None
  
  def statement(self, node):
    if isinstance(node, VarStatement):
      self.var_statement(node)
    elif isinstance(node, PrintStatement):
      self.print(node)
    elif isinstance(node, ForStatement):
      self.for_statement(node)
    elif isinstance(node, WhileStatement):
      self.while_statement(node)
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
    
    if self.ax > 0:
      self.emit(f"free {self.ax}")
      self.ax = 0
  
  def var_statement(self, node):
    if node.body.name and node.body.body:
      self.statement(node.body.body)
  
  def for_statement(self, node):
    label_condition = self.label_new()
    label_body = self.label_new()
    label_end = self.label_new()
    
    self.statement(node.init)
    
    self.emit_label(label_condition)
    if node.condition:
      self.condition(node.condition, label_body, label_end)
    
    self.emit_label(label_body)
    self.statement(node.body)
    
    if node.step:
      self.expression(node.step)
    
    self.emit(f"jmp {label_condition}")
    self.emit_label(label_end)
  
  def while_statement(self, node):
    label_condition = self.label_new()
    label_body = self.label_new()
    label_end = self.label_new()
    
    self.emit_label(label_condition)
    self.condition(node.condition, label_body, label_end)
    self.emit_label(label_body)
    self.statement(node.body)
    self.emit(f"jmp {label_condition}")
    self.emit_label(label_end)
  
  def if_statement(self, node, label_else_end=None):
    label_body = self.label_new()
    label_end = self.label_new() if not label_else_end else label_else_end
    
    if node.else_if:
      label_else = self.label_new()
    
    self.condition(node.condition, label_body, label_else)
    self.emit_label(label_body)
    self.statement(node.body)
    
    if node.else_if:
      self.emit(f"jmp {label_end}")
      self.emit_label(label_else)
      
      if isinstance(node.else_if, IfStatement):
        self.if_statement(node.else_if, label_else_end=label_end)
      else:
        self.statement(node.else_if)
    
    if not label_else_end:
      self.emit_label(label_end)
  
  def condition(self, node, label_body, label_end):
    self.logical_or(node, label_body, label_end)
  
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
      
      self.ax -= 2
    else:
      self.expression(node)
      
      self.emit("const 0")
      self.ax += 1
      
      self.emit(f"jeq {label_end}")
      self.ax -= 2
  
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
    
    self.ax -= 1
  
  def return_statement(self, node):
    if node.body:
      function_type = self.current_function.data_type
      param_size = function_type.declarator.scope_param.size 
      return_size = sizeof(base_type(function_type))
      
      self.expression(node.body)
      return_pos = -8 - param_size - return_size
      self.emit("fp")
      self.emit(f"const {return_pos}")
      self.emit("add")
      
      if return_size <= 4:
        self.emit("sw")
        self.ax -= 1
      else:
        self.emit(f"store {return_size // 4}")
        self.ax -= return_size // 4
    
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
    return_size = sizeof(base_type(node.base.data_type))
    
    if return_size > 0:
      self.emit(f"alloc {math.ceil(return_size / 4)}")
    
    for arg in node.arg:
      self.expression(arg)
    
    if isinstance(node.base, NameNode):
      self.emit(f"call .{node.base.var.name}")
    else:
      raise Exception("unknown")
    
    arg_size = math.ceil(node.base.data_type.declarator.scope_param.size / 4)
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
    
    self.ax -= 1
  
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
      
    self.ax += 1
  
  def binop(self, node):
    lhs_type = node.lhs.data_type
    rhs_type = node.rhs.data_type
    
    if node.op == '=':
      self.assign(node)
    elif node.op in [ '<', '>', '<=', '>=', '==', '!=', '&&', '||' ]:
      label_true = self.label_new()
      label_false = self.label_new()
      label_end = self.label_new()
      
      self.condition(node, label_true, label_false)
      self.emit_label(label_true)
      self.emit("const 1")
      self.emit(f"jmp {label_end}")
      self.emit_label(label_false)
      self.emit("const 0")
      self.emit_label(label_end)
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
      self.ax -= 2
  
  def assign(self, node):
    self.expression(node.rhs)
    self.lvalue(node.lhs)
    
    if sizeof(node.data_type) == 1:
      self.emit("sb")
      self.ax -= 2
    elif sizeof(node.data_type) == 4:
      self.emit("sw")
      self.ax -= 2
    elif isstruct(node.data_type):
      self.emit(f"store {sizeof(node.data_type) // 4}")
      self.ax -= sizeof(node.data_type) // 4
      self.ax -= 1
    else:
      raise Exception("unknown")
  
  def constant(self, node):
    self.emit(f'const {node.value}')
    self.ax += 1
  
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
