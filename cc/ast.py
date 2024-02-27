import math

class Scope:
  def __init__(self):
    self.size = 0
    self.var = {}
  
  def insert(self, var):
    if var.name in self.var:
      return False
    
    size = sizeof(var.data_type)
    align = min(size, 4)
    
    self.var[var.name] = var
    self.size = math.ceil(self.size / align) * align
    var.pos = self.size
    self.size += size
    
    return True
  
  def find(self, name):
    if name not in self.var:
      return None
    
    return self.var[name]

def valid_binop(a, op, b):
  cmp_table = [
    (
      ['+', '-', '*', '/', '=' ],
      [
        (DataType("int", None), DataType("int", None))
      ]
    )
  ]
  
  for cmp_op, cmp_list in cmp_table:
    if op in cmp_op:
      for x,y in cmp_list:
        if data_type_cmp(a, x) and data_type_cmp(b, x):
          return True
  
  return False

def islvalue(node):
  return isinstance(node, NameNode)

def sizeof(data_type):
  specifier_size = { "int": 4, "char": 1 }
  
  if not data_type.declarator:
    return specifier_size[data_type.specifier]
  elif isinstance(data_type.declarator, Array):
    return data_type.declarator.size * sizeof(DataType(data_type.specifier, data_type.declarator.base))
  elif isinstance(data_type.declarator, Pointer):
    return specifier_size["int"]
  else:
    raise Exception("unknown")

def declarator_with_name(declarator, name):
  if not declarator:
    return name
  if isinstance(declarator, Array):
    return f"{declarator_with_name(declarator.base, name)}[{declarator.size}]"
  elif isinstance(declarator, Pointer):
    return f"*{declarator_with_name(declarator.base, name)}"
  else:
    return Exception("unknown")

def data_type_cmp(a, b):
  if not a.declarator and not b.declarator:
    return a.specifier == b.specifier
  elif not a.declarator:
    return False
  elif not b.declarator:
    return False
  elif type(a.declarator) == type(b.declarator):
    return data_type_cmp(DataType(a.specifier, a.declarator.base), DataType(b.specifier, b.declarator.base))

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

class Var:
  def __init__(self, data_type, name):
    self.pos = 0
    self.data_type = data_type
    self.name = name
  
  def __repr__(self):
    return f"{self.data_type.specifier} {declarator_with_name(self.data_type.declarator, self.name)}"

class DataType:
  def __init__(self, specifier, declarator):
    self.specifier = specifier
    self.declarator = declarator
  
  def __repr__(self):
    if self.declarator:
      return f"{self.specifier}{self.declarator}"
    else:
      return f"{self.specifier}"

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
