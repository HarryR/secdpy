from __future__ import print_function
import traceback
from .codegen import parse, unparse, codegen
from .vm import RUN

def repl():
    while True:
        try:
            line = raw_input('> ').strip()
        except EOFError:
            break
        if not line:
            continue

        try:
            parsed = parse(line)
            #print("~", unparse(parsed))
            code = codegen(parsed) + ['STOP']
            print("@", unparse(code))

            result = RUN(code).s.pop(0)
            print("=", result)
            print("")
        except Exception:
            traceback.print_exc()

if __name__ == "__main__":
    repl()
