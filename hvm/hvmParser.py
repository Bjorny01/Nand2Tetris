"""
hvmParser.py -- Parser class for Hack VM translator
"""

from hvmCommands import *

class Parser(object):
    def __init__(self, sourceName, comments=None):
        """
        Open 'sourceFile' and gets ready to parse it.
        """
        self.file = open(sourceName, 'r');
        self.lineNumber = 0
        self.line = ''
        self.rawline = ''
        self.comments = comments

    def Advance(self):
        """
        Reads the next command from the input and makes it the current
        command.
        Returns True if a command was found, False at end of file.
        """
        while True:
            if self.file:
                self.rawline = self.file.readline()
                if len(self.rawline) == 0:
                    return False
                self.rawline = self.rawline.replace('\n', '')
                self.line = self.rawline
                i = self.line.find('//')                
                if i != -1:
                    if self.comments:
                        self.comments.Write('    '+self.line[i:])
                    self.line = self.line[:i]
                self.line = self.line.replace('\t', ' ').strip()
                if len(self.line) == 0:
                    continue
                self._Parse()
                return True
            else:
                return False

    def CommandType(self):
        """
        Returns the type of the current command:
            C_ARITHMETIC = 1
            C_PUSH = 2
            C_POP = 3
            C_LABEL = 4
            C_GOTO = 5
            C_IF = 6
            C_FUNCTION = 7
            C_RETURN = 8
            C_CALL = 9
        """
        return self.commandType
		
    def Arg1(self):
        """
        Returns the command's first argument.
        """
        return self.arg1

    def Arg2(self):
        """
        Returns the command's second argument.
        """
        return self.arg2

    """
    The function to be implemented. 
	For Project 6 the function should parse PUSH/POP and the arithmetic commands.
	Parses the current comment. Assumes that there is a single whitespace between the command and between each argument (there can be up to 2 arguments). 
	Fills in 'commandType', 'arg1' and 'arg2'.
    Some examples:
---------------------------------------------------------------------
|        currentLine	-> desired contents							|
---------------------------------------------------------------------
| "push constant 2"		            -> arg1="constant", arg2=2		    |
| "and"					            -> arg1="and", arg2=0			    |
| "label yourLabel"			        -> arg1="yourLabel", arg2=0	        | <-- Not a arithmetic/logic or memory command? We have to parse the others as well?
| "goto yourLabel"		            -> arg1="yourLabel", arg2=0		    |
| "if-goto yourLabel"               -> arg1="yourLabel", arg2=0	        |
| "function funtionName nVars"		-> arg1="funtionName", arg2=nVars	|
| "call funtionName nArgs"		    -> arg1="funtionName", arg2=nArgs   |
| "return"		                    -> arg1=0, arg2=0		            |
---------------------------------------------------------------------
    PUSH and POP parsed as example. Other solutions are encouraged.
    """

    def _Parse(self):

        # command [arg1 [arg2]]
        self.commandType = None  #this should store the type of the command
        self.arg1 = None         #this should store the first argument of the command (if there is a first argument)
        self.arg2 = None         #this should store the second argument of the command (if there is a second argument)

        Parts = self.line.split()
        if Parts[0] == "push":
            self.commandType = C_PUSH
            self.arg1 = Parts[1]
            if len(Parts) > 2:
                self.arg2 = Parts[2]
            else:
                self.arg2 = 0

        elif Parts[0] == "pop":
            self.commandType = C_POP
            self.arg1 = Parts[1]
            if len(Parts) > 2:
                self.arg2 = Parts[2]
            else:
                self.arg2 = 0

        elif Parts[0] in T_ARITHMETIC:
            self.commandType = C_ARITHMETIC
            self.arg1 = Parts[0]
            self.arg2 = 0

        elif Parts[0] == "call":
            self.commandType = C_CALL
            self.arg1 = Parts[1]
            self.arg2 = Parts[2]

        elif Parts[0] == "function":
            self.commandType = C_FUNCTION
            self.arg1 = Parts[1]
            self.arg2 = Parts[2]

        elif Parts[0] == "if-goto":
            self.commandType = C_IF
            self.arg1 = Parts[1]
            self.arg2 = 0

        elif Parts[0] == "goto":
            self.commandType = C_GOTO
            self.arg1 = Parts[1]
            self.arg2 = 0

        elif Parts[0] == "return":
            self.commandType = C_RETURN
            self.arg1 = 0
            self.arg2 = 0

        elif Parts[0] == "label":
            self.commandType = C_LABEL
            self.arg1 = Parts[1]
            self.arg2 = 0



