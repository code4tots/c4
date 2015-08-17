"""context.py

Parser context -- this is the base class for the lexer in lex.py.
The main parser inherits from this by subclassing the lexer.
"""

class Context(object):

  def __init__(self, string, source, visitor):
    self.s = string
    self.src = source
    self.j = 0
    self.i = 0
    self.peek = self.nexttok()
    self.visitor = visitor

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

  def error(self, message):
    return SyntaxError(self.location_message + message + '\n')

  def raise_error(self, message):
    raise self.error(message)
