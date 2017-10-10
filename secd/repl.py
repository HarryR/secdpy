from __future__ import print_function
from .codegen import parse, codegen
from .vm import RUN
import sys

# read eval print loop

def repl():
	while True:
		try:
			line = raw_input('> ')
		except EOFError:
			break

		parsed = parse(line)
		code = codegen(parsed, [], ['stop'])
		print("@", code)

		result = RUN(code).s.pop()
		print("=", result)
		print("")

if __name__ == "__main__":
	repl()

