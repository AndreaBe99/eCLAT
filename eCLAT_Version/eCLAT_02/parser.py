from rply import ParserGenerator
from ast import *
from lexer import token_list


class Parser():
    def __init__(self):
        self.pg = ParserGenerator(token_list,
        precedence = [
            ('left', ['=']),
            ('left', ['[', ']', ',']),
            ('left', ['IF', ':', 'ELSE', 'END', 'NEWLINE', 'WHILE', ]),
            ('left', ['AND', 'OR', ]),
            ('left', ['NOT', ]),
            ('left', ['==', '!=', '>=', '>', '<', '<=', ]),
            ('left', ['PLUS', 'MINUS', ]),
            ('left', ['MUL', 'DIV', ]),
        ])

    def parse(self):
        @self.pg.production("main : program")
        def main_program(p):
            return p[0]

        @self.pg.production('program : statement_full')
        def program_statement(p):
            return Program(p[0])

        @self.pg.production('program : statement_full program')
        def program_statement_program(p):
            if type(p[1]) is Program:
                program = p[1]
            else:
                program = Program(p[1])
            program.add_statement(p[0])
            return p[1]

        @self.pg.production('block : INDENT blocks DEDENT')
        def block_expr(p):
            return p[1]

        @self.pg.production('blocks : statement_full')
        def blocks_expr(p):
            return Block(p[0])

        @self.pg.production('blocks : statement_full blocks')
        def blocks_expr_block(p):
            if type(p[1]) is Block:
                b = p[1]
            else:
                b = Block(p[1])
            b.add_statement(p[0])
            return b


        @self.pg.production('statement_full : statement NEWLINE')
        @self.pg.production('statement_full : statement $end')
        @self.pg.production('statement_full : statement')
        def statement_full(p):
            return p[0]
        
        @self.pg.production('statement : expression')
        def statement_expr(p):
            return p[0]
        
        @self.pg.production('statement : FROM IDENTIFIER IMPORT arglist')
        def statement_func(p):
            return FromImport(p[1].getstr(), Array(p[3]))
        
        @self.pg.production('statement : IMPORT arglist')
        def statement_func(p):
            return Import(Array(p[1]))

        
        @self.pg.production('arglist : IDENTIFIER')
        #@self.pg.production('arglist : IDENTIFIER ,')
        def arglist_single(p):
            return InnerArray([ p[0].getstr()])
            #return InnerArray([Variable(p[0].getstr())])

        @self.pg.production('arglist : IDENTIFIER , arglist')
        def arglist(p):
            # list should already be an InnerArray
            p[2].push(p[0].getstr())
            #p[2].push(Variable(p[0].getstr()))
            return p[2]
        
        
        
        @self.pg.production('statement : IDENTIFIER = expression')
        def statement_assignment(p):
            return Assignment(Variable(p[0].getstr()), p[2])
        
        
        @self.pg.production('statement : DEF IDENTIFIER ( arglist ) : NEWLINE block ')
        def statement_func(p):
            return FunctionDeclaration(p[1].getstr(), Array(p[3]), p[7])

        @self.pg.production('statement : DEF IDENTIFIER ( ) : NEWLINE block ')
        def statement_func_noargs(p):
            return FunctionDeclaration(p[1].getstr(), Null(), p[6])
        

        ########## GESTIRE INIZIO E FINE BLOCCO IF-ELSE ####################
        
        # @self.pg.production('expression : IF expression : statement_full else_stmt')
        # @self.pg.production('expression : IF expression : statement_full')
        # def expression_if_else_single_line(p):
        #     if len(p) == 5:
        #         return If(condition=p[1], body=p[3], else_body=p[4])
        #     else:
        #        return If(condition=p[1], body=p[3])

        #@self.pg.production('expression : IF expression : statement_full else_stmt')
        #@self.pg.production('expression : IF expression : statement_full')
        @self.pg.production('expression : IF expression : NEWLINE block')
        @self.pg.production('expression : IF expression : NEWLINE block else_stmt')
        def expression_if_else_single_line(p):
            if len(p) == 6:
                return If(condition=p[1], body=p[4], else_body=p[5])
            if len(p) == 5:
                if type(p[4]) is Block:
                    return If(condition=p[1], body=p[4])
                else:
                    return If(condition=p[1], body=p[3], else_body=p[4])
            else:
                return If(condition=p[1], body=p[4])
        
        @self.pg.production('else_stmt : ELSE : statement_full')
        @self.pg.production('else_stmt : ELSE : NEWLINE block')
        def expression_else_stmt(p):
            if len(p) == 3:
                return Else(else_body=p[2])
            else:
                return Else(else_body=p[3])
        ####################################################################

        ########## NEW FUNZIONANTE ##########
        # @self.pg.production('expression : IF expression : NEWLINE block ELSE : NEWLINE block ')
        # @self.pg.production('expression : IF expression : NEWLINE block ')
        # def expression_if_else(p):
        #     if len(p) == 9:
        #         return If(condition=p[1], body=p[4], else_body=p[8])
        #     else:
        #         return If(condition=p[1], body=p[4])

        ########## OLD FUNZIONANTE ##########
        #@self.pg.production('expression : IF expression : NEWLINE INDENT blocks DEDENT')
        #def expression_if(p):
            #return If(condition=p[1], body=p[5])

        #@self.pg.production('expression : IF expression : NEWLINE block ELSE : NEWLINE INDENT blocks DEDENT')
        #def expression_if_else(p):
            #return If(condition=p[1], body=p[4], else_body=p[9])

        
        @self.pg.production('expression : WHILE expression : NEWLINE block ')
        def expression_while(p):
            return While(condition=p[1], body=p[4])
        
        
        @self.pg.production('statement : RETURN')
        def statement_call_args(p):
            return Return(Null())

        @self.pg.production('statement : RETURN expression')
        def statement_call_args(p):
            return Return(p[1])


        
        
        @self.pg.production('expression : const')
        def expression_const(p):
            return p[0]
        
        @self.pg.production('const : FLOAT')
        def expression_float(p):
            # p is a list of the pieces matched by the right hand side of the rule
            return Float(float(p[0].getstr()))

        @self.pg.production('const : BOOLEAN')
        def expression_boolean(p):
            # p is a list of the pieces matched by the right hand side of the rule
            return Boolean(True if p[0].getstr() == 'true' else False)

        @self.pg.production('const : INTEGER')
        def expression_integer(p):
            return Integer(int(p[0].getstr()))
        
        @self.pg.production('const : HEX')
        def expression_integer(p):
            return Integer(int(p[0].getstr(), 16))

        @self.pg.production('const : STRING')
        def expression_string(p):
            return String(p[0].getstr().strip('"\''))
        


        @self.pg.production('expression : IDENTIFIER')
        def expression_call_noargs(p):
            return Variable(p[0].getstr())

        @self.pg.production('expression : IDENTIFIER ( )')
        def expression_call_noargs(p):
            return Call(p[0].getstr(), InnerArray())
        
        @self.pg.production('expression : IDENTIFIER . IDENTIFIER ( )')
        def expression_call_fun_noargs(p):
            return Call(p[0].getstr() + p[1].getstr() + p[2].getstr(), InnerArray())

        @self.pg.production('expression : IDENTIFIER ( expressionlist )')
        def expression_call_args(p):
            return Call(p[0].getstr(), p[2])
        
        @self.pg.production('expression : IDENTIFIER . IDENTIFIER ( expressionlist )')
        def expression_call_fun_noargs(p):
            return Call(p[0].getstr() + p[1].getstr() + p[2].getstr(), p[4])
        
        @self.pg.production('expression : [ expression ]')
        def expression_array_single(p):
            return Array(InnerArray([p[1]]))

        @self.pg.production('expression : [ expressionlist ]')
        def expression_array(p):
            return Array(p[1])

        @self.pg.production('expression : ( expression )')
        def expression_parens(p):
            # in this case we need parens only for precedence
            # so we just need to return the inner expression
            return p[1]

        @self.pg.production('expression : NOT expression ')
        def expression_not(p):
            return Not(p[1])

        # BITWISE OPERATION
        @self.pg.production('expression : ~ expression ')
        def expression_bitwise_not(p):
            return BitWise_Not(p[1])

        @self.pg.production('expression : expression PLUS expression')
        @self.pg.production('expression : expression MINUS expression')
        @self.pg.production('expression : expression MUL expression')
        @self.pg.production('expression : expression DIV expression')
        @self.pg.production('expression : expression != expression')
        @self.pg.production('expression : expression == expression')
        @self.pg.production('expression : expression >= expression')
        @self.pg.production('expression : expression <= expression')
        @self.pg.production('expression : expression > expression')
        @self.pg.production('expression : expression < expression')
        @self.pg.production('expression : expression AND expression')
        @self.pg.production('expression : expression OR expression')
        # BITWISE OPERATION
        @self.pg.production('expression : expression & expression')     # AND
        @self.pg.production('expression : expression PIPE expression')  # OR
        @self.pg.production('expression : expression ^ expression')     # XOR
        @self.pg.production('expression : expression >> expression')    # SHIFT LEFT
        @self.pg.production('expression : expression << expression')    # SHIFT RIGHT
        def expression_binop(p):
            return BinaryOperation(operator=p[1].getstr(), left=p[0], right=p[2])

        @self.pg.production('expressionlist : expression')
        @self.pg.production('expressionlist : expression ,')
        def expressionlist_single(p):
            return InnerArray([p[0]])

        @self.pg.production('expressionlist : expression , expressionlist')
        def arglist(p):
            # expressionlist should already be an InnerArray
            p[2].push(p[0])
            return p[2]
    
        
        
        #### Error
        @self.pg.error
        def error_handle(token):
            raise Exception(token)

    def get_parser(self):
        return self.pg.build()
