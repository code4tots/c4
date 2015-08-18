from .ast import *

class Builder(object):
  """Parser visitor for creating an unannotated version of the syntax tree."""

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
