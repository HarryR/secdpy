# Ensure argument order is correct
> (DIV 3 50)
= 0
> (DIV 50 3)
= 16
> (REM 100 8)
= 4

# Verify the SECD opcodes for an expression
> (+ 1 4)
@ [LDC 4 LDC 1 ADD STOP]
= 5

# More example, many wow, such encoding
!
> (let (n) (10) n)
@ [NIL LDC 10 CONS LDF [LD (0 . 0) RTN] AP STOP]
= 10

