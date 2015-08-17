"""expression.py

Contains parser and visitor mixins for expressions.
"""


class Parser(object):

  def expression(self):
    # c4 expressions are similar to C grammar, but is simplified a bit.
    return self._expression14()

  def _expression00(self):
    if self.at('id'):
      return self.visitor.id(self.expect('id').value)
    elif self.at('int'):
      return self.visitor.int(self.expect('int').value)
    elif self.at('float'):
      return self.visitor.float(self.expect('float').value)
    elif self.at('str'):
      return self.visitor.str(self.expect('str').value)
    elif self.at('char'):
      return self.visitor.char(self.expect('char').value)
    elif self.consume('('):
      expr = self.expression()
      self.expect(')')
      return self.visitor.parenthetical_expression(expr)
    else:
      raise self.error('Expected expression')

  def _expression01(self):
    expr = self._expression00()
    while True:
      if self.consume('('):
        args = []
        while not self.consume(')'):
          args.append(self.expression())
          self.consume(',')
        expr = self.visitor.function_call(expr, tuple(args))
      elif self.consume('['):
        index = self.expression()
        self.expect(']')
        expr = self.visitor.subscript(expr, index)
      elif self.at('++', '--'):
        expr = self.visitor.postfix_operation(expr, self.gettok().value)
      elif self.consume('.'):
        expr = self.visitor.member_access(expr, self.expect('id').value)
      elif self.consume('->'):
        expr = self.visitor.member_access_through_poniter(expr, self.expect('id').value)
      else:
        break
    return expr

  def _expression02(self):
    if self.at('++', '--', '+', '-', '!', '~', '*', '&'):
      op = self.gettok().type
      return self.visitor.prefix_operation(op, self._expression02())
    if self.consume(';sizeof'):
      return self.visitor.sizeof_expression(self.expression())
    if self.consume('sizeof'):
      self.expect('(')
      type_ = self.type_expression()
      self.expect(')')
      return self.visitor.sizeof_type(type_)
    return self._expression01()

  def _expression03(self):
    expr = self._expression02()
    while self.at('*', '/', '%'):
      op = self.gettok().type
      expr = self.visitor.binary_operation(expr, op, self._expression02())
    return expr

  def _expression04(self):
    expr = self._expression03()
    while self.at('+', '-'):
      op = self.gettok().type
      expr = self.visitor.binary_operation(expr, op, self._expression03())
    return expr

  def _expression05(self):
    expr = self._expression04()
    while self.at('<<', '>>'):
      op = self.gettok().type
      expr = self.visitor.binary_operation(expr, op, self._expression04())
    return expr

  def _expression06(self):
    expr = self._expression05()
    while self.at('<', '<=', '>', '>='):
      op = self.gettok().type
      expr = self.visitor.binary_operation(expr, op, self._expression05())
    return expr

  def _expression07(self):
    expr = self._expression06()
    while self.at('==', '!='):
      op = self.gettok().type
      expr = self.visitor.binary_operation(expr, op, self._expression06())
    return expr

  def _expression08(self):
    expr = self._expression07()
    while self.at('&'):
      op = self.gettok().type
      expr = self.visitor.binary_operation(expr, op, self._expression07())
    return expr

  def _expression09(self):
    expr = self._expression08()
    while self.at('^'):
      op = self.gettok().type
      expr = self.visitor.binary_operation(expr, op, self._expression08())
    return expr

  def _expression10(self):
    expr = self._expression09()
    while self.at('|'):
      op = self.gettok().type
      expr = self.visitor.binary_operation(expr, op, self._expression09())
    return expr

  def _expression11(self):
    expr = self._expression10()
    while self.at('&&'):
      op = self.gettok().type
      expr = self.visitor.binary_operation(expr, op, self._expression10())
    return expr

  def _expression12(self):
    expr = self._expression11()
    while self.at('||'):
      op = self.gettok().type
      expr = self.visitor.binary_operation(expr, op, self._expression11())
    return expr

  def _expression13(self):
    expr = self._expression12()
    while self.consume('?'):
      cond = self.expression()
      self.expect(':')
      expr = self.visitor.conditional_expression(expr, cond, self._expression12())
    return expr

  def _expression14(self):
    expr = self._expression13()
    while self.at('=', '+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '&=', '^=', '|='):
      op = self.gettok().type
      expr = self.visitor.binary_operation(expr, op, self._expression13())
    return expr


class Visitor(object):

  def id(self, value):
    """Parser callback for expression identifiers.

    Arguments:
      value(str): The identifier.

    Returns(expression):
      A user defined ast element that represents this identifier.

    Note that this method is not called for all id tokens.
    This method is called for identifiers that can stand as expressions.
    This means that type identifiers and the attribute names in member access do not invoke this method.
    For type identifiers, see type_expression.Visitor.type_id instead.
    Attribute names do not invoke this method since the attribute names themselves are not meant to be an expression.
    """
    raise NotImplementedError()

  def int(self, value):
    """Parser callback for integer literal expressions.

    Arguments:
      value(int): The integer value.

    Returns(expression):
      A user defined ast element that represents this integer.
    """
    raise NotImplementedError()

  def float(self, value):
    """Parser callback for float literal expressions.

    Arguments:
      value(float): The float value.

    Returns(expression):
      A user defined ast element that represents this float.
    """
    raise NotImplementedError()

  def str(self, value):
    raise NotImplementedError()

  def char(self, value):
    raise NotImplementedError()

  def parenthetical_expression(self, expression):
    raise NotImplementedError()

  def function_call(self, function, arguments):
    raise NotImplementedError()

  def subscript(self, subscriptable, index):
    raise NotImplementedError()

  def member_access(self, expression, attribute):
    raise NotImplementedError()

  def member_access_through_pointer(self, expression, attribute):
    raise NotImplementedError()

  def postfix_operation(self, expression, operator):
    raise NotImplementedError()

  def sizeof_expression(self, expression):
    raise NotImplementedError()

  def sizeof_type(self, type_):
    raise NotImplementedError()

  def prefix_operation(self, operator, expression):
    raise NotImplementedError()

  def binary_operation(self, left, operator, right):
    raise NotImplementedError()

  def conditional_expression(self, left, condition, right):
    raise NotImplementedError()
