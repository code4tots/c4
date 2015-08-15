import collections

CHAR_STARTER = ("r'", "'")
STRING_STARTER = ('r"', '"')
SYMBOLS = tuple(reversed(sorted([
    # special symbols
    ';f', ';i', ';s', ';v',
    ';sizeof', # For distinguishing sizeof(type) vs sizeof(expression).
    # operators
    '++', '--',
    '*', '/', '%', '+', '-',
    '<<', '>>',
    '<', '<=', '>', '>=',
    '==', '!=',
    '&', '^', '|', '&&', '||',
    '=', '+=', '-=', '*=', '/=', '%=',
    '<<=', '>>=', '&=', '^=', '|=',
    # delimiters
    '[', ']', '(', ')', '{', '}',
    ';', ',', '.', '->', '~', '?', ':', '!',
])))
ID_CHARS = frozenset('abcdefghijklmnopqrstuvwxyz'
                     'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                     '0123456789_')
KEYWORDS = frozenset([
    'auto', 'break', 'case', 'const', 'continue', 'default',
    'do', 'else', 'enum', 'extern', 'for', 'goto', 'if',
    'register', 'return', 'signed', 'sizeof',
    'static', 'struct', 'switch', 'typedef', 'union', 'unsigned',
    'volatile', 'while',
])

Token = collections.namedtuple('Token', 'type value')

class Parse(object):

  def __init__(self, string, source='<unknown>'):
    self.s = string
    self.src = source
    self.j = 0
    self.i = 0
    self.peek = self.nexttok()

  ## Error handling.

  @property
  def lineno(self):
    return self.s.count('\n', 0, self.j) + 1

  @property
  def colno(self):
    return self.j - self.s.rfind('\n', 0, self.j)

  @property
  def line(self):
    start = self.s.rfind('\n', 0, self.j) + 1
    end = self.s.find('\n', self.j)
    end = len(self.s) if end == -1 else end
    return self.s[start:end]

  @property
  def location_message(self):
    return 'From %s, on line %s\n%s\n%s*\n' % (
        self.src, self.lineno,
        self.line,
        ' ' * (self.colno-1))

  def error(self, message):
    return SyntaxError(self.location_message + message + '\n')

  def raise_error(self, message):
    return self.error(message)

  ## Lex

  def done(self):
    return self.j >= len(self.s)

  @property
  def char(self):
    return self.s[self.i] if self.i < len(self.s) else ''

  def skipspaces(self):
    while not self.done() and self.char.isspace() or self.char == '#':
      if self.char == '#':
        while not self.done() and self.char != '\n':
          self.i += 1
      else:
        self.i += 1
    self.j = self.i

  def nexttok(self):
    self.skipspaces()

    self.j = self.i

    if self.done():
      return Token('eof', 'eof')

    # String literal
    if self.s.startswith(STRING_STARTER+CHAR_STARTER, self.i):
      type_ = 'str' if self.s.startswith(STRING_STARTER, self.i) else 'char'
      raw = False
      if self.char == 'r':
        raw = True
        self.i += 1
      quote = (self.s[self.i:self.i+3] if
               self.s.startswith(('"""', "'''"), self.i) else
               self.char)
      self.i += len(quote)
      while not self.s.startswith(quote, self.i):
        if self.i >= len(self.s):
          raise self.error("Finish your quotes!")
        self.i += 2 if raw and self.char == '\\' else 1
      self.i += len(quote)
      return Token(type_, eval(self.s[self.j:self.i]))

    # Symbol
    symbol_found = False
    for symbol in SYMBOLS:
      if self.s.startswith(symbol, self.i):
        self.i += len(symbol)
        symbol_found = True
        return Token(symbol, symbol)

    # int/float
    if (self.char.isdigit() or (self.char == '.' and
                                     self.s[self.i+1:self.i+2].isdigit())):
      self.j = self.i
      while self.i < len(self.s) and self.char.isdigit():
        self.i += 1
      if self.s.startswith('.', self.i):
        self.i += 1
        while self.i < len(self.s) and self.char.isdigit():
          self.i += 1
        return Token('float', float(self.s[self.j:self.i]))
      else:
        return Token('int', int(self.s[self.j:self.i]))

    # Identifier
    if self.char in ID_CHARS:
      while self.i < len(self.s) and self.char in ID_CHARS:
        self.i += 1
      val = self.s[self.j:self.i]
      return Token(val if val in KEYWORDS else 'id', val)

    # Unrecognized token.
    while self.i < len(self.s) and not self.char.isspace():
      self.i += 1

    raise self.error("I don't know what this token is.")

  def gettok(self):
    tok = self.peek
    self.peek = self.nexttok()
    return tok

  def at(self, *toktype):
    return self.peek.type in toktype

  def consume(self, *toktype):
    if self.at(*toktype):
      return self.gettok()

  def expect(self, *toktype):
    if not self.at(*toktype):
      raise self.error('Expected %s but found %s' %
                       (toktype, self.peek.type))
    return self.gettok()

  ## parse

  def ast(self, astcls, *args):
    return astcls(*(args + (self.s, self.src, self.j)))

  def all(self):
    stmts = []
    while not self.done():
      stmts.append(self.statement())
    return self.ast(TranslationUnit, tuple(stmts))

  def statement(self):
    if self.consume(';i'):
      return self.ast(Include, self.expect('char').value)
    elif self.consume(';v'):
      decls = []
      while not self.consume(';'):
        name = self.ast(Id, self.expect('id').value)
        type_ = self.type_expression()
        value = None
        if self.consume('='):
          value = self.expression()
        decls.append(self.ast(VariableDeclaration, name, type_, value))
        self.consume(',')
      return self.ast(StatementSequence, tuple(decls))
    elif self.consume(';f'):
      name = self.ast(Id, self.expect('id').value)
      type_ = self.type_expression()
      body = self.statement()
      return self.ast(FunctionDefinition, name, type_, body)
    elif self.consume('{'):
      stmts = []
      while not self.consume('}'):
        stmts.append(self.statement())
      return self.ast(Block, tuple(stmts))
    else:
      expr = self.expression()
      self.expect(';')
      return self.ast(ExpressionStatement, expr)

  def type_expression(self):
    if self.at('id'):
      return self.ast(TypeId, self.expect('id').value)
    elif self.consume('*'):
      return self.ast(PointerType, self.type_expression())
    elif self.consume('['):
      index = ''
      if self.at('int'):
        index = self.gettok().value
      self.expect(']')
      return self.ast(ArrayType, self.type_expression(), index)
    elif self.consume('('):
      argnames = []
      argtypes = []
      while not self.consume(')'):
        argnames.append(self.ast(Id, self.expect('id').value))
        argtypes.append(self.type_expression())
        self.consume(',')
      returns = self.type_expression()
      return self.ast(FunctionType, tuple(argnames), tuple(argtypes), returns)
    else:
      raise self.error('Expected type expression')

  def expression(self):
    # c4 expressions are similar to C grammar, but is simplified a bit.
    return self.expression14()

  def expression00(self):
    if self.at('int'):
      return self.ast(Int, self.expect('int').value)
    elif self.at('float'):
      return self.ast(Float, self.expect('float').value)
    elif self.at('str'):
      return self.ast(Str, self.expect('str').value)
    elif self.at('char'):
      return self.ast(Char, self.expect('char').value)
    elif self.at('id'):
      return self.ast(Id, self.expect('id').value)
    elif self.at('('):
      expr = self.expression()
      self.expect(')')
      return expr
    else:
      raise self.error('Expected expression')

  def expression01(self):
    expr = self.expression00()
    while True:
      if self.consume('('):
        args = []
        while not self.consume(')'):
          args.append(self.expression())
          self.consume(',')
        expr = self.ast(FunctionCall, expr, tuple(args))
      elif self.consume('['):
        index = self.expression()
        self.expect(']')
        expr = self.ast(Subscript, expr, index)
      elif self.at('++', '--'):
        expr = self.ast(PostfixOperation, expr, self.gettok().value)
      elif self.at('.', '->'):
        op = self.gettok().type
        op += self.expect('id').value
        expr = self.ast(PostfixOperation, expr, op)
      else:
        break
    return expr

  def expression02(self):
    if self.at('++', '--', '+', '-', '!', '~', '*', '&', ';sizeof'):
      op = self.gettok().type
      return self.ast(PrefixOperation, op, self.expression02())
    if self.consume('sizeof'):
      self.expect('(')
      type_ = self.type_expression()
      self.expect(')')
      return self.ast(SizeOfType, type_)
    return self.expression01()

  def expression03(self):
    expr = self.expression02()
    while self.at('*', '/', '%'):
      op = self.gettok().type
      expr = self.ast(BinaryOperation, expr, op, self.expression02())
    return expr

  def expression04(self):
    expr = self.expression03()
    while self.at('+', '-'):
      op = self.gettok().type
      expr = self.ast(BinaryOperation, expr, op, self.expression03())
    return expr

  def expression05(self):
    expr = self.expression04()
    while self.at('<<', '>>'):
      op = self.gettok().type
      expr = self.ast(BinaryOperation, expr, op, self.expression04())
    return expr

  def expression06(self):
    expr = self.expression05()
    while self.at('<', '<=', '>', '>='):
      op = self.gettok().type
      expr = self.ast(BinaryOperation, expr, op, self.expression05())
    return expr

  def expression07(self):
    expr = self.expression06()
    while self.at('==', '!='):
      op = self.gettok().type
      expr = self.ast(BinaryOperation, expr, op, self.expression06())
    return expr

  def expression08(self):
    expr = self.expression07()
    while self.at('&'):
      op = self.gettok().type
      expr = self.ast(BinaryOperation, expr, op, self.expression07())
    return expr

  def expression09(self):
    expr = self.expression08()
    while self.at('^'):
      op = self.gettok().type
      expr = self.ast(BinaryOperation, expr, op, self.expression08())
    return expr

  def expression10(self):
    expr = self.expression09()
    while self.at('|'):
      op = self.gettok().type
      expr = self.ast(BinaryOperation, expr, op, self.expression09())
    return expr

  def expression11(self):
    expr = self.expression10()
    while self.at('&&'):
      op = self.gettok().type
      expr = self.ast(BinaryOperation, expr, op, self.expression10())
    return expr

  def expression12(self):
    expr = self.expression11()
    while self.at('||'):
      op = self.gettok().type
      expr = self.ast(BinaryOperation, expr, op, self.expression11())
    return expr

  def expression13(self):
    expr = self.expression12()
    while self.consume('?'):
      cond = self.expression()
      self.expect(':')
      expr = self.ast(ConditionalExpression, expr, cond, self.expression12())
    return expr

  def expression14(self):
    expr = self.expression13()
    while self.at('=', '+=', '-=', '*=', '/=', '%=',
                  '<<=', '>>=', '&=', '^=', '|='):
      op = self.gettok().type
      expr = self.ast(BinaryOperation, expr, op, self.expression13())
    return expr

class Ast(object):
  def __init__(self, string, source, location):
    self.string = string
    self.source = source
    self.location = location

class TranslationUnit(Ast):

  def __init__(self, stmts, *args):
    super(TranslationUnit, self).__init__(*args)
    self.stmts = stmts

  @property
  def forward_declarations(self):
    return ''.join(stmt.forward_declaration for stmt in self.stmts)

  @property
  def declarations(self):
    return ''.join(stmt.declaration for stmt in self.stmts)

  @property
  def implementations(self):
    return ''.join(stmt.implementation for stmt in self.stmts)

  @property
  def all(self):
    return (self.forward_declarations +
            self.declarations + self.implementations)

class Type(Ast):
  pass

class TypeId(Type):

  def __init__(self, val, *args):
    super(TypeId, self).__init__(*args)
    self.val = val

  def declare(self, declarator):
    return '%s %s' % (self.val, declarator)

class PointerType(Type):

  def __init__(self, pointee, *args):
    super(PointerType, self).__init__(*args)
    self.pointee = pointee

  def declare(self, declarator):
    return self.pointee.declare('(*' + declarator + ')')

class ArrayType(Type):

  def __init__(self, target, index, *args):
    super(ArrayType, self).__init__(*args)
    self.target = target
    self.index = index

class FunctionType(Type):

  def __init__(self, argnames, argtypes, returns, *args):
    super(FunctionType, self).__init__(*args)
    self.argnames = argnames
    self.argtypes = argtypes
    self.returns = returns

  def declare(self, declarator):
    declarator += '('
    first = True
    for name, type_ in zip(self.argnames, self.argtypes):
      if not first:
        declarator += ', '
      first = False
      declarator += type_.declare(name.str)
    declarator += ')'
    return self.returns.declare(declarator)

class Expression(Ast):
  pass

class Int(Expression):

  def __init__(self, val, *args):
    super(Int, self).__init__(*args)
    self.val = val

  @property
  def str(self):
    return str(self.val)

class Char(Expression):

  def __init__(self, val, *args):
    super(Char, self).__init__(*args)
    self.val = val

  @property
  def str(self):
    return "'%s'" % ''.join('\\x%02x' % ord(c) for c in self.val)

class Str(Expression):

  def __init__(self, val, *args):
    super(Str, self).__init__(*args)
    self.val = val

  @property
  def str(self):
    return '"%s"' % ''.join('\\x%02x' % ord(c) for c in self.val)

class Id(Expression):

  def __init__(self, val, *args):
    super(Id, self).__init__(*args)
    self.val = val

  @property
  def str(self):
    return self.val

class FunctionCall(Expression):

  def __init__(self, f, fargs, *args):
    super(FunctionCall, self).__init__(*args)
    self.f = f
    self.args = fargs

  @property
  def str(self):
    return '(%s(%s))' % (self.f.str, ','.join(a.str for a in self.args))

class SizeOfType(Expression):

  def __init__(self, type_, *args):
    super(SizeOfType, self).__init__(*args)
    self.type_ = type_

  @property
  def str(self):
    return 'sizeof(%s)' % self.type_.declare('')

class PostfixOperation(Expression):

  def __init__(self, expr, op, *args):
    super(PostfixOperation, self).__init__(*args)
    self.expr = expr
    self.op = op

  @property
  def str(self):
    return '(%s%s)' % (self.expr.str, self.op)

class PrefixOperation(Expression):

  def __init__(self, op, expr, *args):
    super(PrefixOperation, self).__init__(*args)
    self.op = op
    self.expr = expr

  @property
  def str(self):
    return '(%s%s)' % (self.op, self.expr.str)

class BinaryOperation(Expression):

  def __init__(self, lhs, op, rhs, *args):
    super(BinaryOperation, self).__init__(*args)
    self.lhs = lhs
    self.op = op
    self.rhs = rhs

  @property
  def str(self):
    return '(%s%s%s)' % (self.lhs.str, self.op, self.rhs.str)

class Statement(Ast):
  def forward(self, depth):
    return ''


class Include(Statement):

  def __init__(self, path, *args):
    super(Include, self).__init__(*args)
    self.path = path

  @property
  def forward_declaration(self):
    return '#include <%s>\n' % (self.path)

  @property
  def declaration(self):
    return ''

  @property
  def implementation(self):
    return ''

class StatementSequence(Statement):
  """A sequence of statements, but not grouped like in a block."""

  def __init__(self, stmts, *args):
    super(StatementSequence, self).__init__(*args)
    self.stmts = stmts

  def forward(self, depth):
    return ''.join(stmt.forward(depth) for stmt in self.stmts)

  def str(self, depth):
    return ''.join(stmt.str(depth) for stmt in self.stmts)

class VariableDeclaration(Statement):

  def __init__(self, name, type_, value, *args):
    super(VariableDeclaration, self).__init__(*args)
    self.name = name
    self.type = type_
    self.value = value

  def forward(self, depth):
    return '\t' * depth + self.type.declare(self.name.str) + ';\n'

  def str(self, depth):
    return '\t' * depth + ('' if self.value is None else '%s = %s;\n' % (
        self.name.str, self.value.str))

class ExpressionStatement(Statement):

  def __init__(self, expr, *args):
    super(ExpressionStatement, self).__init__(*args)
    self.expr = expr

  def str(self, depth):
    return '\t' * depth + self.expr.str + ';\n'

class Block(Statement):

  def __init__(self, stmts, *args):
    super(Block, self).__init__(*args)
    self.stmts = stmts

  def str(self, depth):
    return '%s{\n%s%s}\n' % (
        '\t' * depth,
        ''.join(stmt.forward(depth+1) for stmt in self.stmts),
        ''.join(stmt.str(depth+1) for stmt in self.stmts))

class FunctionDefinition(Statement):

  def __init__(self, name, type_, body, *args):
    super(FunctionDefinition, self).__init__(*args)
    self.name = name
    self.type_ = type_
    self.body = body

  @property
  def forward_declaration(self):
    return ''

  @property
  def declaration(self):
    return self.type_.declare(self.name.str) + ';\n'

  @property
  def implementation(self):
    return self.type_.declare(self.name.str) + '\n' + self.body.str(0)

print(Parse(r"""
;i 'stdio.h'

;f main(argc int, argv **char) int {
  ;v x int = 10;
  printf("hi world! %d\n", 5 + 12);
  printf("sizeof(int) = %lu\n", sizeof(int));
  printf("sizeof(long) = %lu\n", sizeof(long));
  printf("sizeof(*void) = %lu\n", sizeof(*void));

  printf("x = %d\n", x);
  printf("x = %d\n", x++);
  printf("x = %d\n", x);
  printf("x = %d\n", ++x);
}
""").all().all)
