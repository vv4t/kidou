import math

def sizeof(data_type):
  specifier_size = { "int": 4, "char": 1 }
  
  if not data_type.declarator:
    if isstruct(data_type):
      return data_type.specifier.struct_scope.size
    
    return specifier_size[data_type.specifier.name]
  elif isinstance(data_type.declarator, Array):
    return data_type.declarator.size * sizeof(DataType(data_type.specifier, data_type.declarator.base))
  elif isinstance(data_type.declarator, Pointer):
    return specifier_size["int"]
  else:
    raise Exception("unknown")

def c_type_check(a, op, b):
  check = False
  
  check = not isstruct(a) and not isstruct(b) 
  
  if not check and op == '=':
    check = isstruct(a) and isstruct(b) and a.specifier.struct_scope == b.specifier.struct_scope
  
  return check

def islvalue(node):
  return (
    isinstance(node, NameNode) or
    isinstance(node, IndexNode) or
    isinstance(node, AccessNode) or
    (isinstance(node, UnaryNode) and node.op == '*')
  )

def isfunction(data_type):
  return isinstance(data_type.declarator, FunctionType)

def ispointer(data_type):
  return isinstance(data_type.declarator, Pointer)

def isarray(data_type):
  return isinstance(data_type.declarator, Array)

def isstruct(data_type):
  return data_type.specifier.name == "struct" and not data_type.declarator

def pointer_type(data_type):
  return DataType(data_type.specifier, Pointer(data_type.declarator))

def base_type(data_type):
  if not data_type.declarator:
    return data_type
  else:
    return DataType(data_type.specifier, data_type.declarator.base)

def declarator_with_name(declarator, name):
  if not declarator:
    return name
  if isinstance(declarator, Array):
    return f"{declarator_with_name(declarator.base, name)}[{declarator.size}]"
  elif isinstance(declarator, FunctionType):
    return f"{declarator_with_name(declarator.base, name)}" + "(" + ", ".join([ str(p) for p in declarator.param ]) + ")"
  elif isinstance(declarator, Pointer):
    return f"*{declarator_with_name(declarator.base, name)}"
  else:
    return Exception("unknown")

def data_type_cmp(a, b):
  if not a.declarator and not b.declarator:
    return specifier_type_cmp(a.specifier, b.specifier)
  elif not a.declarator:
    return False
  elif not b.declarator:
    return False
  elif type(a.declarator) == type(b.declarator):
    return data_type_cmp(DataType(a.specifier, a.declarator.base), DataType(b.specifier, b.declarator.base))

def specifier_type_cmp(a, b):
  if a.name == b.name:
    if a.name == "struct":
      return a.struct_scope == b.struct_scope
    else:
      return True
  else:
    return False

def type_specifier(specifier, struct_name=""):
  return DataType(Specifier(specifier, struct_name), None)

class Unit:
  def __init__(self, function):
    self.function = function
  
  def __repr__(self, indent=0):
    return (" " * indent + "\n").join([ function.__repr__(indent=indent+2) for function in self.function ])

class ReturnStatement:
  def __init__(self, body):
    self.body = body
  
  def __repr__(self, indent=0):
    return " " * indent + f"return {self.body}"

class PrintStatement:
  def __init__(self, print_type, body):
    self.print_type = print_type
    self.body = body
  
  def __repr__(self, indent=0):
    return " " * indent + f"{self.print_type} {self.body}"

class IfStatement:
  def __init__(self, condition, body):
    self.condition = condition
    self.body = body
  
  def __repr__(self, indent=0):
    body = f"\n{self.body.__repr__(indent=indent)}"
    return " " * indent + f"if ({self.condition}){body}"

class CompoundStatement:
  def __init__(self, body):
    self.body = body
  
  def __repr__(self, indent=0):
    pad1 = " " * indent
    pad2 = pad1 + "  "
    body = "\n".join([ statement.__repr__(indent=indent + 2) for statement in self.body ])
    return pad1 + "{\n" + body + "\n" + pad1 + "}"

class VarStatement:
  def __init__(self, body):
    self.body = body
  
  def __repr__(self, indent=0):
    return " " * indent + str(self.body) + ";"

class ExpressionStatement:
  def __init__(self, body):
    self.body = body
  
  def __repr__(self, indent=0):
    return " " * indent + str(self.body) + ";"

class FunctionBody:
  def __init__(self, scope):
    self.scope = scope
    self.body = None

class Var:
  def __init__(self, data_type, name):
    self.pos = 0
    self.data_type = data_type
    self.name = name
    self.body = None
  
  def __repr__(self):
    return f"{self.data_type.specifier} {declarator_with_name(self.data_type.declarator, self.name)}"

class DataType:
  def __init__(self, specifier, declarator=None):
    self.specifier = specifier
    self.declarator = declarator
  
  def __repr__(self):
    if self.declarator:
      return f"{self.specifier}{self.declarator}"
    else:
      return f"{self.specifier}"

class Specifier:
  def __init__(self, name, struct_scope=None):
    self.name = name
    self.struct_scope = struct_scope
  
  def __repr__(self):
    if self.name == "struct":
      return f"{self.name} {self.struct_scope.name}"
    else:
      return f"{self.name}"

class FunctionType:
  def __init__(self, base, param, scope_param):
    self.base = base
    self.param = param
    self.scope_param = scope_param
  
  def __repr__(self, indent=0, show_body=True):
    param = "(" + ", ".join([ str(p) for p in self.param ]) + ")"
    base = str(self.base) if self.base else ""
    return f"{base}{param}"

class Pointer:
  def __init__(self, base):
    self.base = base
  
  def __repr__(self):
    if not self.base:
      return "*"
    else:
      return f"*{self.base}"

class Array:
  def __init__(self, base, size):
    self.base = base
    self.size = size
  
  def __repr__(self):
    if not self.base:
      return f"[{self.size}]"
    else:
      return f"{self.base}[{self.size}]"

class BinopNode:
  def __init__(self, lhs, op, rhs, data_type):
    self.lhs = lhs
    self.op = op
    self.rhs = rhs
    self.data_type = data_type
  
  def __repr__(self):
    return f'({self.lhs}) {self.op} ({self.rhs})'

class UnaryNode:
  def __init__(self, op, base, data_type):
    self.op = op
    self.base = base
    self.data_type = data_type
  
  def __repr__(self):
    return f'{self.op}{self.base}'

class IndexNode:
  def __init__(self, base, pos, data_type):
    self.base = base
    self.pos = pos
    self.data_type = data_type
  
  def __repr__(self):
    return f'{self.base}[{self.pos}]'

class AccessNode:
  def __init__(self, base, var, direct, data_type):
    self.base = base
    self.var = var
    self.direct = direct
    self.data_type = data_type
  
  def __repr__(self):
    return f'{self.base}.{self.var.name}'

class CallNode:
  def __init__(self, base, arg, data_type):
    self.base = base
    self.arg = arg
    self.data_type = data_type
  
  def __repr__(self):
    arg = "(" + ", ".join([ str(a) for a in self.arg ]) + ")"
    return f"{base}{arg}"

class ConstantNode:
  def __init__(self, value, data_type):
    self.value = value
    self.data_type = data_type
  
  def __repr__(self):
    return str(self.value)

class NameNode:
  def __init__(self, var, data_type):
    self.var = var
    self.data_type = data_type
  
  def __repr__(self):
    return self.var.name
