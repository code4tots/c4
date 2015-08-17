import unittest

from . import lex


class TestLexer(unittest.TestCase):

  def test_five_plus_five(self):
    lexer = lex.Lex(string="5+5.", source="<unittest>", visitor=None)

    tokens = []
    while not lexer.done():
      tokens.append(lexer.gettok())

    self.assertItemsEqual(tokens, [
        lex.Token('int', 5),
        lex.Token('+', None),
        lex.Token('float', 5.0),
    ])


if __name__ == '__main__':
  unittest.main()
