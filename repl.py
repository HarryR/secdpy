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
	print("Line:", line)

	parsed = parse(line)
	print("Parsed:", parsed)

	code = codegen(parsed, [], ['stop'])
	print("Code:", code)

	result = secd_eval(code).s.pop()
	print("=", result)

