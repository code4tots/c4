# C4 design

The c4 package will be composed of three main parts:

```text
                 ----------                      -------------
                 | ast.py | ----- generates ---> | C program |
                 ----------                      -------------
                 ^         ^
                /           \
   generates ast           verifies and
   from a C4 program       transforms the ast
              /               \
             /                 v
      -------------       ------------------
      | parser.py |       | transformer.py |
      -------------       ------------------
```

Now, not all possible configuration of ast elements will generate a valid C program.

The ast transformers will first verify that the the parsed ast is valid. Then it will annotate the tree (e.g. type annotations), and do other fancy footwork (insert forward declarations, expand templates, etc.).

It seems to me that the most interesting part of this package will be the transformer.
