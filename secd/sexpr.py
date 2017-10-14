import re

list2cons = lambda args: reduce(lambda X, Y: (Y, X), args[::-1])
isatom = lambda e: e is None or isinstance(e, (str, int, bool))
issym = lambda e: isinstance(e, str) and len(e) > 0
isnum = lambda x: isinstance(x, int)
iscons = lambda x: isinstance(x, tuple) and len(x) == 2
cons = lambda x, y: (x, y)
car = lambda x: x[0]
cdr = lambda x: x[1] if isinstance(x, tuple) else x[1:]
cadr = lambda x: car(cdr(x))
caddr = lambda x: car(cdr(cdr(x)))

def itercons(x, maxn=None):
	n = 0
	while x is not None:
		if isatom(x):
			yield x
			break
		if isinstance(x, list) and not x:
			break
		yield car(x)
		x = cdr(x)
		n += 1
		if maxn and n == maxn:
			break

cons2list = lambda x: list(itercons(x))

_TERM_RX = r'''(?mx)
	\s*(?:
			(?P<lsq>\[)|
			(?P<rsq>\])|
			(?P<lbr>\()|
			(?P<rbr>\))|
			(?P<dot>\.)|
			(?P<num>-?\d+)|
			(?P<str>"([^"]|\\.)*")|
			(?P<sym>[^()\[\]\s]+)
	   )'''

def parse(sexpr):
	tokens = [[(t, v) for t, v in match.groupdict().items() if v][0]
		 	  for match in re.finditer(_TERM_RX, sexpr)]
	return tok2ast(tokens)

def tok2cons(tokens):
	out = []
	terminated = False
	while len(tokens):
		if tokens[0][0] == 'rbr':
			break
		if tokens[0][0] == 'dot':
			tokens.pop(0)
			out.append(tok2ast(tokens))
			terminated = True
			break
		out.append(tok2ast(tokens))
	if tokens[0][0] != 'rbr':
		raise SyntaxError("Missing right paren")
	if not terminated:
		out.append(None)
	tokens.pop(0)
	return list2cons(out)

def tok2list(tokens):
	out = []
	while len(tokens):
		if tokens[0][0] == 'rsq':
			break
		out.append(tok2ast(tokens))
	if tokens[0][0] != 'rsq':
		raise SyntaxError("Missing right bracket")
	tokens.pop(0)
	return out

def tok2ast(tokens):
	term, value = tokens.pop(0)
	if term == "lbr":
		return tok2cons(tokens)
	elif term == "lsq":
		return tok2list(tokens)
	elif term == "num":
		return int(value)
	elif term == "str":
		return value[1:-1]
	elif term == "sym":
		return value
	raise SyntaxError("Unexpected token: " + str(((term, value))))

def unparse(expr):
	if expr is None:
		return 'nil'
	if isinstance(expr, list):
		return '[' + ' '.join([unparse(X) for X in expr]) + ']'
	if isinstance(expr, tuple):
		out = []
		while expr:
			if expr[1] is None:
				out.append(unparse(expr[0]))
				break
			elif isatom(expr[1]):
				out.extend([unparse(expr[0]), '.', unparse(expr[1])])
				break
			out.append(unparse(expr[0]))
			expr = expr[1]
		return '(' + ' '.join(out) + ')'
	return str(expr)

