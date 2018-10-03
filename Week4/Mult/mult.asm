// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Modificado por Samuel Gadiel de Ávila

// Put your code here.

	@R0
	D=M
	@mult1 // Multiplicando
	M=D
	
	@R1
	D=M
	@mult2 // Multiplicador
	M=D
	
	@R2    // Produto
	M=0
	
	@i     // Contando variavel
	M=0
	
(LOOP)
	@i
	D=M
	@mult2
	D=D-M
	@END
	D; JEQ // Se (i-mult2 == 0) vai para END;
	
	@mult1
	D=M
	@R2
	M=M+D  // Adiciona mult1 para R2
	
	@i     // Aumenta contador
	M=M+1
	
	@LOOP
	0; JMP

(END)
	@END
	0; JMP
