import re
from collections import namedtuple

cons2list = lambda x: list(itercons(x))
list2cons = lambda args: reduce(lambda X, Y: cons(Y, X), args[::-1])
isstr = lambda x: isinstance(x, (str, bytes))
issym = lambda x: isinstance(x, symbol)
isnum = lambda x: isinstance(x, (int, long))
isnil = lambda x: x is None
islist = lambda x: isinstance(x, list)
iscons = lambda x: isinstance(x, cons) or (isinstance(x, tuple) and len(x) == 2)
isbool = lambda x: isinstance(x, bool)
isatom = lambda x: any([fn(x) for fn in [isstr, issym, isnum, isnil, isbool]])
symbol = namedtuple('symbol', ('name',))
cons = namedtuple('cons', ('car', 'cdr'))
car = lambda x: x[0]
cdr = lambda x: x[1] if isinstance(x, (tuple, cons)) else x[1:]
cadr = lambda x: car(cdr(x))
caar = lambda x: car(car(x))
cdar = lambda x: cdr(car(x))
caddr = lambda x: car(cdr(cdr(x)))

def itercons(expr, maxn=None):
    assert iscons(expr)
    count = 0
    while expr is not None:
        if isatom(expr):
            yield expr
            break
        if isinstance(expr, list) and not expr:
            break
        yield car(expr)
        expr = cdr(expr)
        count += 1
        if maxn and count == maxn:
            break

_LEX_REGEX = r'''(?mx)
    \s*(?:
            (?P<lsq>\[)|
            (?P<rsq>\])|
            (?P<lbr>\()|
            (?P<rbr>\))|
            (?P<dot>\.)|
            (?P<num>-?\d+)|
            "(?P<str>([^"]|\\.)*)"|
            (?P<sym>[^'"()\[\]\s\r\n$]+)
       )'''

lex = lambda sexpr: [[(t, v) for t, v in match.groupdict().items() if v][0]
                     for match in re.finditer(_LEX_REGEX, sexpr)]

parse = lambda sexpr: _tok2ast(lex(sexpr))

def _tok2cons(tokens):
    out = []
    terminated = False
    while tokens:
        if caar(tokens) == 'rbr':
            break
        if caar(tokens) == 'dot':
            tokens.pop(0)
            out.append(_tok2ast(tokens))
            terminated = True
            break
        out.append(_tok2ast(tokens))
    if caar(tokens) != 'rbr':
        raise SyntaxError("Missing right paren")
    if not terminated:
        out.append(None)
    tokens.pop(0)
    return list2cons(out)

def _tok2list(tokens):
    out = []
    while tokens:
        if caar(tokens) == 'rsq':
            break
        out.append(_tok2ast(tokens))
    if tokens[0][0] != 'rsq':
        raise SyntaxError("Missing right bracket")
    tokens.pop(0)
    return out

def _tok2ast(tokens):
    term, value = tokens.pop(0)
    if term == "lbr":
        return _tok2cons(tokens)
    elif term == "lsq":
        return _tok2list(tokens)
    elif term == "num":
        return int(value)
    elif term == "str":
        return value
    elif term == "sym":
        return symbol(value.upper())
    raise SyntaxError("Unexpected token: " + str(((term, value))))

def unparse(expr, raw=False):
    """
    Convert an sexpression back into its string representation.
    """
    if expr is None:
        return 'nil'
    if issym(expr):
        return expr.name
    if isinstance(expr, list):
        return '[' + ' '.join([unparse(X, True) for X in expr]) + ']'
    if isnum(expr) or (raw and isstr(expr)):
        return str(expr)
    if iscons(expr):
        out = []
        while expr:
            if issym(expr) or expr[1] is None:
                out.append(unparse(expr[0]))
                break
            elif isatom(expr[1]):
                out.extend([unparse(expr[0]), '.', unparse(expr[1])])
                break
            out.append(unparse(expr[0]))
            expr = expr[1]
        return '(' + ' '.join(out) + ')'
    if isstr(expr):
        return '"' + str(expr) + '"'
    raise RuntimeError("Cannot unparse unknown type: %s - %s" % (type(expr), str(expr)))
