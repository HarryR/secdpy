from __future__ import print_function
import sys
import ast
import operator
import copy
from collections import namedtuple 

State = namedtuple('State', ('s', 'e', 'c', 'd'))

APPLY = lambda N, F: lambda (s, e, c, d): State(s[:0-N] + [F(*s[0-N:][::-1])], e, c, d)
PEEK = lambda N, F: lambda (s, e, c, d): State(s + [F(*s[0-N:][::-1])], e, c, d)

COMMANDS = dict()
COMMANDS.update({op.upper(): APPLY(2, getattr(operator, op))
				 for op in ['add', 'mul', 'sub', 'mod', 'div', 'xor']})
COMMANDS.update({op.upper(): PEEK(2, getattr(operator, op))
				 for op in ['eq', 'lt', 'gt', 'le', 'ge']})
COMMANDS.update({
	'CONS': lambda (s, e, c, d): State(s[:-2] + [ [s[-2], s[-1]] ], e, c, d),
	'CAR': lambda (s, e, c, d): State(s[:-1] + [ s[-1][-1] ], e, c, d),
	'CDR': lambda (s, e, c, d): State(s[:-1] + [ s[-1][-2] ], e, c, d),

	# pushes a nil pointer onto the stack
	'NIL': lambda (s, e, c, d): State(s + [None], e, c, d),

	'ATOM': lambda (s, e, c, d): State(s + [s[-1] == []], e, c, d),

	# pushes a constant argument onto the stack
	'LDC': lambda (s, e, c, d): State(s + [c[-1]], e, c[:-1], d),

	# load function, takes on argument representing a function
	# it constructs a closure and pushes that onto the stack
	'LDF': lambda (s, e, c, d): State(s + [[e, c[-1]]], e, c[:-1], d),

	# pops a closure and a list of parameters from the stack
	# the closure is applied to the parameters by installing its environment as
	# the current one, pushing the parameter list infront of that, clearing the
	# stack, and setting C to the closure's function pointer
	# the previous value of S, E and C are saved on the dump.
	'AP': lambda (s, e, c, d): State([], s[-1][-2] + [s[-2]], s[-1][-1], d + [c, e, s]),

	# pushes the value of a variable onto the stack
	# The variable is indicated by the argument, a pair
	# The pairs car represents the level, and cdr the position
	'LD': lambda (s, e, c, d): State(s + [e[0-c[-1][-1]][0-c[-1][-2]]], e, c[:-1], d),

	# pushes a 'dummy', empty list onto the stack
	'DUM': lambda (s, e, c, d): State(s, e + [[]], c, d),

	# pops a list reference from the dump and makes this the new value of C
	# the instruction appears at the end of either branch of a SEL
	'JOIN': lambda (s, e, c, d): State(s, e, [d[-1]], d[:-1]),

	# pops one value from the stack, restores S, E and C from the dump
	# then pushes return value onto the now current stack
	'RET': lambda (s, e, c, d): State(d[-1] + [s[-1]], d[-2], d[-3], d[:-3]),

	# expects two list arguments, and pops a value from the stack
	# The first list is executed if the value is not Nil
	'SEL': lambda (s, e, c, d): State(s[:-1], e, [c[-1] if s[-1] is not None else c[-2]], d + c[:-2]),

	# works like AP, only that it replaces an occurrence of a dummy environment with 
	# the current one, thus making recursive functions possible
	'RAP': lambda (s, e, c, d): State([], s[-1][-2][:-1] + [s[-2]], s[-1][-1], d + [c, e, s]),
})

STEP = lambda S: (COMMANDS[S.c[-1].upper()](State(S.s, S.e, S.c[:-1], S.d)), True) if S.c[-1].upper() != 'STOP' else (S, False)

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
    code = ast.literal_eval(sys.stdin.read())
    result = RUN(code)

