"""
hvmCodeWriter.py -- Code Writer class for Hack VM translator
"""

import os
from hvmCommands import *

debug = False

class CodeWriter(object):
    
    def __init__(self, outputName):
        """
        Open 'outputName' and gets ready to write it.
        """
        self.file = open(outputName, 'w')
        self.SetFileName(outputName)

        self.labelNumber = 0
        self.returnLabel = None
        self.callLabel = None
        self.cmpLabels = {}
        self.needHalt = True


    def Debug(self, value):
        """
        Set debug mode.
        Debug mode writes useful comments in the output stream.
        """
        global debug
        debug = value


    def Close(self):
        """
        Write a jmp $ and close the output file.
        """
        if self.needHalt:
            if debug:
                self.file.write('    // <halt>\n')
            label = self._UniqueLabel()
            self._WriteCode('@%s, (%s), 0;JMP' % (label, label))
        self.file.close()


    def SetFileName(self, fileName):
        """
        Sets the current file name to 'fileName'.
        Restarts the local label counter.

        Strips the path and extension.  The resulting name must be a
        legal Hack Assembler identifier.
        """
        if (debug):
            self.file.write('    // File: %s\n' % (fileName))
        self.fileName = os.path.basename(fileName)
        self.fileName = os.path.splitext(self.fileName)[0]
        self.functionName = None


    def Write(self, line):
        """
        Raw write for debug comments.
        """
        self.file.write(line + '\n')


    def _UniqueLabel(self):
        """
        Make a globally unique label.
        The label will be _sn where sn is an incrementing number.
        """
        self.labelNumber += 1
        return '_' + str(self.labelNumber)


    def _LocalLabel(self, name):
        """
        Make a function/module unique name for the label.
        If no function has been entered, the name will be
        FileName$$name. Otherwise it will be FunctionName$name.
        """
        if self.functionName != None:
            return self.functionName + '$' + name
        else:
            return self.fileName + '$$' + name


    def _StaticLabel(self, index):
        """
        Make a name for static variable 'index'.
        The name will be FileName.index
        """
        return self.fileName + '.' + str(index)    


    def _WriteCode(self, code):
        """
        Write the comma separated commands in 'code'.
        """
        code = code.replace(',', '\n').replace(' ', '')
        self.file.write(code + '\n')
        


    def WritePushPop(self, commandType, segment, index):
        """
        Write Hack code for 'commandType' (C_PUSH or C_POP).
        'segment' (string) is the segment name.
        'index' (int) is the offset in the segment.
	To be implemented as part of Project 6
	
	    For push: Pushes the content of segment[index] onto the stack. It is a good idea to move the value to be pushed into a register first, then push the content of the register to the stack.
        For pop: Pops the top of the stack into segment[index]. You may need to use a general purpose register (R13-R15) to store some temporary results.
        Hint: Recall that there are 8 memory segments in the VM model, but only 5 of these exist in the assembly definition. Also, not all 8 VM segments allow to perform both pop and push on them. Chapter 7.3 of the book explains memory segment mapping.
        Hint: Use pen and paper first. Figure out how to compute the address of segment[index] (except for constant). Then figure out how you move the value of segment[index] into a register (by preference D). Then figure out how to push a value from a register onto the stack. 
        Hint: For pop, you already know how to compute the address of segment[index]. Store it in a temporary register (you can use R13 to R15 freely). Then read the value from the top of the stack, adjust the top of the stack, and then store the value at the location stored in the temporary register.
    
    PUSH constant is implemented as an example. Other solutions are possible too.

        """
        segment_push_dict = {
            #13 is used as addr memory, since it is a free use memory in the arcitecture proposed in the book
            'local' : "@LCL, D=M, @" + index + ", D=D+A, @13, M=D, A=M, D=M,", #D=RAM[LCL + index]
            'argument': "@ARG, D=M, @" + index + ", D=D+A, @13, M=D, A=M, D=M,",
            'this': "@THIS, D=M, @" + index + ", D=D+A, @13, M=D, A=M, D=M,",
            'that': "@THAT, D=M, @" + index + ", D=D+A, @13, M=D, A=M, D=M,",
            'constant' : "@" + index + ", D=A,",
            'static' : "@" + self.fileName + "." + index + ", D=M,",
            'pointer' : "@3, D=A, @" + index + ", D=D+A, @13, M=D, A=M, D=M,", #index is either 0/1 depending on if we want this/that
            'temp' :"@5, D=A, @" + index + ", D=D+A, @13, M=D, A=M, D=M,",
            }

        segment_pop_dict = {
            #13 is used as addr memory, since it is a free use memory in the arcitecture proposed in the book
            'local' : "@LCL, D=M, @" + index + ", D=D+A, @13, M=D,", #addr=RAM[LCL] + index
            'argument': "@ARG, D=M, @" + index + ", D=D+A, @13, M=D,",
            'this': "@THIS, D=M, @" + index + ", D=D+A, @13, M=D,",
            'that': "@THAT, D=M, @" + index + ", D=D+A, @13, M=D,",
            'static' : "@" + self.fileName + "." + index + ", D=A, @13, M=D,",
            'pointer' : "@3, D=A, @" + index + ", D=D+A, @13, M=D,", #index is either 0/1 depending on if we want this/that
            'temp' :"@5, D=A, @" + index + ", D=D+A, @13, M=D,",
            }

        if commandType == C_PUSH: #Pushesh value from chosen memory segment onto top of stack, inc SP
            #ex pseudo: push local 2 --> addr = LCL + 2, *SP=*addr, SP++
            code = "//Push command, "
            code += segment_push_dict[segment] + " @SP, A=M, M=D, @SP, M=M+1"
            self._WriteCode(code)

        elif commandType == C_POP: #Pops value from top of stack into chosen memory segment, dec SP
            #ex pseudo: pop local 2 --> addr = LCL + 2, SP--, *addr = *SP
            code = "//Pop command, "
            code += segment_pop_dict[segment] + "@SP, M=M-1, @SP, A=M, D=M, @13, A=M, M=D"
            self._WriteCode(code)

    def WriteArithmetic(self, command):
        """"
         Write Hack code for stack arithmetic 'command' (str).
         To be implemented as part of Project 6

         Compiles the arithmetic VM command into the corresponding ASM code. Recall that the operands (one or two, depending on the command) are on the stack and the result of the operation should be placed on the stack.
         The unary and the logical and arithmetic binary operators are simple to compile.
         The three comparison operators (EQ, LT and GT) do not exist in the assembly language. The corresponding assembly commands are the conditional jumps JEQ, JLT and JGT. You need to implement the VM operations using these conditional jumps. You need two labels, one for the true condition and one for the false condition and you have to put the correct result on the stack.
        """

        """
        STACK 
         ...
          x
          y    
SP-->        
        """
        compuation_dict = {
            'add': "@SP, M=M-1, A=M, D=M, A=A-1, M=M+D", #x+y
            'sub': "@SP, M=M-1, A=M, D=M, A=A-1, M=M-D", #x-y
            'neg': "@SP, A=M-1, M=-M", #y=-y
            'and': "@SP, M=M-1, A=M, D=M, A=A-1, M=D&M", #x&y
            'or': "@SP, M=M-1, A=M, D=M, A=A-1, M=D|M",  #x|y
            'not': "@SP, A=M-1, M=!M" #noty
        }

        compare_dict = {
            # JMP conditions
            'eq': "D;JEQ,",  #x=y
            'gt': "D;JGT,",  #x>y
            'lt': "D;JLT,"   #x<y
        }

        if command in compuation_dict:
            code = "//Arithmetic_or_Logical command, " + compuation_dict[command]
            self._WriteCode(code)

        elif command in compare_dict:
            # För att inte få krockande LABELs, alltå "förvirring" i hoppandet
            FALSE_LABEL = self._UniqueLabel()
            TRUE_LABEL = self._UniqueLabel()
            code = "//Arithmetic_or_Logical command, "
            code += ("@SP, M=M-1, A=M, D=M, @13, M=D, @SP, A=M-1, D=M, @13, D=D-M, @" + TRUE_LABEL + ", " + compare_dict[command] + "@SP, A=M-1, M=0, @" + FALSE_LABEL + ", 0;JMP, (" + TRUE_LABEL + "), @SP, A=M-1, M=-1, (" + FALSE_LABEL + ")")
            """
            //For easier readability
            "@SP
            M=M-1
            A=M
            D=M
            @13
            M=D
            @SP
            A=M-1
            D=M
            @13
            D=D-M //x-y
            @TRUE_LABEL
            D;JGT //example
            @SP
            A=M-1
            M=0 //False
            @FALSE_LABEL 
            0;JMP
            (TRUE_LABEL)
            @SP
            A=M-1
            M=-1 //True
            (FALSE_LABEL)
            """
            self._WriteCode(code)

    def WriteInit(self, sysinit = True):
        """
        Write the VM initialization code:
        To be implemented as part of Project 7
        """
        if (debug):
            self.file.write('    // Initialization code\n')
        if sysinit == True:
            code = "@256, D=A, @SP, M=D"
            self._WriteCode(code)
            self.WriteCall("Sys.init", "0")


    def WriteLabel(self, label):
        code = "(" + label + ")"
        self._WriteCode("//label_has_been_written," + code + ",//label_has_been_excecuted")
        """
        Write Hack code for 'label' VM command.
	    To be implemented as part of Project 7
        """

    def WriteGoto(self, label):
        code = "@" + label + ", 0;JMP"
        self._WriteCode("//goto_has_been_written," + code + ",//goto_has_been_excecuted")
        """
        //0;JMP command,
        Write Hack code for 'goto' VM command.
	    To be implemented as part of Project 7
        """

    def WriteIf(self, label):
        #If top of stack is True: -1, JMP if False: 0 continue
        code = "@SP, A=M-1, D=M, @SP, M=M-1, @" + label + ", D;JNE"
        self._WriteCode("//if-goto_has_been_written," + code + ",//if-goto_has_been_excecuted")
        """
        //Uses top of stack, if True JMP if False continue
        Write Hack code for 'if-goto' VM command.
	    To be implemented as part of Project 7
        """
        

    def WriteFunction(self, functionName, numLocals):
        code = "(" + functionName + "),"
        for i in range(int(numLocals)): #Initializes the local variables to zero, pushes numb of nVars onto stack
            code += "@0, D=A, @SP, A=M, M=D, @SP, M=M+1,"
        self._WriteCode("//function_has_been_written," + code + ",//function_has_been_excecuted")
        """
        //Declear a label for the function entry
    (function Name)
        //Initialize the local variables to zero, numLocals of them
        @0
        D=A
        @SP
        A=M
        M=D
        @SP
        M=M+1
        //This should be done nVars times, much easier to fix it in python, loop with JMP conditions in HACK should also be possible
        
        Write Hack code for 'function' VM command.
	    To be implemented as part of Project 7
        """


    def WriteReturn(self):
        code = "//function_return_has_been_written,"
        code += "@LCL, D=M, @13, M=D," #endFrame = LCL //endFrame is a temporary variable, why not just use @LCL, eg. retAddr = *(LCL - 5)
        code += "@5, D=A, @13, A=M-D, D=M, @14, M=D," #retAddr = *(endFrame - 5) //gets the return address, RAM14 = retAddr and RAM13 = endFrame
        code += "@SP, A=M-1, D=M, @SP, M=M-1, @ARG, A=M, M=D," #*ARG=pop()  //Repositions the return value for the caller (stack top), its pop argument 0
        code += "@ARG, D=M, @SP, M=D+1," #SP=ARG+1  //Reposotions SP of the caller
        code += "@13, A=M-1, D=M, @THAT, M=D," #THAT = *(endFrame - 1)   //Restores THAT of the caller
        code += "@2, D=A, @13, A=M-D, D=M, @THIS, M=D," #THIS = *(endFrame - 2)    //Restores THIS of the caller
        code += "@3, D=A, @13, A=M-D, D=M, @ARG, M=D,"  #ARG = *(endFrame - 3)     //Restores ARG of the caller
        code += "@4, D=A, @13, A=M-D, D=M, @LCL, M=D,"  #LCL = *(endFrame - 4)     //Restores LCL of the caller
        code += "@14, A=M, 0;JMP," #goto returnAddress, stored in RAM14, pushed during call command
        code += "//function_return_has_been_excecuted"
        self._WriteCode(code)
        """
        //endFrame = LCL
        @LCL
        D=M
        @endFrame
        M=D
        //retAddr = *(endFrame - 5)
        @endFrame
        A=M
        D=M
        @5
        D=D-A
        @retAddr
        M=D
        //*ARG=pop()
        @SP
        A=M-1
        D=M
        @ARG
        A=M
        M=D
        //SP=ARG-1
        @ARG
        D=M
        @SP
        M=A+1
        //THAT = *(endFrame - 1)
        @endFrame
        A=M
        D=M-1
        @THAT
        M=D
        //THIS = *(endFrame - 2)
        @2
        D=A
        @endFrame
        A=M
        D=M-D
        @THIS
        M=D
        //ARG = *(endFrame - 3)
        @3
        D=A
        @endFrame
        A=M
        D=M-D
        @LCL
        M=D
        //goto return address
        @retaddr
        A=M
        0;JMP
        
        Write Hack code for 'return' VM command.
	    To be implemented as part of Project 7
        """


    def WriteCall(self, functionName, numArgs):
        returnAddress = self._LocalLabel(functionName)
        code = "//function_call_has_been_written,"
        code += "@" + returnAddress + ", D=A, @SP, A=M, M=D, @SP, M=M+1," #Push return address, to which called function returns after execution
        code += "@LCL, D=M, @SP, A=M, M=D, @SP, M=M+1," #Save LCL of the caller
        code += "@ARG, D=M, @SP, A=M, M=D, @SP, M=M+1," #Save ARG of the caller
        code += "@THIS, D=M, @SP, A=M, M=D, @SP, M=M+1," #Save THIS of the caller
        code += "@THAT, D=M, @SP, A=M, M=D, @SP, M=M+1," #Save THAT of the caller
        code += "@SP, D=M, @5, D=D-A, @" + numArgs + ", D=D-A, @ARG, M=D," #Reposition ARG, ARG = SP - 5 - nArgs
        code += "@SP, D=M, @LCL, M=D,"  #Reposition LCL, to push local variabels of called function to
        #BELOW: This is now @Sys.init for function call due to how write init is written
        code += "@" + functionName + ", 0;JMP," #goto functionname (transfers control to the called funtion)
        code += "(" + returnAddress + "),"   #Declear label for the return address
        code += "//function_call_has_been_excecuted"
        self._WriteCode(code)
        """
        //Push return address
        @_LocalLabel //address to which called function returns after execution
        D=A 
        @SP
        A=M
        M=D
        @SP
        M=M+1
        //Save LCL of the caller
        @LCL
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        //Save ARG of the caller
        @ARG
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        //Save THIS of the caller
        @THIS
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        //Save THAT of the caller
        @THAT
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        //Reposition ARG
        @SP
        D=M
        @5
        D=D-A //ARG = SP -5
        @numArgs
        D=D-A //ARG = SP - 5 - nArgs
        @ARG
        M=D
        //LCL = SP
        @SP
        D=M
        @LCL
        M=D
        //goto funtionName
        @functionName
        0;JMP
    (_LocalLabel) //Sets return adress

        White Hack code for 'call' VM command.
	    To be implemented as part of Project 7
        """

    
