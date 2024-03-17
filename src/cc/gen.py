import sys
from parse import *

class Gen:
  def __init__(self, parse):
    self.parse = parse
    self.num_label = 0
    self.text = ""
    self.ip = 0
    self.label = {}
    self.export = {}
    self.string_map = {}
    self.data = []
    self.current_function = None
    self.return_label = None
    self.ax = 0
  
    self.unit()
    
    if '--dump' in sys.argv:
      self.dump()
    
    for label, pos in self.label.items():
      self.text = self.text.replace(label, str(pos))
    
    self.emit_data()
    self.emit_export()
  
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
  
  def emit_data(self):
    size = 0
    
    text = f"{1 + len(self.string_map)}\n"
    text += f"space {self.parse.context.scope_global.size}\n"
    
    size += self.parse.context.scope_global.size
    
    for string, label in self.string_map.items():
      text += f"data {len(string)}\n"
      text += string
      text += "\n"
      self.text = self.text.replace(label, str(size))
      size = (size + 3) // 4
    
    self.text = text + self.text
  
  def emit_export(self):
    text = str(len(self.export)) + "\n"
    
    for key, value in self.export.items():
      text += f"{key} {value}\n"
    
    self.text = text + self.text
  
  def unit(self):
    for var in self.parse.context.scope_global.var.values():
      if isfunction(var.data_type) and not isinstance(var.body, int):
        self.function(var)
  
  def function(self, node):
    self.current_function = node
    
    self.export_label(node.name)
    self.emit_label(f".{node.name}")
    self.emit(f'enter {(node.body.scope.size + 3) // 4}')
    
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
      self.expression(node.body, output=False)
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
      self.expression(node.step, output=False)
    
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
    else:
      label_else = label_end
    
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
    arg_size = 0
    for arg in reversed(node.arg):
      self.expression(arg)
      arg_size += max(sizeof(arg.data_type), 4)
    
    self.emit("int 0")
    
    if arg_size > 0:
      self.emit(f'free {arg_size // 4}')
    
    self.ax -= arg_size // 4
  
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
  
  def expression(self, node, output=True):
    if islvalue(node):
      self.value(node, output)
    elif isinstance(node, ConstantNode):
      self.constant(node, output)
    elif isinstance(node, BinopNode):
      self.binop(node, output)
    elif isinstance(node, UnaryNode):
      self.unary(node, output)
    elif isinstance(node, CallNode):
      self.call(node, output)
    elif isinstance(node, CastNode):
      self.cast(node, output)
    else:
      raise Exception("unknown")
  
  def cast(self, node, output):
    self.expression(node.base, output)
    
    if output:
      if isint(node.data_type) and isfloat(node.base.data_type):
        self.emit("cvtss2si")
      elif isfloat(node.data_type) and isint(node.base.data_type):
        self.emit("cvtsi2ss")
  
  def call(self, node, output):
    return_type = base_type(node.base.data_type)
    
    if not isvoid(return_type):
      size = sizeof(return_type)
      self.emit(f"alloc {(size + 3) // 4}")
    
    for arg in reversed(node.arg):
      self.expression(arg)
    
    if isinstance(node.base, NameNode):
      if isinstance(node.base.var.body, int):
        self.emit(f"int {node.base.var.body}")
      else:
        self.emit(f"call .{node.base.var.name}")
    else:
      raise Exception("unknown")
    
    arg_size = (node.base.data_type.declarator.scope_param.size + 3) // 4
    if arg_size > 0:
      self.emit(f'free {arg_size}')
      self.ax -= arg_size
    
    if not output and not isvoid(return_type):
      self.emit(f"free {(sizeof(return_type) + 3) // 4}")
  
  def unary(self, node, output):
    if node.op == '&':
      self.lvalue(node.base, output)
    else:
      raise Exception("unknown")
  
  def value(self, node, output):
    self.lvalue(node, output)
    
    if output:
      if isarray(node.data_type):
        pass
      elif sizeof(node.data_type) == 1:
        self.emit("lb")
      elif sizeof(node.data_type) == 4:
        self.emit("lw")
      elif isstruct(node.data_type):
        self.emit(f"load {sizeof(node.data_type) // 4}")
      else:
        raise Exception("unknown")
  
  def lvalue(self, node, output):
    if isinstance(node, NameNode):
      self.name(node, output)
    elif isinstance(node, StringNode):
      self.string(node, output)
    elif isinstance(node, IndexNode):
      self.index(node, output)
    elif isinstance(node, AccessNode):
      self.access(node, output)
    elif isinstance(node, UnaryNode) and node.op == '*':
      self.expression(node.base, output)
    else:
      raise Exception("unknown")
  
  def index(self, node, output):
    if ispointer(node.base.data_type):
      self.value(node.base, output)
    elif isarray(node.base.data_type):
      self.lvalue(node.base, output)
    else:
      raise Exception("unknown")
    
    self.expression(node.pos, output)
      
    if output:
      size = sizeof(node.data_type)
      if size > 1:
        self.emit(f"const {size}")
        self.emit("mul")
      
      self.emit("add")
      
      self.ax -= 1
  
  def access(self, node, output):
    if node.direct:
      self.lvalue(node.base, output)
    else:
      self.value(node.base, output)
    
    if node.var.pos > 0 and output:
      self.emit(f"const {node.var.pos}")
      self.emit("add")
  
  def name(self, node, output):
    if not output:
      return
    
    if node.var.local:
      self.emit("fp")
      
      if node.var.pos != 0:
        self.emit(f"const {node.var.pos}")
        self.emit("add")
    else:
      self.emit(f"const {node.var.pos}")
      
    self.ax += 1
  
  def binop(self, node, output):
    lhs_type = node.lhs.data_type
    rhs_type = node.rhs.data_type
    
    if node.op == '=':
      self.assign(node, output)
    elif node.op in [ '<', '>', '<=', '>=', '==', '!=', '&&', '||' ]:
      self.conditional_expression(node, output)
    else:
      self.expression(node.lhs, output)
      self.expression(node.rhs, output)
      
      op_table = {
        '+': 'add',
        '-': 'sub',
        '*': 'mul',
        '/': 'div'
      }
      
      if output:
        op = op_table[node.op]
        
        if isfloat(node.data_type):
          op = "f" + op
        
        self.emit(op)
        self.ax -= 2
  
  def conditional_expression(self, output):
    if output:
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
      label_end = self.label_new()
      self.condition(node, label_end, label_end)
      self.emit_label(label_end)
  
  def assign(self, node, output):
    self.expression(node.rhs, True)
    self.lvalue(node.lhs, True)
    
    if sizeof(node.lhs.data_type) == 1:
      self.emit("sb")
      self.ax -= 2
    elif sizeof(node.lhs.data_type) == 4:
      self.emit("sw")
      self.ax -= 2
    elif isstruct(node.lhs.data_type):
      self.emit(f"store {sizeof(node.lhs.data_type) // 4}")
      self.ax -= sizeof(node.lhs.data_type) // 4
      self.ax -= 1
    else:
      raise Exception("unknown")
    
    if output:
      self.value(node.lhs, True)
  
  def string(self, node, output):
    if not output:
      return
    
    label = None
    
    if node.text in self.string_map:
      label = self.string_map[node.text]
    else:
      label = self.label_new()
      self.string_map[node.text] = label
    
    self.emit(f"const {label}")
    self.ax += 1
  
  def constant(self, node, output):
    if not output:
      return
    
    self.emit(f'const {node.value}')
    self.ax += 1
  
  def label_new(self):
    self.num_label += 1
    return f".{self.num_label}_"
  
  def export_label(self, label):
    if label in self.export:
      raise Exception(f"export redefinition '{label}'")
    
    self.export[label] = self.ip
  
  def emit_label(self, label):
    if label in self.label:
      raise Exception(f"label redefinition '{label}'")
    
    self.label[label] = self.ip
  
  def emit(self, text):
    self.text += text + "\n"
    self.ip += 1 + text.count(" ")
