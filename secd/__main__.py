from __future__ import print_function
import traceback
import sys
from .codegen import parse, unparse, codegen
from .vm import RUN

def main(args):
	for filename in args:
		with open(filename, 'rb') as handle:
			print("Running", filename)
			code = codegen(parse(handle.read())) + ['STOP']
			print("Code:", unparse(code))
			result = RUN(code)
			print("Result:", result)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

