import sys
import ast
import operator
from collections import namedtuple 

State = namedtuple('State', ('s', 'e', 'c', 'd'))

APPLY = lambda S, N, F: F(*[x.pop() for x in [S.s] * N])
PEEK = lambda S, N, F: F(*S.s[-1:0-N])

COMMANDS = {
	'ADD': (APPLY, 2, operator.add),
	'MUL': (APPLY, 2, operator.mul),
	'SUB': (APPLY, 2, operator.sub),
	'DIV': (APPLY, 2, operator.div),
	'XOR': (APPLY, 2, operator.xor),
	'EQ': (PEEK, 2, operator.eq),
	'LT': (PEEK, 2, operator.lt),
	'GT': (PEEK, 2, operator.gt),
	'LEQ': (PEEK, 2, operator.le),
	'GEQ': (PEEK, 2, operator.ge),
	'CONS': (APPLY, 2, lambda car, cdr: [cdr.append(car), cdr][1]),
	'CAR': (APPLY, 1, lambda x: x.pop()),
	'CDR': (APPLY, 1, lambda x: [x.pop(), x][1]),
	'NIL': (lambda _: list(),),
	'ATOM': (PEEK, 1, lambda x: x == []),
	'LDC': (lambda S: S.c.pop(),),  # pushes constant argument onto stack
	'LDF': (lambda (s, e, c, d): [e[:], c.pop()],)
}

def secd_eval(code, stack=[]):
	state, running = State(stack, [], code, []), True
	while running:
		state, running = secd_step(state)
	return state

def secd_step(state):
	s, e, c, d = state
	stop = False
	op = c.pop().upper()
	if op in COMMANDS:
		cmd = COMMANDS[op]
		retval = cmd[0](*[state] + list(cmd[1:]))
		if retval is not None:
			s.append(retval)
	elif op == 'STOP':
		stop = True
	elif op == 'AP':
		d.extend([c, e, s])
		ce = s.pop()
		c, e = ce.pop(), ce.pop()
		e.append(s.pop())
		s = []
	elif op == 'LD':  # pushes the value of a variable onto the stack
		x, y = c.pop()
		s.append(e[-x][-y])
	elif op == 'DUM':
		e.append([])
	elif op == 'RAP':
		closure = s.pop()
		fn, env = closure.pop(), closure.pop()
		env.pop()
		v = s.pop()
		e.pop()
		d.extend([c, e, s])
		e = env
		e.append(v)
		c = fn
		s = []
	elif op == 'JOIN':
		c = [d.pop()]
	elif op == 'RTN':
		retval = s.pop()
		s = d.pop()
		s.append(retval)
		e, c = d.pop(), d.pop()
	elif op == 'SEL':
		x = s.pop()
		ct, cf = c.pop(), c.pop()
		d.append(c)
		c = [ct if x else cf]

	return State(s, e, c, d), not(stop)

if __name__ == "__main__":
    code = ast.literal_eval(sys.stdin.read())
    result = secd_eval(code)

