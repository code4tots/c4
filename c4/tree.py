

class Tree(object):
  def __init__(self, *args):
    for attr, arg in zip(self.attributes, args):
      setattr(self, attr, arg)


class Include(Tree):

  attributes = ['path']

  def str(self):
    return '#include <%s>\n' % self.path


class VariableDeclaration(Tree):

  attributes = ['name', 'type', 'value']

  def str(self, depth=0):
    return '\t' * depth + self.type.Declare(self.name) + ' = ' self.value.str() + ';\n'


class FunctionDeclaration(Tree):

  attributes = ['name', 'type']

  def str(self):
    return self.type.Declare(self.name) + ';\n'


class FunctionDefinition(Tree):

  attributes = ['name', 'type', 'body']

  def str(self):
    return self.type.Declare(self.name) + self.body.str(0)
