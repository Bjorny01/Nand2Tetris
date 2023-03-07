// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen gradually,
// When no key is pressed, the program clears the screen gradually

//Tried for a really long time make a program that counts upwards A=A+1 and fills in the addresses with 
//-1 (black) when a key is pressed
//And counts backwards A=A-1 anf fills in the addresses with 0 (white) when no key is pressed

//However I couldnt manage so I made a program that really fills upp the whole screen gradaully
//when a key is pressed
//And empties it gradually when no key i pressed

(INF_LOOP)
	@SCREEN //@16384
	D=A
	@pixel_counter
	M=D	//Saving the adress of the first 16 pixels to always start there, either gradually 
		//filling screen wiuth black or white depending on kbd input

	@KBD	
	D=M
	@WHITE
	D;JEQ	//Checks keyboard input, if no key is pressed M=0 so D will jump to white function, else continue

(BLACK)
	@pixel_counter
	A=M	//Pointer to first 16 pixels
	M=-1	//First 16 pixels of screen in the beginning set to black

	@pixel_counter
	D=M
	@24575
	D=D-A
	@INF_LOOP
	D;JEQ	//Jumps and quits loop when we are on second last pixel, as 24576 is also start of keyboard
	
	@pixel_counter
	M=M+1	//Goes to next 16 pixels, so when we set pointer we point to next 16 pixels
	@BLACK
	0;JMP	//Jumps back to black loop, as the check if the screen is filled is already done

(WHITE)
	@pixel_counter
	A=M
	M=0	//First 16 pixels of screen in the beginning set to black

	@pixel_counter	//check if on last pixels have to be done too know when to read KBD
	D=M
	@24575
	D=D-A
	@INF_LOOP
	D;JEQ	//Jumps and quits loop when we are on second last pixel as 24576 is also start of keyboard
	
	@pixel_counter
	M=M+1	//Goes to next 16 pixels
	@WHITE
	0;JMP	//Jumps back to white loop, as the check if the screen is filled is already done