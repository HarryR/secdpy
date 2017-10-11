# secdpy

SECD machine and Lispkit Lisp compiler, in Python. Based on the final project by [Willem Yarbrough](https://github.com/yarbroughw/secdpy).

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

### opcodes

 * cons
 * car
 * cdr
 * nil
 * atom
 * ldc
 * ldf
 * ap
 * dum
 * join
 * ret
 * sel
 * rap
 * add
 * mul
 * sub
 * div
 * mod
 * xor
 * eq
 * lt
 * gt
 * le
 * ge

# SECD resources

 * [SECD virtual machine](https://webdocs.cs.ualberta.ca/~you/courses/325/Mynotes/Fun/SECD-slides.html)
 * https://github.com/zachallaun/secd
 * https://en.wikipedia.org/wiki/SECD_machine
 * The LispKit Manual, [Volume 1](https://www.cs.ox.ac.uk/files/3299/PRG32%20vol%201.pdf) [Volume 2](http://www.ocs.net/~jfurman/lispkit/prgversion/PRG32_vol_2.pdf) (PDF)
