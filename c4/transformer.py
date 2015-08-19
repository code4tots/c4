"""transformer.py
"""
from . import ast


class Visitor(object):

  def Visit(self, node):
    visit_method_name = 'Visit' + type(node).__name__
    if hasattr(self, visit_method_name):
      return getattr(self, visit_method_name)(node)
    else:
      return self.GenericVisit(node)

  def GenericVisit(self, node):
    for attribute in node.attributes:
      child = getattr(node, attribute)
      if isinstance(node, ast.Tree):
        self.Visit(child)
      elif isinstance(child, tuple):
        for c in child:
          if isinstance(c, ast.Tree):
            self.Visit(c)


class TypeAnnotator(object):
  pass


class TemplateExpander(object):
  pass

