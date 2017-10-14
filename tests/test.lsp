> (DIV 3 50)
= 16
> (DIV 50 3)
= 0

# Example
> (+ 1 4)
@ [LDC 4 LDC 1 ADD STOP]
= 5

# More example
!
> (let (n) (10) n)
@ [NIL LDC 10 CONS LDF [LD (0 . 0) RTN] AP STOP]
= 10
