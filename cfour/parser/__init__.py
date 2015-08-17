import abc

from . import expression
from . import lex
from . import statement
from . import type_expression


class Parser(lex.Lex, expression.Parser, statement.Parser, type_expression.Parser):
  pass


class Visitor(expression.Visitor, statement.Parser, type_expression.Parser):
  pass
