import unittest

from . import parser
from . import ast


class ParseTest(unittest.TestCase):

  def test_six_minus_seven(self):
    self.assertEqual(
        parser.Parse('6 - 7;', '<unittest>'),
        ast.Module((
            ast.ExpressionStatement(
                ast.BinaryOperation(
                    ast.Int(6),
                    '-',
                    ast.Int(7),
                )
            ),
        ))
    )

  def test_template_type(self):
    self.assertEqual(
        parser.Parse("""
            ;v y [string string]map;
        """, '<unittest>'),
        ast.Module((
            ast.VariableDeclaration(
                ast.Id('y'),
                ast.TemplateType(
                    (ast.TypeId('string'), ast.TypeId('string'),),
                    'map',
                ),
                None,
            ),
        ))
    )


class CodeGenerationTest(unittest.TestCase):

  def test_function_definition(self):
    self.assertEqual(
        parser.Parse("""
            ;f main(argc int, argv **char) int {
              return 0;
            }
        """, '<unittest>').str,
r"""int main(int argc, char **argv)
{
  return 0;
}
""")

  def test_while_statement(self):
    self.assertEqual(
        parser.Parse("""
            while x < 2 {
              x++;
            }
        """, '<unittest>').str,
r"""while (x < 2)
{
  x++;
}
""")


if __name__ == '__main__':
  unittest.main()
