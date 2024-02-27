
class Scope:
  def __init__(self):
    self.size = 0
    self.var = {}
  
  def insert(self, var):
    if var.name in self.var:
      return False
    
    self.var[var.name] = var
    var.pos = self.size
    self.size += sizeof(var.data_type)
    
    return True
  
  def find(self, name):
    if name not in self.var:
      return None
    
    return self.var[name]

def islvalue(node):
  return isinstance(node, IdentifierNode)

def sizeof(data_type):
  specifier_size = { "int": 4, "char": 1 }
  
  if not data_type.declarator:
    return specifier_size[data_type.specifier]
  elif isinstance(data_type.declarator, Array):
    return declarator.size * sizeof(DataType(data_type.specifier, data_type.declarator.base))
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
  def __init__(self, lhs, op, rhs):
    self.lhs = lhs
    self.op = op
    self.rhs = rhs
  
  def __repr__(self):
    return f'({self.lhs}) {self.op} ({self.rhs})'

class ConstantNode:
  def __init__(self, value):
    self.value = value
  
  def __repr__(self):
    return str(self.value)

class IdentifierNode:
  def __init__(self, name):
    self.name = name
  
  def __repr__(self):
    return str(self.name)
