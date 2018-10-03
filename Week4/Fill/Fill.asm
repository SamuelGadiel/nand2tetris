// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Modificado por Samuel Gadiel de Ávila

// Put your code here.

(RESET) // Reseta o ponteiro para o inicio da tela
	@SCREEN
	D=A
	@cur_screen_word // Ponteiro para a palavra sendo atualmente operada
	M=D

(LOOP)	
	@KBD
	D=M
	
	@FILL // Se alguma tecla for pressionada (M[KBD] > 0), entao preencha palavra
	D; JGT
	
	@BLANK // caso contrario, palavra em branco
	0; JMP
	
(FILL)
	@cur_screen_word
	A=M
	M=-1
	
	@CHECK
	0; JMP
	
(BLANK)
	@cur_screen_word
	A=M
	M=0
	
	@CHECK
	0; JMP
	
(CHECK) // Checa se alcançou o fim da tela
	@cur_screen_word
	MD=M+1
	@KBD
	D=D-A
	
	@RESET // Se M[cur_screen_word] == KBD, reseta para o inicio da tela
	D; JEQ
	
	@LOOP  // caso contrario continua preenchendo(deixando em branco)
	0; JMP
	
