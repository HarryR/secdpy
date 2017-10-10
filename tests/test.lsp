# Example
> (+ 1 4)
@ ['stop', 'add', 1, 'ldc', 4, 'ldc']
= 5

# More example
!
> (let (n) (10) n)
@ ['stop', 'ap', ['rtn', [1, 1], 'ld'], 'ldf', 'cons', 10, 'ldc', 'nil']
= 10
