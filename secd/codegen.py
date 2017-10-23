import sys
import re
import operator

from .vm import COMMANDS
from .sexpr import *

def index(name, namelist):
    for x, level1 in enumerate(namelist):
        for y, element in enumerate(level1):
            if element == name:
                return (x, y)
    raise SyntaxError("Unknown variable '"+str(name)+"' in "+str(namelist))

def genatom(expr, names):
    if expr is None:
        return ['NIL']
    elif isnum(expr) or isstr(expr):
        return ['LDC', expr]
    elif issym(expr):
        return ['LD', index(expr.name, names)]
    raise SyntaxError("Cannot codegen atom: " + str(expr))

def peekargs(n, expr):
    out = [x for x in itercons(expr)][:n]
    if n != len(out) and expr is not None:
        raise SyntaxError("Trailing arguments, expected %d, remaining %d: %s" % (n, n - len(out), unparse(expr)))
    return out

EXPR = lambda n, f: lambda names, x: f(*[names] + peekargs(n, x))

flatten = lambda x: reduce(operator.add, x) if x else []

complis = lambda n, v: flatten([codegen(X, n) + ['CONS'] for X in itercons(v)])

genap = lambda n, v, b: ['NIL'] + complis(n, v) + b + ['AP']

MACROS = {
    'QUOTE': EXPR(1, lambda _, a: ['LDC', a]),

    # (IF x then else)
    'IF': EXPR(3, lambda n, x, a, b: codegen(x, n) + ['SEL', codegen(a, n) + ['JOIN'], codegen(b, n) + ['JOIN']]),

    # (LAMBDA args body)
    'LAMBDA': EXPR(2, lambda n, a, b: ['LDF', codegen(b, [a] + n) + ['RTN']]),

    # (LET args vals body)
    'LET': EXPR(3, lambda n, a, v, b: genap(n, v, ['LDF', codegen(b, [[x.name if x else None for x in a]] + n) + ['RTN']]))
}
COMMAND_ALIASES = {
    '+': 'ADD', '-': 'SUB', '/': 'DIV', '*': 'MUL',
    '^': 'XOR', '&': 'AND', '|': 'OR', 'EQ?': 'EQ',
    'ATOM?': 'ATOM', 'NIL?': 'NIL', '#T': 'T', '#F': 'F',
    'NULL?': 'NIL', 'NULL': 'NIL', '<=': 'LE', ">=": 'GE',
    '<': 'LT', '>': 'GT',
}

def codegen(expr, names=None):
    if names is None:
        names = []
    if isatom(expr):
        return genatom(expr, names)
    assert iscons(expr) or islist(expr)
    op = car(expr)
    if issym(op):
        name = op.name
        if name in MACROS:
            return MACROS[name](names, cdr(expr))
        # Otherwise, passthru to builtin command
        name = COMMAND_ALIASES.get(name, name)
        if name in COMMANDS:
            nargs, _ = COMMANDS[name]
            if nargs:
                args = peekargs(nargs, cdr(expr))
                return flatten([codegen(arg, names) for arg in args[::-1]]) + [name]
            return [name]
        raise SyntaxError("Unknown operation: '"+str(op)+"'")
    raise SyntaxError("Unknown token: "+type(op).__name__+' = '+str(op))

def main():
    code = sys.stdin.read()
    print(codegen(parse(code)))

if __name__ == '__main__':
    main()

