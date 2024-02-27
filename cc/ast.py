import math

class Scope:
  def __init__(self, name=""):
    self.size = 0
    self.struct = {}
    self.var = {}
    self.name = name
  
  def insert_struct(self, struct_scope):
    if self.find_struct(struct_scope.name):
      return None
    
    self.struct[struct_scope.name] = struct_scope
  
  def find_struct(self, name):
    if name not in self.struct:
      return None
    
    return self.struct[name]
  
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
        (data_type_cmp(a, type_specifier("int")), data_type_cmp(b, type_specifier("int"))),
        (data_type_cmp(a, type_specifier("int")), data_type_cmp(b, type_specifier("char"))),
        (data_type_cmp(a, type_specifier("char")), data_type_cmp(b, type_specifier("char"))),
        (data_type_cmp(a, type_specifier("char")), data_type_cmp(b, type_specifier("int"))),
        (ispointer(a), ispointer(b))
      ]
    )
  ]
  
  for cmp_op, cmp_list in cmp_table:
    if op in cmp_op:
      for x, y in cmp_list:
        if x and y:
          return True
  
  return False

def islvalue(node):
  return (
    isinstance(node, NameNode) or
    isinstance(node, IndexNode) or
    (isinstance(node, UnaryNode) and node.op == '*')
  )

def ispointer(data_type):
  return isinstance(data_type.declarator, Pointer)

def isarray(data_type):
  return isinstance(data_type.declarator, Array)

def isstruct(data_type):
  return data_type.specifier.name == "struct"

def pointer_type(data_type):
  return DataType(data_type.specifier, Pointer(data_type.declarator))

def base_type(data_type):
  if not data_type.declarator:
    return data_type
  else:
    return DataType(data_type.specifier, data_type.declarator.base)

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
