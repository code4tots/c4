"""lex.py

Extends ParseContext with methods for lexing.
"""
import collections

from . import context

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


class Lex(context.Context):

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
      raise self.error('Expected %s but found %s' % (toktype, self.peek.type))
    return self.gettok()
