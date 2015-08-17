import unittest

from . import parser


class SimpleVisitor(parser.Visitor):
  """SimpleVisitor for testing.

  Since implementing all of the visitor methods is rather tedious, this class implements __getattribute__ so that whenever a visitor method is called, we return (method_name, *args). where method_name is the name of the visitor method, and args is the arguments that was passed to the method.
  """

  def __getattribute__(self, attribute):
    value = super(SimpleVisitor, self).__getattribute__(attribute)
    if callable(value):
      def astfunc(*args):
        return (attribute,) + args
      return astfunc
    else:
      return value


class ExpressionTest(unittest.TestCase):

  def test_five_plus_five(self):
    visitor = SimpleVisitor()
    parser_ = parser.Parser("5 + 5", '<unittest>', visitor)
    self.assertEqual(
        parser_.expression(),
        (
            'binary_operation',
            ('int', 5),
            '+',
            ('int', 5),
        )
    )


if __name__ == '__main__':
  unittest.main()
