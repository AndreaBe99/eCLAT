import sys
from lex import *

# Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()    # Call this twice to initialize current and peek.

   # Return true if the current token matches.
    def checkToken(self, kind):
        return kind == self.curToken.kind

    # Return true if the next token matches.
    def checkPeek(self, kind):
        return kind == self.peekToken.kind

    # Try to match current token. If not, error. Advances the current token.
    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()

    # Advances the current token.
    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()
        # No need to worry about passing the EOF, lexer handles that.

    def abort(self, message):
        sys.exit("Error. " + message)
    
    
    
    # Production rules.

    # program ::= {statement}
    def program(self):
        print("PROGRAM")

        # Parse all the statements in the program.
        while not self.checkToken(TokenType.EOF):
            self.statement()
    
    
    # One of the following statements...
    def chain_block(self):
        # IDENTIFIER NUMBER
        if self.checkToken(TokenType.IDENT):
            self.nextToken()
            if self.checkToken(TokenType.NUMBER):
                self.nextToken()
                print("         STATEMENT-PROGRAM_NUMBER")
            elif self.checkToken(TokenType.IDENT):
                self.nextToken()
                print("         STATEMENT-PROGRAM_IDENT")
            elif self.checkToken(TokenType.HEX):
                self.nextToken()
                print("         STATEMENT-PROGRAM_HEX")
        else:
            # Expect an expression.
            self.expression()
        
        # Newline.
        self.nl()
    
    # One of the following statements...
    def config_block(self):
        # KEY " IPV6 " VALUE " IDENT "
        if self.checkToken(TokenType.KEY):
            self.nextToken()
            if self.checkToken(TokenType.STRING):
                self.nextToken()
                if self.checkToken(TokenType.VALUE):
                    self.nextToken()
                    if self.checkToken(TokenType.STRING):
                        self.nextToken()
                        print("         STATEMENT-CONFIG_VALUE")
        else:
            # Expect an expression.
            self.expression()
        
        # Newline.
        self.nl()
    
    
    
    # One of the following statements...
    def statement(self):
        # Check the first token to see what kind of statement this is.
        
        # TABLE IDENT KEY_TYPE IDENT VALUE_TYPE IDENT nl
        if self.checkToken(TokenType.TABLE):
            self.nextToken()
            if self.checkToken(TokenType.IDENT):
                self.nextToken()
                if self.checkToken(TokenType.KEY_TYPE):
                    self.nextToken()
                    if self.checkToken(TokenType.IDENT):
                        self.nextToken()
                        if self.checkToken(TokenType.VALUE_TYPE):
                            self.nextToken()
                            if self.checkToken(TokenType.IDENT):
                                self.nextToken()
                                print("     STATEMENT-TABLE")
            else:
                # Expect an expression.
                self.expression()

        # PROGRAM XDP IDENT nl
        elif self.checkToken(TokenType.PROGRAM):
            self.nextToken()
            if self.checkToken(TokenType.XDP):
                self.nextToken()
                if self.checkToken(TokenType.IDENT):
                    self.nextToken()
                    print("     STATEMENT-PROGRAM")
            else:
                # Expect an expression.
                self.expression()
        
        # DEF IDENT NUMBER nl
        elif self.checkToken(TokenType.DEF):
            self.nextToken()
            if self.checkToken(TokenType.IDENT):
                self.nextToken()
                if self.checkToken(TokenType.NUMBER):
                    self.nextToken()
                    print("     STATEMENT-DEF")
            else:
                # Expect an expression.
                self.expression()
        
        # ENTRYPOINT IDENT nl
        elif self.checkToken(TokenType.ENTRYPOINT):
            self.nextToken()
            if self.checkToken(TokenType.IDENT):
                self.nextToken()
                print("     STATEMENT-ENTRYPOINT")
            else:
                # Expect an expression.
                self.expression()
        
        
        # CHAIN  XDP IDENT : {block} ENDCHAIN'
        elif self.checkToken(TokenType.CHAIN):
            print("     STATEMENT-CHAIN")
            self.nextToken()
            if self.checkToken(TokenType.XDP):
                self.nextToken()
                if self.checkToken(TokenType.IDENT):
                    self.nextToken()
            #self.comparison()

            self.match(TokenType.TWOPOINT)
            self.nl()

            # Zero or more statements in the body.
            while not self.checkToken(TokenType.ENDCHAIN):
                self.chain_block()

            self.match(TokenType.ENDCHAIN)
        
        # CONFIG IDENT : {block} ENDCHAIN'
        elif self.checkToken(TokenType.CONFIG):
            print("     STATEMENT-CONFIG")
            self.nextToken()
            if self.checkToken(TokenType.IDENT):
                self.nextToken()
            #self.comparison()

            self.match(TokenType.TWOPOINT)
            self.nl()

            # Zero or more statements in the body.
            while not self.checkToken(TokenType.ENDCONFIG):
                self.config_block()

            self.match(TokenType.ENDCONFIG)

        # Newline.
        self.nl()
    
    # nl ::= '\n'+
    def nl(self):
        #print("NEWLINE")
		
        # Require at least one newline.
        self.match(TokenType.NEWLINE)
        # But we will allow extra newlines too, of course.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()