from __future__ import print_function
from codegen import *
from secd    import *
import sys

# read eval print loop

while True:
	try:
		line = raw_input('> ')
	except EOFError:
		break

	parsed = parse(line)
	code = codegen(parsed, [], ['stop'])
	print("@", code)
	result = secd_eval(code).s.pop()

	print("=", result)

