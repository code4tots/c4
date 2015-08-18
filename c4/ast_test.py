import unittest

from . import ast


class AstTest(unittest.TestCase):

  def test_five_plus_five(self):
    self.assertEqual(
        ast.BinaryOperation(
            ast.Int(5),
            '+',
            ast.Float(5.0)).str,
        '5 + 5.0')


if __name__ == '__main__':
  unittest.main()
