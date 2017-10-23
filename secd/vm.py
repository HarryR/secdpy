from __future__ import print_function
import sys
import operator
import copy
from collections import namedtuple

from .sexpr import *

State = namedtuple('State', ('s', 'e', 'c', 'd'))

APPLY = lambda N, F: lambda (s, e, c, d): State([F(*s[:N])] + s[N:], e, c[1:], d)
PEEK = lambda N, F: lambda (s, e, c, d): State([F(*s[:N])] + s, e, c[1:], d)

COMMANDS = dict(
    NOP=(0, lambda S: S),
    T=(0, lambda (s, e, c, d): State([True] + s, e, c[1:], d)),
    F=(0, lambda (s, e, c, d): State([False] + s, e, c[1:], d)),
    CHR=(1, APPLY(1, chr)),
    ORD=(1, APPLY(1, ord)),
)
COMMANDS.update({op.upper(): (2, APPLY(2, getattr(operator, op)))
                 for op in ['add', 'mul', 'sub', 'mod', 'div', 'xor', 'lshift', 'rshift']})
COMMANDS.update({op.upper(): (2, PEEK(2, getattr(operator, op)))
                 for op in ['eq', 'lt', 'gt', 'le', 'ge']})

COMMANDS.update({
    # Special instruction, exit loop
    'STOP': COMMANDS['NOP'],

    #
    #   s = cons( cons( car(s),car(cdr(s)) ),cdr(cdr(s)) )
    #   c = cdr(c)
    #
    'CONS': (2, lambda (s, e, c, d): State([(s[0], s[1])] + s[2:], e, c[1:], d)),

    # CAR = ((v1.v2).s) e (CAR.c) d -> (v1.s) e c d
    #
    #   s = cons(car(car(s)), cdr(s))
    #   c = cdr(c)
    #
    'CAR': (1, lambda (s, e, c, d): State([s[0][0]] + s[1:], e, c[1:], d)),

    # CDR = ((v1.v2).s) e (CDR.c) d -> (v2.s) e c d
    #
    #   s = cons(cdr(car(s)),cdr(s))
    #   c = cdr(c)
    #
    'CDR': (1, lambda (s, e, c, d): State([s[0][1]] + s[1:], e, c[1:], d)),

    # pushes a nil pointer onto the stack
    'NIL': (0, lambda (s, e, c, d): State([None] + s, e, c[1:], d)),

    # Is a symbol, number or other primitive non-Null value?
    #
    #   if issym(car(s)) or isnum(car(s))
    #       then s := cons(t, cdr(s))
    #       else s := cons(f, cdr(s))
    #   c = cdr(c)
    #
    'ATOM': (1, lambda (s, e, c, d): State([isatom(s[0])] + s, e, c[1:], d)),

    # pushes a constant argument onto the stack
    #
    #   s = cons(car(cdr(c)), s)
    #   c = cdr(cdr(c))
    #
    'LDC': (1, lambda (s, e, c, d): State([c[1]] + s, e, c[2:], d)),

    # LDF = s e (LDF c'.c) d -> ((c'.e).s) e c d
    #
    # load function, takes on argument representing a function
    # it constructs a closure and pushes that onto the stack
    #
    #   s = cons(cons(car(cdr(c)), e), s)
    #   c = cdr(cdr(c))
    #
    'LDF': (1, lambda (s, e, c, d): State([[c[1], e]] + s, e, c[2:], d)),

    # AP = ((c'.e')v .s) e (AP.c) d -> NIL (v.e') c' (s e c .d)
    #
    # pops a closure and a list of parameters from the stack
    # the closure is applied to the parameters by installing its environment as
    # the current one, pushing the parameter list infront of that, clearing the
    # stack, and setting C to the closure's function pointer
    # the previous value of S, E and C are saved on the dump.
    #
    #   d = cons(cdr(cdr(s)), cons(e, cons(cdr(c), d)))     # s[1][1]
    #   e = cons(car(cdr(s)), cdr(car(s)))                  # s[1] + s[0][1:]
    #   c = car(car(s))                                     # s[0][0]
    #   s = None
    #
    'AP': (2, lambda (s, e, c, d): State([], [s[1]] + s[0][1:], s[0][0], [s[2:], e, c[1:]] + d)),

    # pushes the value of a variable onto the stack
    # The variable is indicated by the argument, a pair
    # The pairs car represents the level, and cdr the position
    #
    'LD': (1, lambda (s, e, c, d): State([e[c[1][0]][c[1][1]]] + s, e, c[2:], d)),

    # pushes a 'dummy', empty list onto the stack
    #
    #   e = cons(nil, e)
    #   c = cdr(c)
    #
    'DUM': (0, lambda (s, e, c, d): State(s, [None] + e, c[1:], d)),

    # pops a list reference from the dump and makes this the new value of C
    # the instruction appears at the end of either branch of a SEL
    #
    #   c = car(d)
    #   d = cdr(d)
    #
    'JOIN': (0, lambda (s, e, c, d): State(s, e, [d[0]], d[1:])),

    # RET = (v) e" (RTN) (s e c . d) -> (v . s) e c d
    #
    # pops one value from the stack, restores S, E and C from the dump
    # then pushes return value onto the now current stack
    #
    #   s = cons(car(s), car(d))
    #   e = car(cdr(d))
    #   c = car(cdr(cdr(d)))
    #   d = cdr(cdr(cdr(d)))
    #
    'RET': (0, lambda (s, e, c, d): State([s[0]] + d[0], d[1], d[2], d[3:])),

    # SEL = (v . s) e (SEL cT cF . c) d -> s e cv(c.d)
    #
    # expects two list arguments, and pops a value from the stack
    # The first list is executed if the value is not Nil
    #
    # (... SEL (...then part...JOIN)
    #          (...else part...JOIN) ...)
    #
    #   d := cons(cdr(cdr(cdr(c))), d)
    #   c := car(cdr(c)) if sval(car(s)) == "T" else car(cdr(cdr(c)))
    #   s := cdr(s)
    #
    'SEL': (2, lambda (s, e, c, d): State(s[1:], e, [c[1] if s[0] is not None else c[2]], c[3:] + d)),

    # works like AP, only that it replaces an occurrence of a dummy environment with
    # the current one, thus making recursive functions possible
    #
    #   d := cons(cdr(cdr(s)),cons(cdr(e),cons(cdr(c),d)))
    #   e := cdr(car(s))
    #   car(e) := car(cdr(s))
    #   c := car(car(s))
    #   s := nil
    #
    'RAP': (2, lambda (s, e, c, d): State([], [s[1]] + s[0][1][1:], s[0][0], [s, e, c] + d)),
})

