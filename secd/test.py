from __future__ import print_function
import sys
import ast
from .vm import RUN
from .codegen import codegen, parse, unparse


def test_harness(handle):
	"""
	Executes statements from a 'test file'
	example:

		> (+ 1 4)
		= 5
	"""
	state = None
	result = None
	code = None
	for line in handle:
		line = line.strip()
		if not line or line[0] == '#':
			if len(line):
				print(line)
			continue
		elif line == '!':
			print("!")
			state = None
		elif line[0] == '>':
			parsed = parse(line[1:].strip())
			print('>', unparse(parsed))
			code = codegen(parsed, [], ['stop'])
			print("@", code)
			state = RUN(code, state=state)
			result = state.s[-1]
			print("=", result)
			print("")
		elif line[0] == '@':
			expected = ast.literal_eval(line[1:].strip())
			if code != expected:
				print("#!! Expected:", expected)
				print("#       Code:", code)
				print("")
		elif line[0] == '=':
			expected = line[1:].strip()
			if str(result) != expected:
				print("#!! Expected:", expected)
				print("")
		else:
			print("#!! Unexpected:", line)
			print("")
	

def main(args):
	if len(args):
		for filename in args:
			with open(filename, 'r') as handle:
				test_harness(handle)
	else:
		test_harness(sys.stdin)


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))

