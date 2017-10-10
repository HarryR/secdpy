from __future__ import print_function
import sys
from secd import secd_eval
from codegen import codegen, parse


def test_harness(handle):
	"""
	Executes statements from a 'test file'
	example:

		> (+ 1 4)
		= 5
	"""
	state = None
	result = None
	for line in handle:
		line = line.strip()
		if not line or line[0] == '#':
			continue
		elif line == '!':
			print("!")
			state = None
			continue
		elif line[0] == '>':
			parsed = parse(line[1:].strip())
			print('>', parsed)
			code = codegen(parsed, [], ['stop'])
			print("@", code)
			state = secd_eval(code, state)
			result = state.s[-1]
			print("=", result)
			continue
		elif line[0] == '=':
			expected = line[1:].strip()
			if str(result) != expected:
				print("!!! Expected:", expected)
				print("")
	

def main(args):
	for filename in args:
		with open(filename, 'r') as handle:
			test_harness(handle)


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))

