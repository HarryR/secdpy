from __future__ import print_function
import sys
import ast
import operator
import copy
from collections import namedtuple 

State = namedtuple('State', ('s', 'e', 'c', 'd'))

APPLY = lambda S, N, F: F(*[x.pop() for x in [S.s] * N])
PEEK = lambda S, N, F: F(*S.s[-1:0-N])

COMMANDS = {
	'CONS': (APPLY, 2, lambda car, cdr: [cdr.append(car), cdr][1]),
	'CAR': (APPLY, 1, lambda x: x.pop()),
	'CDR': (APPLY, 1, lambda x: [x.pop(), x][1]),
	'NIL': (lambda _: [],),
	'ATOM': (PEEK, 1, lambda x: x == []),
	'LDC': (lambda S: S.c.pop(),),  # pushes constant argument onto stack
	'LDF': (lambda (s, e, c, d): [e[:], c.pop()],)
}
COMMANDS.update({op.upper(): (APPLY, 2, getattr(operator, op))
				 for op in ['add', 'mul', 'sub', 'mod', 'div', 'xor']})
COMMANDS.update({op.upper(): (PEEK, 2, getattr(operator, op))
				 for op in ['eq', 'lt', 'gt', 'le', 'ge']})


"""
		d.extend([c, e, s])
		ce = s.pop()
		c, e = ce.pop(), ce.pop()
		e.append(s.pop())
		s = []


	ce = s[-1]
	c = ce[-1]
	e = ce[-2]

	d = d + [c, e, s]
	e = s[-1][-2] + s[-2]
	c = s[-1][-1]
	s = []
"""
AP = lambda (s, e, c, d): State([], s[-1][-2] + s[-2], s[-1][-1], d + [c, e, s])


"""
		x, y = c.pop()
		s.append(e[-x][-y])

		x = c[-1][-1]
		y = c[-1][-2]

		s = s + [e[c[-1][-1]][c[-1][-2]]]
"""
LD = lambda (s, e, c, d): State(s + [e[c[-1][-1]][c[-1][-2]]], e, c[:-1], d)

"""
		e.append([])
"""
DUM = lambda (s, e, c, d): State(s, e + [[]], c, d)

"""
		c = [d.pop()]

	c = [d[-1]]
	d = d[:-1]
"""
JOIN = lambda (s, e, c, d): State(s, e, [d[-1]], d[:-1])


"""
		retval = s.pop()
		s = d.pop()
		s.append(retval)
		e, c = d.pop(), d.pop()

		retval = s[-1]
		s = d[-1] + s[-1]
		e = d[-2]
		c = d[-3]
		d = d[:-3]
"""
RTN = lambda (s, e, c, d): State(d[-1] + s[-1], d[-2], d[-3], d[:-3])


"""
		x = s.pop()
		ct, cf = c.pop(), c.pop()
		d.append(c)
		c = [ct if x else cf]

	x = s[-1]
	ct = c[-1]
	cf = c[-2]

	s = s[:-1]
	e = e
	d = d + c[:-2]
	c = [c[-1] if s[-1] else c[-2]]
"""
SEL = lambda (s, e, c, d): State(s[:-1], e, [c[-1] if s[-1] else c[-2]], d + c[:-2])


"""
		closure = s.pop()  # s[-1]
		fn, env = closure.pop(), closure.pop()  # fn=s[-1][-1], env=s[-1][-2]
		env.pop()  # env = env[:-1]
		v = s.pop()        # s[-2]
		e.pop()        # e = e[:-1]
		d.extend([c, e, s])  # d = d + [c, e, s]
		e = env              # e = s[-1][-2][:-1]
		e.append(v)          # e = s[-1][-2][:-1] + [s[-2]]
		c = fn               # c = s[-1][-1]
		s = []				 # s = []
"""
RAP = lambda (s, e, c, d): State([], s[-1][-2][:-1] + [s[-2]], s[-1][-1], d + [c, e, s])


def secd_eval(code, state=None, stack=None):
	code = copy.deepcopy(code)
	if stack is None:
		stack = []
	if state is None:
		state = State(stack, [], code, [])
	else:
		state = State(state.s, state.e, code, state.d)
	running = True
	while running:
		state, running = secd_step(state)
	return state



def secd_step(state):
	s, e, c, d = state
	stop = False
	op = c.pop().upper()
	#print("#")
	#print("#  :", op)
	if op in COMMANDS:
		cmd = COMMANDS[op]
		newstate = State(s, e, c, d)
		args = [newstate] + list(cmd[1:])
		retval = cmd[0](*args)
		if retval is not None:
			#print("# S=", s)
			#print("# E=", e)
			#print("# C=", c)
			#print("# D=", d)
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
		# retval = s[-1]
		# s = d[-1] + s[-1]
		# e = d[-2]
		# c = d[-3]
		# d = d[:-3]
	elif op == 'SEL':
		x = s.pop()
		ct, cf = c.pop(), c.pop()
		d.append(c)
		c = [ct if x else cf]

	return State(s, e, c, d), not(stop)

if __name__ == "__main__":
    code = ast.literal_eval(sys.stdin.read())
    result = secd_eval(code)

