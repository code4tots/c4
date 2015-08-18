"""ast.py

There are four kinds of tree nodes:

  1. Module
      - In every parsed program, there is always one Module, and it is always at the root.
      - Uses the 'str' property to generate C code.
  2. Expression
      - Uses the 'str' property to generate C code.
  3. Statement
      - Uses the 'Str(depth)' method to generate C code at the given indentation depth.
  4. Type
      - Uses the 'Declare(declarator)' and 'EmptyDeclare()' methods to generate C code.

Not all tree nodes have have a method/property for generating C code.
Some nodes, like the TemplateFunctionDefinition, are removed by the transformer before the tree is ready to generate C code.

Not all tree nodes are generated by the parser.
Some nodes, like FunctionDeclaration, are inserted by the transformer to make code generation easier.
"""

# Tab is two spaces because I says so.
# If you want to change this, you're going to have to modify the tests too.
TAB = '  '


def SanitizeCharacter(c):
  return ('\\n'  if c == '\n' else
          '\\t'  if c == '\t' else
          '\\\\' if c == '\\' else
          '\\\"' if c == '\"' else
          '\\\'' if c == '\'' else
          c)


class Tree(object):

  def __init__(self, *args):
    if len(args) != len(self.attributes):
      raise TypeError("%s expects %d arguments %s, but found %d arguments %s" %
                      (type(self).__name__,
                       len(self.attributes), self.attributes,
                       len(args), args))
    for attr, arg in zip(self.attributes, args):
      setattr(self, attr, arg)

  def NotImplementedError(self):
    return NotImplementedError(type(self).__name__ + ' does not implement this method')

  def __eq__(self, other):
    return type(self) == type(other) and all(getattr(self, attr) == getattr(other, attr) for attr in self.attributes)

  def __repr__(self):
    return '%s(%s)' % (type(self).__name__, ', '.join(repr(getattr(self, attr)) for attr in self.attributes))


class Module(Tree):
  attributes = ('statements',)

  @property
  def str(self):
    return ''.join(stmt.Str(0) for stmt in self.statements)


class Expression(Tree):

  @property
  def str(self):
    raise self.NotImplementedError()

  def __str__(self):
    return self.str


class Id(Expression):
  attributes = ('value',)

  @property
  def str(self):
    return self.value


class Int(Expression):
  attributes = ('value',)

  @property
  def str(self):
    return str(self.value)


class Float(Expression):
  attributes = ('value',)

  @property
  def str(self):
    return str(self.value)


class Str(Expression):
  attributes = ('value',)

  @property
  def str(self):
    return '"%s"' % ''.join(map(SanitizeCharacter, self.value))


class Char(Expression):
  attributes = ('value',)

  @property
  def str(self):
    return "'%s'" % ''.join(map(SanitizeCharacter, self.value))


class ParentheticalExpression(Expression):
  attributes = ('expression',)

  @property
  def str(self):
    return '(' + self.expression.str + ')'


class FunctionCall(Expression):
  attributes = ('function', 'arguments',)

  @property
  def str(self):
    return '%s(%s)' % (self.function, ', '.join(arg.str for arg in self.arguments))


class Subscript(Expression):
  attributes = ('subscriptable', 'index',)

  @property
  def str(self):
    return '%s[%s]' % (self.subscriptable, self.index)


class MemberAccess(Expression):
  attributes = ('expression', 'attribute',)

  @property
  def str(self):
    return '%s.%s' % (self.expression, self.attribute)


class MemberAccessThroughPointer(Expression):
  attributes = ('expression', 'attribute',)

  @property
  def str(self):
    return '%s->%s' % (self.expression, self.attribute)


class PostfixOperation(Expression):
  attributes = ('expression', 'operator',)

  @property
  def str(self):
    return '%s%s' % (self.expression, self.operator)


class SizeofExpression(Expression):
  attributes = ('expression',)

  @property
  def str(self):
    return 'sizeof(%s)' % (self.expression)


class SizeofType(Expression):
  attributes = ('type',)

  @property
  def str(self):
    return 'sizeof(%s)' % (self.type.EmptyDeclare())


