from . import ast


class CodeGeneratorVisitor(ast.Visitor):

  def __init__(self):
    self.c_code = ''

  def VisitInclude(self, node):
    self.c_code += '#include <%s>' % node.path

  def VisitFunctionDeclaration(self, node):
    self.c_code += node.type.Declaration(node.name)
    self.Visit(node.body)


class DeclarationGeneratorVisitor(ast.Visitor):

  def __init__(self):
    self.declaration = ''

  def VisitPointerType(self, node):
    self.declaration += '*'
