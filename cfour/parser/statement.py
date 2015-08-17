"""statement.py

Contains parser and visitor mixins for statements.
"""


class Parser(object):

  def statement(self):
    if self.consume(';i'):
      return self.visitor.include(self.expect('char').value)
    elif self.consume(';v'):
      name = self.visitor.id(self.expect('id').value)
      type_ = self.type_expression()
      value = None
      if self.consume('='):
        value = self.expression()
      self.expect(';')
      return self.visitor.variable_declaration(name, type_, value)
    elif self.consume(';f'):
      name = self.visitor.id(self.expect('id').value)
      type_ = self.type_expression()
      body = self.statement()
      return self.visitor.function_definition(name, type_, body)
    elif self.consume(';s'):
      name = self.visitor.type_id(self.expect('id').value)
      bases = []
      while not self.at('{'):
        bases.append(self.type_expression())
      body = self.statement()
      return self.visitor.struct_definition(name, tuple(bases), body)
    elif self.consume(';t'):
      args = []
      while not self.at(';f', ';s'):
        args.append(self.visitor.type_id(self.expect('id').value))
      if self.at(';f'):
        return self.visitor.template_function_definition(tuple(args), self.statement())
      elif self.at(';s'):
        return self.visitor.template_struct_definition(tuple(args), self.statement())
      else:
        raise SyntaxError(self.peek)
    elif self.consume('{'):
      stmts = []
      while not self.consume('}'):
        stmts.append(self.statement())
      return self.visitor.block(tuple(stmts))
    else:
      expr = self.expression()
      self.expect(';')
      return self.visitor.expression_statement(expr)


class Visitor(object):

  def include(self, path):
    """Parser callback for include directives.

    Arguments:
      path(str): The path to include.

    Returns(statement):
      A user defined ast element that represents this include directive.
    """
    raise NotImplementedError()

  def variable_declaration(self, name, type_, value):
    """Parser callback for variable declarations.

    Arguments:
      name(expression): The identifier to be declared.
      type_(type_expression): The the type associated with this declaration.
      value(expresion|None): The value to initialize this declaration with, if one has been specified.

    Returns(statement):
      A user defined ast element that represents this variable declaration.
    """
    raise NotImplementedError()

  def function_definition(self, name, type_, body):
    """Parser callback for function definitions.

    Arguments:
      name(expression): The name of this function.
      type_(type_expression): This functions type.
      body(statement): The body of the function.

    Returns(statement):
      A user defined ast element that represents this function definition.
    """
    raise NotImplementedError()

  def block(self, statements):
    """Parser callback for '{' '}' delimited list of statements.

    Arguments:
      statements(tuple(statement)): The statements that this block consists of.

    Returns(statement):
      A user defined ast element that represents this statement block.
    """
    raise NotImplementedError()

  def expression_statement(self, expression):
    """Parser callback for expression statements.

    Arguments:
      expression(expression): The expression in this statement.

    Returns(statement):
      A user defined ast element that represents this expression statement.
    """
    raise NotImplementedError()

  def struct_definition(self, name, bases, body):
    """Parser callback for struct definitions.

    Arguments:
      name(expression): Struct identifier.
      bases(tuple(type_expression)): Bases for this inheritance.
      body(statement): Struct body.

    Returns(statement):
      A user defined ast element that represents this struct definition.

    C4 structs have some syntactic extensions that C structs don't.
    """
    raise NotImplementedError()

  def template_function_definition(self, arguments, function_definition):
    raise NotImplementedError()

  def template_struct_definition(self, arguments, struct_definition):
    raise NotImplementedError()