# Common aliases for compatibility and ease of use
COMMAND_ALIASES = {'RTN': 'RET', 'REM': 'MOD', 'LEQ': 'LE', 'GEQ': 'GE', 'IF': 'SEL',
                   'SHL': 'LSHIFT', 'SHR': 'RSHIFT',

                   # LispKit numeric aliases
                   1: 'LD', 2: 'LDC', 3: 'LDF', 4: 'AP', 5: 'RET',
                   6: 'DUM', 7: 'RAP', 8: 'SEL', 9: 'JOIN', 10: 'CAR',
                   11: 'CDR', 12: 'ATOM', 13: 'CONS', 14: 'EQ', 15: 'ADD',
                   16: 'SUB', 17: 'MUL', 18: 'DIV', 19: 'MOD', 20: 'LE',
                   21: 'STOP'}
COMMANDS.update({x: COMMANDS[y] for x, y in COMMAND_ALIASES.items()})

STEP = lambda S: (COMMANDS[S.c[0].upper()][1](S), True) if S.c[0].upper() != 'STOP' else (S, False)

def RUN(code, state=None, stack=None):
    if stack is None:
        stack = []
    if state is None:
        state = State(stack, [], code, [])
    else:
        state = State(state.s, state.e, code, state.d)
    running = True
    while running:
        print('#', state)
        state, running = STEP(state)
    return state

if __name__ == "__main__":
    print(unparse(RUN(parse(sys.stdin.read()))))
