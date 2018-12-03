// push constant 0
	@0
	D=A
	@SP
	M=M+1
	A=M-1
	M=D
// pop LCL 0
	@LCL
	D=M
	@0
	D=A+D
	@R13
	M=D
	@SP
	AM=M-1
	D=M
	@R13
	A=M
	M=D
// label None$LOOP_START
(None$LOOP_START)
// push ARG 0
	@ARG
	D=M
	@0
	A=A+D
	D=M
	@SP
	M=M+1
	A=M-1
	M=D
// push LCL 0
	@LCL
	D=M
	@0
	A=A+D
	D=M
	@SP
	M=M+1
	A=M-1
	M=D
// add
	@SP
	AM=M-1
	D=M
	@SP
	AM=M-1
	D=M+D
	@SP
	M=M+1
	A=M-1
	M=D
// pop LCL 0
	@LCL
	D=M
	@0
	D=A+D
	@R13
	M=D
	@SP
	AM=M-1
	D=M
	@R13
	A=M
	M=D
// push ARG 0
	@ARG
	D=M
	@0
	A=A+D
	D=M
	@SP
	M=M+1
	A=M-1
	M=D
// push constant 1
	@1
	D=A
	@SP
	M=M+1
	A=M-1
	M=D
// sub
	@SP
	AM=M-1
	D=M
	@SP
	AM=M-1
	D=M-D
	@SP
	M=M+1
	A=M-1
	M=D
// pop ARG 0
	@ARG
	D=M
	@0
	D=A+D
	@R13
	M=D
	@SP
	AM=M-1
	D=M
	@R13
	A=M
	M=D
// push ARG 0
	@ARG
	D=M
	@0
	A=A+D
	D=M
	@SP
	M=M+1
	A=M-1
	M=D
// if-goto None$LOOP_START
	@SP
	AM=M-1
	D=M
	@None$LOOP_START
	D;JNE
// push LCL 0
	@LCL
	D=M
	@0
	A=A+D
	D=M
	@SP
	M=M+1
	A=M-1
	M=D
