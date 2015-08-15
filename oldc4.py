STRING_STARTER = ('r"', '"', "r'", "'")
SYMBOLS = tuple(reversed(sorted([
    # special symbols
    ';f', ';i', ';s', ';v',
    # operators
    '++', '--',
    '*', '/', '%', '+', '-',
    '<<', '>>',
    '<', '<=', '>', '>=',
    '==', '!=',
    '&', '^', '|', '&&', '||',
    '=', '+=', '-=', '*=', '/=', '%=',
    '<<=', '>>=', '&=', '^=', '|='
    # delimiters
    '[', ']', '(', ')', '{', '}',
    ';', ',', '.', '->', '~', '?', ':',
])))
ID_CHARS = frozenset('abcdefghijklmnopqrstuvwxyz'
                     'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                     '0123456789_')

def lex(s):
    tokens = []
    i = 0
    while True:
        # Skip spaces and comments.
        while i < len(s) and (s[i].isspace() or s[i] == '#'):
            if s[i] == '#':
                while i < len(s) and s[i] != '\n':
                    i += 1
            else:
                i += 1

        # Check for eof
        if i >= len(s):
            break

        # Mark the start of this new token.
        j = i

        # Lex string literals
        if s.startswith(STRING_STARTER, i):
            raw = False
            if s[i] == 'r':
                raw = True
                i += 1
            quote = s[i:i+3] if s.startswith(('"""', "'''"), i) else s[i]
            i += len(quote)
            while not s.startswith(quote, i):
                if i >= len(s):
                    raise SyntaxError("close your quotes!")
                i += 2 if raw and s[i] == '\\' else 1
            i += len(quote)
            tokens.append(s[j:i])
            continue

        # Lex symbols
        symbol_found = False
        for symbol in SYMBOLS:
            if s.startswith(symbol, i):
                tokens.append(symbol)
                i += len(symbol)
                symbol_found = True
                break
        if symbol_found:
            continue

        # Lex id
        if s[i].isdigit() or (s[i] == '.' and s[i+1:i+2].isdigit()):
            j = i
            while i < len(s) and s[i].isdigit():
                i += 1
            if s.startswith('.', i):
                i += 1
                while i < len(s) and s[i].isdigit():
                    i += 1
                tokens.append(float(s[j:i]))
            else:
                tokens.append(int(s[j:i]))
            continue

        # Identifier
        if s[i] in ID_CHARS:
            while i < len(s) and s[i] in ID_CHARS:
                i += 1
            tokens.append(s[j:i])
            continue

        # Unrecognized token.
        while i < len(s) and not s[i].isspace():
            i += 1
        raise SyntaxError(s[j:i])

    return tuple(tokens)

def parse(s):
    tokens = lex(s)
    i = [0]

    def error(*args, **kwargs):
        raise SyntaxError(*args, **kwargs)

    def done():
        return i[0] >= len(tokens)

    def peek():
        return tokens[i[0]] if i[0] < len(tokens) else ''

    def atstr():
        return isinstance(peek(), str) and peek().startswith(STRING_STARTER)

    def atid():
        return (not done() and
                isinstance(peek(), str) and
                all(c in ID_CHARS for c in peek()))

    def at(tok):
        return (atid()                  if tok == 'id'            else
                at((tok,))              if isinstance(tok, str)   else
                peek() in tok           if isinstance(tok, tuple) else
                atstr()                 if tok == str             else
                isinstance(peek(), tok) if tok in (int, float)    else
                error(tok))

    def gettok():
        tok = peek()
        i[0] += 1
        return tok

    def consume(tok):
        if at(tok):
            return gettok()

    def expect(tok):
        if not at(tok):
            raise SyntaxError((tok, peek()))
        return gettok()

    # The three major constructs we will have are
    # statements, expressions and type expressions.

    def statement():
        if consume(';f'):
            name = expect('id')
            type_ = type_expression()
            body = statement()
            return (';f', name, type_, body)
        elif consume(';s'):
            name = expect('id')
            body = statement()
            return (';s', name, body)
        elif consume(';i'):
            return (';i', eval(expect(str)))
        elif consume(';v'):
            triples = []
            while not consume(';'):
                name = expect('id')
                type_ = type_expression()
                value = None
                if consume('='):
                    value = expression()
                triples.append((name, type_, value))
            if triples:
                return (';v', tuple(triples))
            else:
                return (';',)
        elif consume('return'):
            expr = expression()
            expect(';')
            return ('return', expr)
        elif consume('{'):
            stmts = []
            while not consume('}'):
                stmts.append(statement())
            return ('{}', tuple(stmts))
        elif consume(';'):
            return (';',)
        else:
            expr = expression()
            expect(';')
            return (';e', expr)

    def expression():
        return expression14()

    def type_expression():
        if consume('*'):
            return ('*', type_expression())
        elif at('id'):
            return ('id', gettok())
        elif consume('('):
            args = []
            while not consume(')'):
                name = expect('id')
                type_ = type_expression()
                args.append((name, type_))
                consume(',')
            returns = type_expression()
            return (';f', tuple(args), returns)
        elif consume('['):
            if consume(']'):
                return ('[]', type_expression(), '')
            else:
                d = expect(int)
                return ('[]', type_expression(), d)
        else:
            error(peek())

    # Expression parsing is a bit more complicated, so they
    # are split into phases here.

    def expression00():
        if consume('('):
            expr = expression()
            expect(')')
            return expr
        elif at(int):
            return ('int', gettok())
        elif at(float):
            return ('float', gettok())
        elif at(str):
            return ('str', eval(gettok()))
        elif at('id'):
            return ('id', gettok())
        else:
            error(peek())

    def expression01():
        expr = expression00()
        while True:
            if at(('++', '--')):
                expr = ('.' + gettok(), expr)
            elif consume('('):
                args = []
                while not consume(')'):
                    args.append(expression())
                    consume(',')
                expr = ('.()', expr, tuple(args))
            elif consume('.'):
                expr = ('.', expr, expect('id'))
            else:
                break
        return expr

    def expression04():
        expr = expression01()
        while at(('+', '-')):
            op = gettok()
            rhs = expression01()
            expr = (op, expr, rhs)
        return expr

    def expression14():
        expr = expression04()
        if at(('=', '+=', '-=', '*=', '/=', '%=',
               '<<=', '>>=', '&=', '^=', '|=')):
            op = gettok()
            rhs = expression14()
            return (op, expr, rhs)
        return expr

    stmts = []
    while not done():
        stmts.append(statement())
    return tuple(stmts)

class CodeGenerator(object):

    def __init__(self, string):
        self.stmts = parse(string)

    def all(self):
        return (self.generate_forward_declarations(self.stmts) +
                self.generate_headers(self.stmts) +
                self.generate_implementations(self.stmts))

    def generate_forward_declarations(self, stmts):
        return ''.join(self.generate_forward_declaration(stmt)
                       for stmt in stmts)

    def generate_headers(self, stmts):
        return ''.join(self.generate_header(stmt) for stmt in stmts)

    def generate_implementations(self, stmts):
        return ''.join(self.generate_implementation(stmt) for stmt in stmts)

    def require_path(self, filename):
        return '~/src/c4/lib/' + filename

    def generate_forward_declaration(self, stmt):
        if stmt[0] == ';s':
            return 'typedef struct %s %s;\n' % ((stmt[1],) * 2)
        elif stmt[0] == ';r':
            with open(self.require_path(stmt[1]), 'r') as f:
                return CodeGenerator(f.read()).generate_forward_declarations()
        elif stmt[0] in (';f', ';v', ';i'):
            return ''
        else:
            raise ValueError(stmt)

    def generate_header(self, stmt):
        if stmt[0] == ';f':
            _, name, type_, _ = stmt
            return self.declare_variable(type_, name) + ';\n'
        elif stmt[0] == ';s':
            _, name, body = stmt
            return 'struct %s %s;\n' % (name, self.generate_statement(body))
        elif stmt[0] == ';v':
            hdr = ''
            for name, type_, _ in stmt[1]:
                hdr += 'extern ' + self.declare_variable(type_, name) + ';\n'
            return hdr
        elif stmt[0] == ';i':
            return '#include <%s>\n' % stmt[1]
        elif stmt[0] == ';r':
            with open(self.require_path(stmt[1]), 'r') as f:
                return CodeGenerator(f.read()).generate_headers()
        else:
            raise ValueError(stmt)

    def generate_implementation(self, stmt):
        if stmt[0] == ';f':
            _, name, type_, body = stmt
            return '%s %s' % (self.declare_variable(type_, name),
                              self.generate_statement(body))
        elif stmt[0] == ';v':
            imp = ''
            for name, type_, value in stmt[1]:
                imp += self.declare_variable(type_, name)
                if value:
                    imp += ' = ' + self.generate_expression(value)
                imp += ';\n'
            return imp
        elif stmt[0] in (';s', ';i'):
            return ''
        elif stmt[0] == ';r':
            with open(self.require_path(stmt[1]), 'r') as f:
                return CodeGenerator(f.read()).generate_implementations()
        else:
            raise ValueError()

    def declare_variable(self, type_, declarator):
        if type_[0] == ';f':
            _, args, returns = type_
            declarator += '('
            first = True
            for argname, argtype in args:
                if not first:
                    declarator += ', '
                first = False
                declarator += self.declare_variable(argtype, argname)
            declarator += ')'
            return self.declare_variable(returns, '('+declarator+')')
        elif type_[0] == '*':
            return self.declare_variable(type_[1], '(*'+declarator+')')
        elif type_[0] == 'id':
            return '%s %s' % (type_[1], declarator)
        elif type_[0] == '[]':
            _, inner_type, index = type_
            return self.declare_variable(inner_type,
                                         '(%s[%s])' % (declarator, index))
        else:
            raise ValueError(type_)

    def generate_statement(self, stmt):
        if stmt[0] == '{}':
            _, stmts = stmt
            return '{%s}' % ''.join(self.generate_statement(s) for s in stmts)
        elif stmt[0] == ';e':
            return self.generate_expression(stmt[1]) + ';'
        elif stmt[0] == ';v':
            return self.generate_implementation(stmt)
        elif stmt[0] == 'return':
            return 'return %s;' % self.generate_expression(stmt[1])
        else:
            raise ValueError(stmt)

    def generate_expression(self, expr):
        if expr[0] == 'id':
            return expr[1]
        elif expr[0] in ('int', 'float'):
            return str(expr[1])
        elif expr[0] == 'str':
            return '"%s"' % ''.join('\\x%02x' % ord(c) for c in expr[1])
        elif expr[0] == '.()':
            _, f, args = expr
            return '(%s(%s))' % (self.generate_expression(f),
                                 ','.join(self.generate_expression(arg)
                                          for arg in args))
        elif expr[0] == '.':
            _, e, attr = expr
            return '(%s.%s)' % (self.generate_expression(e), attr)
        elif expr[0] in ('*', '/', '%',
                         '+', '-',
                         '<<', '>>',
                         '<', '<=', '>', '>=',
                         '==', '!=',
                         '&', '^', '|', '&&', '||',
                         '=', '+=', '-=', '*=', '/=', '%=',
                         '<<=', '>>=', '&=', '^=', '|='):
            op, lhs, rhs = expr
            return '(%s%s%s)' % (self.generate_expression(lhs), op,
                                 self.generate_expression(rhs))
        else:
            raise ValueError(expr)

print(CodeGenerator(r"""
;i 'stdio.h'

;f gcd (a int, b int) int {
    while (b != 0) {
        int c = b;
        b = a % c;
        a = c;
    }
    return a;
}

;s Datum {
    ;v x int;
}

;f main (argc int, argv **char) int {
    ;v x int = 10;
    ;v d Datum;
    d.x = 5 + 525;
    printf("%d\n", argc);
    printf("Hello world!\n");
    printf("x = %d\n", x);
    printf("d.x = %d\n", d.x);
    return 0;
}
""").all())
