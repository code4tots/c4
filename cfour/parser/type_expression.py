"""type_expression.py

Contains parser and visitor mixins for type_expressions.
"""


class Parser(object):

  def type_expression(self):
    if self.at('id'):
      return self.visitor.type_id(self.expect('id').value)
    elif self.consume('*'):
      return self.visitor.pointer_type(self.type_expression())
    elif self.consume('['):
      index = ''
      if self.at('int'):
        index = self.gettok().value
      self.expect(']')
      return self.visitor.array_type(self.type_expression(), index)
    elif self.consume('('):
      argnames = []
      argtypes = []
      while not self.consume(')'):
        argnames.append(self.visitor.id(self.expect('id').value))
        argtypes.append(self.type_expression())
        self.consume(',')
      returns = self.type_expression()
      return self.visitor.function_type(tuple(argnames), tuple(argtypes), returns)
    else:
      raise self.error('Expected type expression')


class Visitor(object):

  def type_id(self, value):
    raise NotImplementedError()

  def pointer_type(self, type_expression):
    raise NotImplementedError()

  def array_type(self, type_expression, index):
    raise NotImplementedError()

  def function_type(self, argument_names, argument_types, return_type):
    raise NotImplementedError()
