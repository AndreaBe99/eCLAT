from rply import ParserGenerator
from ast import Program, Annotation, CodeC


class Parser():
    def __init__(self):
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            ['SLASH', 'STAR', 'AT', 'TABLE', 'OPEN_PAREN', 'CLOSE_PAREN', 'KEY',
                'COMMA', 'VALUE', 'SEMI_COLON', 'IDENTIFIER', 'CCODE']
        )

    def parse(self):
        @self.pg.production('program : statement')
        def program_statement(p):
            return Program(p[0])

        @self.pg.production('program : statement program')  
        def program_statement_program(p):
            if type(p[1]) is Program:
                program = p[1]
            else:
                program = Program(p[1])
            program.add_value(p[0])
            return p[1]    
        
        @self.pg.production('statement : SLASH STAR AT TABLE IDENTIFIER OPEN_PAREN KEY IDENTIFIER COMMA VALUE IDENTIFIER CLOSE_PAREN SEMI_COLON STAR SLASH')
        def statement(p):
            return Annotation(p[4], p[7], p[10])  

        @self.pg.production('statement : CCODE')   
        @self.pg.production('statement : IDENTIFIER')   
        @self.pg.production('statement : SEMI_COLON')  
        @self.pg.production('statement : OPEN_PAREN') 
        @self.pg.production('statement : CLOSE_PAREN') 
        @self.pg.production('statement : COMMA') 
        def statement_ccode(p):
            return CodeC(p[0])

        @self.pg.error
        def error_handle(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
