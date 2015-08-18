"""parser.py

This module has two components:

  1. the Parse function, and
  2. the Parser class.

Parse is a convenience function around Parser.
For most intents and purposes, I don't think you will need to use the Parser class directly.

The Parser class is enormous, but is divided into six logical parts.

  -- context
  -- lexical analysis
  -- module parsing
  -- expression parsing
  -- statement parsing
  -- type expression parsing

As of this writing, the Parser class is ~350 lines long.

  -- About ~150 lines of it is expression parsing.
  -- About ~100 lines of it is lexical analysis.

"""
import collections

from . import ast

CHAR_STARTER = ("r'", "'")

STRING_STARTER = ('r"', '"')

# To see that the symbols listed here match with the ones used during the parse, the regex
#   ;(?!(?:f|i|s|v|t|sizeof)\b)\w+
# may be useful.
SYMBOLS = tuple(reversed(sorted([
    # special symbols
    ';f', ';i', ';s', ';t', ';v',
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
    'auto',
    'break',
    'case', 'const', 'continue',
    'default', 'do',
    'else', 'enum', 'extern',
    'for',
    'goto',
    'if',
    'register', 'return',
    'signed', 'sizeof', 'static', 'struct', 'switch',
    'typedef',
    'union', 'unsigned',
    'volatile',
    'while'
])

Token = collections.namedtuple('Token', 'type value')


def Parse(string, source):
  return Parser(string, source).Module()


class Parser(object):

  ## context

  def __init__(self, string, source):
    self.s = string
    self.src = source
    self.j = 0
    self.i = 0
    self.peek = self.NextTok()

  @property
  def done(self):
    return self.j >= len(self.s)

  @property
  def char(self):
    return self.s[self.i] if self.i < len(self.s) else ''

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

  def Error(self, message):
    return SyntaxError(self.location_message + message + '\n')

  ## lexical analysis

  def SkipSpaces(self):
    while not self.done and self.char.isspace() or self.char == '#':
      if self.char == '#':
        while not self.done and self.char != '\n':
          self.i += 1
      else:
        self.i += 1
    self.j = self.i

  def NextTok(self):
    self.SkipSpaces()

    self.j = self.i

    if self.done:
      return Token('eof', 'eof')

    # String literal
    if self.s.startswith(STRING_STARTER + CHAR_STARTER, self.i):
      type_ = 'str' if self.s.startswith(STRING_STARTER, self.i) else 'char'
      raw = False
      if self.char == 'r':
        raw = True
        self.i += 1
      quote = self.s[self.i:self.i+3] if self.s.startswith(('"""', "'''"), self.i) else self.char
      self.i += len(quote)
      while not self.s.startswith(quote, self.i):
        if self.i >= len(self.s):
          raise self.Error("Finish your quotes!")
        self.i += 2 if raw and self.char == '\\' else 1
      self.i += len(quote)
      return Token(type_, eval(self.s[self.j:self.i]))

    # Symbol
    symbol_found = False
    for symbol in SYMBOLS:
      if self.s.startswith(symbol, self.i):
        self.i += len(symbol)
        symbol_found = True
        return Token(symbol, None)

    # int/float
    if self.char.isdigit() or (self.char == '.' and self.s[self.i+1:self.i+2].isdigit()):
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
      type_ = val if val in KEYWORDS else 'id'
      return Token(type_, val if type_ == 'id' else None)

    # Unrecognized token.
    while self.i < len(self.s) and not self.char.isspace():
      self.i += 1

    raise self.Error("I don't know what this token is.")

  def GetTok(self):
    tok = self.peek
    self.peek = self.NextTok()
    return tok

  def At(self, *toktype):
    return self.peek.type in toktype

  def Consume(self, *toktype):
    if self.At(*toktype):
      return self.GetTok()

  def Expect(self, *toktype):
    if not self.At(*toktype):
      raise self.Error('Expected %s but found %s' % (toktype, self.peek.type))
    return self.GetTok()

  ## module parsing

  def Module(self):
    stmts = []
    while not self.done:
      stmts.append(self.Statement())
    return ast.Module(tuple(stmts))

  ## expression parsing

  def Expression(self):
    # c4 expressions are similar to C grammar, but is simplified a bit.
    return self.Expression14()

  def Expression00(self):
    if self.At('id'):
      return ast.Id(self.Expect('id').value)
    elif self.At('int'):
      return ast.Int(self.Expect('int').value)
    elif self.At('float'):
      return ast.Float(self.Expect('float').value)
    elif self.At('str'):
      return ast.Str(self.Expect('str').value)
    elif self.At('char'):
      return ast.Char(self.Expect('char').value)
    elif self.Consume('('):
      expr = self.Expression()
      self.Expect(')')
      return ast.ParentheticalExpression(expr)
    else:
      raise self.Error('Expected expression')

  def Expression01(self):
    expr = self.Expression00()
    while True:
      if self.Consume('('):
        args = []
        while not self.Consume(')'):
          args.append(self.Expression())
          self.Consume(',')
        expr = ast.FunctionCall(expr, tuple(args))
      elif self.Consume('['):
        index = self.Expression()
        self.Expect(']')
        expr = ast.Subscript(expr, index)
      elif self.At('++', '--'):
        expr = ast.PostfixOperation(expr, self.GetTok().type)
      elif self.Consume('.'):
        expr = ast.MemberAccess(expr, self.Expect('id').value)
      elif self.Consume('->'):
        expr = ast.MemberAccessThroughPoniter(expr, self.Expect('id').value)
      else:
        break
    return expr

  def Expression02(self):
    if self.At('++', '--', '+', '-', '!', '~', '*', '&'):
      op = self.GetTok().type
      return ast.PrefixOperation(op, self.Expression02())
    if self.Consume(';sizeof'):
      return ast.SizeofExpression(self.Expression())
    if self.Consume('sizeof'):
      self.Expect('(')
      type_ = self.TypeExpression()
      self.Expect(')')
      return ast.SizeofType(type_)
    return self.Expression01()

  def Expression03(self):
    expr = self.Expression02()
    while self.At('*', '/', '%'):
      op = self.GetTok().type
      expr = ast.BinaryOperation(expr, op, self.Expression02())
    return expr

  def Expression04(self):
    expr = self.Expression03()
    while self.At('+', '-'):
      op = self.GetTok().type
      expr = ast.BinaryOperation(expr, op, self.Expression03())
    return expr

  def Expression05(self):
    expr = self.Expression04()
    while self.At('<<', '>>'):
      op = self.GetTok().type
      expr = ast.BinaryOperation(expr, op, self.Expression04())
    return expr

  def Expression06(self):
    expr = self.Expression05()
    while self.At('<', '<=', '>', '>='):
      op = self.GetTok().type
      expr = ast.BinaryOperation(expr, op, self.Expression05())
    return expr

  def Expression07(self):
    expr = self.Expression06()
    while self.At('==', '!='):
      op = self.GetTok().type
      expr = ast.BinaryOperation(expr, op, self.Expression06())
    return expr

  def Expression08(self):
    expr = self.Expression07()
    while self.At('&'):
      op = self.GetTok().type
      expr = ast.BinaryOperation(expr, op, self.Expression07())
    return expr

  def Expression09(self):
    expr = self.Expression08()
    while self.At('^'):
      op = self.GetTok().type
      expr = ast.BinaryOperation(expr, op, self.Expression08())
    return expr

  def Expression10(self):
    expr = self.Expression09()
    while self.At('|'):
      op = self.GetTok().type
      expr = ast.BinaryOperation(expr, op, self.Expression09())
    return expr

  def Expression11(self):
    expr = self.Expression10()
    while self.At('&&'):
      op = self.GetTok().type
      expr = ast.BinaryOperation(expr, op, self.Expression10())
    return expr

  def Expression12(self):
    expr = self.Expression11()
    while self.At('||'):
      op = self.GetTok().type
      expr = ast.BinaryOperation(expr, op, self.Expression11())
    return expr

  def Expression13(self):
    expr = self.Expression12()
    while self.Consume('?'):
      cond = self.Expression()
      self.Expect(':')
      expr = ast.ConditionalExpression(expr, cond, self.Expression12())
    return expr

  def Expression14(self):
    expr = self.Expression13()
    while self.At('=', '+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '&=', '^=', '|='):
      op = self.GetTok().type
      expr = ast.BinaryOperation(expr, op, self.Expression13())
    return expr

  ## statement parsing

  def Statement(self):
    if self.Consume(';i'):
      return ast.Include(self.Expect('char').value)
    elif self.Consume(';v'):
      name = ast.Id(self.Expect('id').value)
      type_ = self.TypeExpression()
      value = None
      if self.Consume('='):
        value = self.Expression()
      self.Expect(';')
      return ast.VariableDeclaration(name, type_, value)
    elif self.Consume(';f'):
      name = ast.Id(self.Expect('id').value)
      type_ = self.TypeExpression()
      body = self.Statement()
      return ast.FunctionDefinition(name, type_, body)
    elif self.Consume(';s'):
      name = ast.TypeId(self.Expect('id').value)
      bases = []
      while not self.At('{'):
        bases.append(self.TypeExpression())
      body = self.Statement()
      return ast.StructDefinition(name, tuple(bases), body)
    elif self.Consume(';t'):
      args = []
      while not self.At(';f', ';s'):
        args.append(ast.TypeId(self.Expect('id').value))
      if self.At(';f'):
        return ast.TemplateFunctionDefinition(tuple(args), self.Statement())
      elif self.At(';s'):
        return ast.TemplateStructDefinition(tuple(args), self.Statement())
      else:
        raise SyntaxError(self.peek)
    elif self.Consume('while'):
      cond = self.Expression()
      body = self.Statement()
      return ast.While(cond, body)
    elif self.Consume('{'):
      stmts = []
      while not self.Consume('}'):
        stmts.append(self.Statement())
      return ast.Block(tuple(stmts))
    elif self.Consume('return'):
      expr = self.Expression()
      self.Expect(';')
      return ast.Return(expr)
    else:
      expr = self.Expression()
      self.Expect(';')
      return ast.ExpressionStatement(expr)

  ## type expression parsing

  def TypeExpression(self):
    if self.At('id'):
      return ast.TypeId(self.Expect('id').value)
    elif self.Consume('const'):
      return ast.ConstType(self.TypeExpression())
    elif self.Consume('volatile'):
      return ast.VolatileType(self.TypeExpression())
    elif self.Consume('*'):
      return ast.PointerType(self.TypeExpression())
    elif self.Consume('['):
      if self.At('int'):
        index = self.GetTok().value
        self.Expect(']')
        return ast.ArrayType(self.TypeExpression(), index)
      else:
        args = []
        while not self.Consume(']'):
          args.append(self.TypeExpression())
        template_name = self.Expect('id').value
        return ast.TemplateType(tuple(args), template_name)
    elif self.Consume('('):
      argnames = []
      argtypes = []
      while not self.Consume(')'):
        argnames.append(ast.Id(self.Expect('id').value))
        argtypes.append(self.TypeExpression())
        self.Consume(',')
      returns = self.TypeExpression()
      return ast.FunctionType(tuple(argnames), tuple(argtypes), returns)
    else:
      raise self.Error('Expected type expression')
