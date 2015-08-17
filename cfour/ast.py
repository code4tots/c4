"""ast.py

Most of the code here is boilerplate.
I put this here outside of the parser since I wanted to manipulate ast without feeling too much like I was tied to the parser.
Perhaps this could be done better without duplication like this?

Currently much of the code here should mirror what is in the parser.

However, possibly in the future, there may be a superset of nodes here that are not in the parser (i.e. intermedite/generated nodes)
"""

"""About exec.

So I could have meddled in Ast.__init__.
But I think that way would've been less readable and more code.

Actually writing out __init__ in all the subclasses would've definitely been more code.
Maybe it's that my editor tricks is not good enough.
Repeating patterns with a variable number of lines is kind of hard one for me with sublime.
"""

from . import parser

INIT_TEMPLATE = """
def __init__(self, %s):
%s
"""

class AstMetaclass(type):

  def __new__(mcs, name, bases, dict_):

    if 'attributes' in dict_:
      attributes = dict_['attributes']

      argument_list = ', '.join(attributes)
      assignments = ''.join('  self.%s = %s\n' % (attr, attr) for attr in attributes)
      exec(INIT_TEMPLATE % (argument_list, assignments))
      dict_['__init__'] = __init__

    return super(AstMetaclass, mcs).__new__(mcs, name, bases, dict_)


BaseAst = AstMetaclass('BaseAst', (object,), dict())


class Ast(BaseAst):

  def __repr__(self):
    attributes = ', '.join(map(repr, (getattr(self, attr) for attr in self.attributes)))
    return '%s(%s)' % (type(self).__name__, attributes)

  def __eq__(self, other):
    return type(self) == type(other) and all(getattr(self, attr) == getattr(other, attr) for attr in self.attributes)


class Expression(Ast):
  pass


class Id(Expression):
  attributes = ('value',)


class Int(Expression):
  attributes = ('value',)


class Float(Expression):
  attributes = ('value',)


class Str(Expression):
  attributes = ('value',)


class Char(Expression):
  attributes = ('value',)


class ParentheticalExpression(Expression):
  attributes = ('expression',)


class FunctionCall(Expression):
  attributes = ('function', 'arguments',)


class Subscript(Expression):
  attributes = ('subscriptable', 'index',)


class MemberAccess(Expression):
  attributes = ('expression', 'attribute',)


class MemberAccessThroughPointer(Expression):
  attributes = ('expression', 'attribute',)


class PostfixOperation(Expression):
  attributes = ('expression', 'operator',)


class SizeofExpression(Expression):
  attributes = ('expression',)


class SizeofType(Expression):
  attributes = ('type',)


class PrefixOperation(Expression):
  attributes = ('operator', 'expression',)


class BinaryOperation(Expression):
  attributes = ('left', 'operator', 'right',)


class ConditionalExpression(Expression):
  attributes = ('left', 'condition', 'right',)


class Statement(Ast):
  pass


class Include(Statement):
  attributes = ('path')


class VariableDeclaration(Statement):
  attributes = ('name', 'type', 'value')


class FunctionDefinition(Statement):
  attributes = ('name', 'type', 'body')


class Block(Statement):
  attributes = ('statements')


class ExpressionStatement(Statement):
  attributes = ('expression')


class StructDefinition(Statement):
  attributes = ('name', 'bases', 'body')


class TemplateFunctionDefinition(Statement):
  attributes = ('arguments', 'function_definition')


class TemplateStructDefinition(Statement):
  attributes = ('arguments', 'struct_definition')


class Type(Ast):
  pass


class TypeID(Type):
  attributes = ('value',)


class PointerType(Type):
  attributes = ('type_expression',)


class ArrayType(Type):
  attributes = ('type_expression', 'index',)


class FunctionType(Type):
  attributes = ('argument_names', 'argument_types', 'return_type',)


class AstBuilder(parser.Visitor):
  """Visitor for creating an unannotated version of the syntax tree."""

  # expressions

  def id(self, value):
    return ID(value)

  def int(self, value):
    return Int(value)

  def float(self, value):
    return Float(value)

  def str(self, value):
    return Str(value)

  def char(self, value):
    return Char(value)

  def parenthetical_expression(self, expression):
    return ParentheticalExpression(expression)

  def function_call(self, function, arguments):
    return FunctionCall(function, arguments)

  def subscript(self, subscriptable, index):
    return Subscript(subscriptable, index)

  def member_access(self, expression, attribute):
    return MemberAccess(expression, attribute)

  def member_access_through_pointer(self, expression, attribute):
    return MemberAccessThroughPointer(expression, attribute)

  def postfix_operation(self, expression, operator):
    return PostfixOperation(expression, operator)

  def sizeof_expression(self, expression):
    return SizeofExpression(expression)

  def sizeof_type(self, type_):
    return SizeofType(type_)

  def prefix_operation(self, operator, expression):
    return PrefixOperation(operator, expression)

  def binary_operation(self, left, operator, right):
    return BinaryOperation(left, operator, right)

  def conditional_expression(self, left, condition, right):
    return ConditionalExpression(left, condition, right)

  # statements

  def include(self, path):
    return Include(path)

  def variable_declaration(self, name, type_, value):
    return VariableDeclaration(name, type_, value)

  def function_definition(self, name, type_, body):
    return FunctionDefinition(name, type_, body)

  def block(self, statements):
    return Block(statements)

  def expression_statement(self, expression):
    return ExpressionStatement(expression)

  def struct_definition(self, name, bases, body):
    return StructDefinition(name, bases, body)

  def template_function_definition(self, arguments, function_definition):
    return TemplateFunctionDefinition(arguments, function_definition)

  def template_struct_definition(self, arguments, struct_definition):
    return TemplateStructDefinition(arguments, struct_definition)

  # types

  def type_id(self, value):
    return TypeID(value)

  def pointer_type(self, type_expression):
    return PointerType(type_expression)

  def array_type(self, type_expression, index):
    return ArrayType(type_expression, index)

  def function_type(self, argument_names, argument_types, return_type):
    return FunctionType(argument_names, argument_types, return_type)

### Everything above this line could probably be autogenerated from the parser code.

