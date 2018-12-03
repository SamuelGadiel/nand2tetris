// push ARG 1
	@ARG
	D=M
	@1
	A=A+D
	D=M
	@SP
	M=M+1
	A=M-1
	M=D
// pop pointer 1
	@3
	D=A
	@1
	D=A+D
	@R13
	M=D
	@SP
	AM=M-1
	D=M
	@R13
	A=M
	M=D
// push constant 0
	@0
	D=A
	@SP
	M=M+1
	A=M-1
	M=D
// pop THAT 0
	@THAT
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
// push constant 1
	@1
	D=A
	@SP
	M=M+1
	A=M-1
	M=D
// pop THAT 1
	@THAT
	D=M
	@1
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
// push constant 2
	@2
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
// label None$MAIN_LOOP_START
(None$MAIN_LOOP_START)
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
// if-goto None$COMPUTE_ELEMENT
	@SP
	AM=M-1
	D=M
	@None$COMPUTE_ELEMENT
	D;JNE
// goto None$END_PROGRAM
	@None$END_PROGRAM
	0;JMP
// label None$COMPUTE_ELEMENT
(None$COMPUTE_ELEMENT)
// push THAT 0
	@THAT
	D=M
	@0
	A=A+D
	D=M
	@SP
	M=M+1
	A=M-1
	M=D
// push THAT 1
	@THAT
	D=M
	@1
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
// pop THAT 2
	@THAT
	D=M
	@2
	D=A+D
	@R13
	M=D
	@SP
	AM=M-1
	D=M
	@R13
	A=M
	M=D
// push pointer 1
	@3
	D=A
	@1
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
// pop pointer 1
	@3
	D=A
	@1
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
// goto None$MAIN_LOOP_START
	@None$MAIN_LOOP_START
	0;JMP
// label None$END_PROGRAM
(None$END_PROGRAM)
