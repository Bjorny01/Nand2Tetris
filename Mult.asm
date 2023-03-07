// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.
//The code is optimized in the matter that if for example R0 is 1 and R1 is 6000 we dont add 1 6000 times but 
//insted ad 6000 one time 

//Set up variables
	@R2 
	M=0	//zeros the result before beginning

	@sum	//Zeros the sum before beginnening 
	M=0

	@counter
	M=0	//zeros the counter used for keeping track of number of addition

	@R0	//check if either factor is zero then directly put output R2 to zero
	D=M

	@FACTOR_ZERO
	D;JEQ

	@R1
	D=M

	@FACTOR_ZERO
	D;JEQ

	@R0	//Check which variable is bigger for optimized calculation speed
	D=M

	@R1
	D=D-M	//D will be >= 0 if R0 >= R1

	@IF_TRUE		
	D;JGE	//jumps to IF_TRUE



//Code for if R0<R1: R1 + R1 + R1 + ... + R1, R0 times	
(LOOP_1)	
	@sum
	D=M	//Now we added the in R1 one time to sum and stored it as our new sum
	
	@R2
	M=D	//stored the temporary result in R2

	@R1	//Add R1 one time to sum
	D=M

	@sum
	M=D+M

	@counter	//while loop start
	D=M+1

	@counter
	M=D

	@R0
	D=D-M	//counter - R0, if counter = RO we have added R1 R0 times
	
	@END
	D;JGT		//while loop end

	@LOOP_1
	0;JMP


//Code for if R0>=R1
(IF_TRUE)
	@sum
	D=M	//Now we added the in R1 one time to sum and stored it as our new sum
	
	@R2
	M=D	//stored the temporary result in R2

	@R0	//Add R1 one time to sum
	D=M

	@sum
	M=D+M

	@counter	//while loop start
	D=M+1

	@counter
	M=D

	@R1
	D=D-M	//counter - R1, if counter = R1 we have added R1 R0 times
	
	@END
	D;JGT		//while loop end

	@IF_TRUE
	0;JMP	//Jumps to  if true loop start 

(FACTOR_ZERO)	//sets result to zero if either factor is zero
	@R2
	M=0
	@END
	0;JMP

(END)
	@END
	0;JMP	//finish infinite loop