class PrefixOperation(Expression):
  attributes = ('operator', 'expression',)

  @property
  def str(self):
    return '%s%s' % (self.operator, self.expression)


class BinaryOperation(Expression):
  attributes = ('left', 'operator', 'right',)

  @property
  def str(self):
    return '%s %s %s' % (self.left, self.operator, self.right)


class ConditionalExpression(Expression):
  attributes = ('left', 'condition', 'right',)

  @property
  def str(self):
    return '%s ? %s : %s' % (self.left, self.condition, self.right)


class Statement(Tree):

  def Str(self, depth):
    raise self.NotImplementedError()


class Include(Statement):
  attributes = ('path',)

  def Str(self, depth):
    return TAB * depth + '#include <%s>\n' % self.path


class VariableDeclaration(Statement):
  attributes = ('name', 'type', 'value',)

  def Str(self, depth):
    return TAB * depth + self.type.Declare(self.name.str) + ' = ' + self.value.str + ';\n'


class FunctionDeclaration(Tree):
  attributes = ('name', 'type',)

  def Str(self, depth):
    return TAB * depth + self.type.Declare(self.name) + ';\n'


class FunctionDefinition(Statement):
  attributes = ('name', 'type', 'body',)

  def Str(self, depth):
    return TAB * depth + self.type.Declare(self.name.str) + '\n' + self.body.Str(0)


class While(Statement):
  attributes = ('condition', 'body',)

  def Str(self, depth):
    return TAB * depth + 'while (' + self.condition.str + ')\n' + self.body.Str(depth)


class Block(Statement):
  attributes = ('statements',)

  def Str(self, depth):
    return (TAB * depth + '{\n' +
            ''.join(stmt.Str(depth+1) for stmt in self.statements) +
            TAB * depth + '}\n')


class Return(Statement):
  attributes = ('expression',)

  def Str(self, depth):
    return TAB * depth + 'return ' + self.expression.str + ';\n'


class ExpressionStatement(Statement):
  attributes = ('expression',)

  def Str(self, depth):
    return TAB * depth + self.expression.str + ';\n'


class StructDefinition(Statement):
  attributes = ('name', 'bases', 'body',)

  def Str(self, depth):
    return TAB * depth + 'struct ' + self.name.EmptyDeclare() + '\n' + self.body.Str(depth)


class TemplateFunctionDefinition(Statement):
  attributes = ('arguments', 'function_definition',)


class TemplateStructDefinition(Statement):
  attributes = ('arguments', 'struct_definition',)


class Type(Tree):

  def Declare(self, declarator):
    raise self.NotImplementedError()

  def EmptyDeclare(self):
    return self.Declare('').strip()


class TypeId(Type):
  attributes = ('value',)

  def Declare(self, declarator):
    return self.value + ' ' + declarator


class PointerType(Type):
  attributes = ('pointee',)

  def Declare(self, declarator):
    return self.pointee.Declare('*' + declarator)


class ArrayType(Type):
  attributes = ('type', 'count',)

  def Declare(self, declarator):
    if declarator.startswith('*'):
      declarator = '(' + declarator + ')'
    return self.type.Declare(declarator + '[' + self.count + ']')


class ConstType(Type):
  attributes = ('type',)

  def Declare(self, declarator):
    return 'const ' + self.type.Declare(declarator)


class VolatileType(Type):
  attributes = ('type',)

  def Declare(self, declarator):
    return 'volatile ' + self.type.Declare(declarator)


class FunctionType(Type):
  attributes = ('argument_names', 'argument_types', 'return_type',)

  def Declare(self, declarator):
    declarator += '('
    first = True
    for name, type_ in zip(self.argument_names, self.argument_types):
      if not first:
        declarator += ', '
      first = False
      declarator += type_.Declare(name.str)
    declarator += ')'
    if declarator.startswith('*'):
      declarator = '(' + declarator + ')'
    return self.return_type.Declare(declarator)


class TemplateType(Type):
  attributes = ('arguments', 'name',)
