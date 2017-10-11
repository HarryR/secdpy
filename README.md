# secdpy

**WARNING: this is a work-in-progress, there are still some oddities and incompatibilities with existing LispKit compiled code**

SECD machine and Lispkit Lisp compiler, in Python. Based on the project by [Willem Yarbrough](https://github.com/yarbroughw/secdpy). It aims to be an easy to understand functional implementation of the SECD virtual machine, with a LispKit compatible compiler and Python friendly integrations.

## repl.py

```
# python -msecd.repl
> (+ 1 4)
= 5

# etc..
```

## test.py

The test tool is a general purpose unit testing tool for secdpy, it parses commands which looks like and are compatible with output from the REPL:

```lisp
# Example
> (+ 1 4)
@ ['stop', 'add', 1, 'ldc', 4, 'ldc']
= 5

# More example
!
> (let (n) (10) n)
@ ['stop', 'ap', ['rtn', [1, 1], 'ld'], 'ldf', 'cons', 10, 'ldc', 'nil']
= 10
```

run the tests from the commandline with:

```
python -msecd.test tests/*.lsp
```

commands:

each line in the unit test file stats with a single letter command:

 * `!` clear state
 * `>` compile and execute lisp
 * `@` verify compiled lisp matches exactly
 * `=` check result on stack

## vm.py

The virtual machine has been re-written in a purely functional style that transforms the current state into a new result state, for example:

```python
State = namedtuple('State', ('s', 'e', 'c', 'd'))
NOP = lambda S: S
NIL = lambda (s, e, c, d): State(s + [None], e, c, d)
NIL(NOP(State([],[],[],[]))) == State([None], [], [], [])
```

a more complicated example:

```python
# pops one value from the stack, restores S, E and C from the dump
# then pushes return value onto the now current stack
RET = lambda (s, e, c, d): State(d[-1] + [s[-1]], d[-2], d[-3], d[:-3])
```

can be translated from the equivalent procedural code:

```python
retval = s.pop()         # s[-1]
s = d.pop() + [retval]   # d[-1] + [s[-1]]
e = d.pop()              # d[-2]
c = d.pop()              # d[-3]
d = d                    # d[:-3]
```

Python functions can be used with the wrappers `APPLY` and `PEEK` to create a state transform which accepts N arguments, then applies the function and pushes its result onto the stack, for example:

```python
ADD = APPLY(2, operator.add)
EQ = PEEK(2, operator.peek)   # don't remove arguments from stack
CHR = APPLY(1, chr)
```

# Lisp Syntax

The Lisp syntax aims to be SECD and LispKit compatible, it should be able to run code from textbooks as great care is being taken to preserve compatibility with the reference materials.

```lisp
(LETREC SUMFOLD
	(SUMFOLD LAMBDA (Z) (FOLDRIGHT ADDTHEM (QUOTE 1) Z))
	(ADDTHEM LAMBDA (X Y) (ADD X Y))
	(FOLDRIGHT LAMBDA (FUN B XS)
		(IF (EQ XS (QUOTE NIL)) B
			(FUN (CAR XS) (FOLDRIGHT FUN B (CDR XS))))))
```

## Commands

 * `if`
 * `null`
 * `nil`
 * `lambda`
 * `let`
 * `letrec`
 * `list`
 
## Operators

 * `+ - * / ^`
 * `car`, `cdr`
 * `zero`
 * `atom`
 * `eq`
 * `leq`

# Opcodes / Instructions

## control

 * `stop` halt execution
 * `ap F A` pops Function and Arguments from stack, saves then replaces current state. 
 * `rap` like AP, but allows for recursion
 * `sel X A B` runs `A if X else B` 
 * `join` returns after a `sel`
 * `ret A` restores state from `C`, adds `A` to stack
 
## structure

 * `ldc A` pushes a constant argument onto the stack
 * `ldf A` load function, takes on argument representing a function, pushes a closure onto stack
 * `dum` pushes an empty list onto the stack
 * `cons A B` creates a pair from two arguments
 * `car A` first of pair
 * `cdr A` second of pair
 * `nil` pushes a nil pointer onto the stack
 * `atom` given an expression returns True if its value is atomic; False if not.
 
## operator functions

 * `add A B`
 * `mul A B`
 * `sub A B`
 * `div A B`
 * `mod A B`
 * `xor A B`
 
## comparisons

arguments aren't removed from stack for comparison operations

 * `eq A B` equal
 * `lt A B` less than
 * `gt A B` greater than
 * `le A B` less than equal
 * `ge A B` greater than equal

# References

 * [The LispKit System, by Peter Henderson](http://www.cs.ncl.ac.uk/publications/trs/papers/129.pdf)
 * [LispKit C and Lisp Source, compiled SECD output](http://www.cs.uml.edu/~giam/91.531/Code/lispkit/LKIT-2/)
 * [SECD virtual machine](https://webdocs.cs.ualberta.ca/~you/courses/325/Mynotes/Fun/SECD-slides.html)
 * The LispKit Manual, [Volume 1](https://www.cs.ox.ac.uk/files/3299/PRG32%20vol%201.pdf) [Volume 2](http://www.ocs.net/~jfurman/lispkit/prgversion/PRG32_vol_2.pdf) (PDF)

# License

MIT licensed, see [`LICENSE`](LICENSE) file.
