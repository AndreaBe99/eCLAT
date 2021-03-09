from rply import ParserGenerator
from ast import Program, DefineTable, DefineProgram, Def, ChainDeclaration, Chain, Block, Match, ConfigMatchTable, BlockMatchTable, TableElement, StringIPv6, Ipv6, MatchTableElement, Variable, EntryPoint
from lexer import token_list

class Parser():
    def __init__(self):
        self.pg = ParserGenerator(token_list)

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
    
        @self.pg.production('space : ')
        def program_statement(p):
            return p
        
        @self.pg.production('space : SPACE')
        def program_statement(p):
            return p[0]

        @self.pg.production('space : SPACE space')
        def program_statement_program(p):
            return p[1]
        
        ##### Sezione dichiarativa tabelle
        @self.pg.production('statement : TABLE space IDENTIFIER space KEY_TYPE space IDENTIFIER space VALUE_TYPE space IDENTIFIER')
        def statement_defineTable(p):
            return DefineTable(p[2], p[6], p[10])

        
        ##### Sezione dichiarativa chains/programs
        @self.pg.production('statement : PROGRAM space XDP space IDENTIFIER')
        def statement_xdp_program(p):
            return DefineProgram(p[4])
        @self.pg.production('statement : PROGRAM space TC space IDENTIFIER')
        def statement_tc_program(p):
            return DefineProgram(p[4])
        
        ##### Sezione alias
        @self.pg.production('statement : DEF space IDENTIFIER space NUMBER')
        def statement_def(p):
            return Def(Variable(p[2].getstr()), p[4])

        ##### Sezione scrittura chains
        @self.pg.production('statement : CHAIN space XDP space IDENTIFIER space : block')
        def statement_chain(p):
            return ChainDeclaration(p[4], p[len(p)-1])

        @self.pg.production('block : chainElement')
        def block_chainElement(p):
            return Block(p[0])
        @self.pg.production('block : chainElement block')
        def block_chainElement_block(p):
            if type(p[1]) is Block:
                b = p[1]
            else:
                b = Block(p[1])
            if b.get_len() > 7:
                raise Exception("Chain lenght must be less than 7.")
            b.add_statement(p[0])
            return b

        @self.pg.production('chainElement : SPACE SPACE SPACE SPACE IDENTIFIER space HEXADDR')
        @self.pg.production('chainElement : SPACE SPACE SPACE SPACE IDENTIFIER space NUMBER')
        @self.pg.production('chainElement : SPACE SPACE SPACE SPACE IDENTIFIER space IDENTIFIER')
        def chainElement(p):
            return Chain(p[4].getstr(), p[6])
        
        ##### Sezione match 
        @self.pg.production('statement : MATCHTABLE space IDENTIFIER space VALUE_TYPE space IDENTIFIER')
        def statement_match(p):
            return Match(p[2], p[6])

        ##### Sezione popolazione delle matchTable
        @self.pg.production('statement : CONFIG space IDENTIFIER space : blockMatchTable')
        def statement_configMatchTable(p):
            return ConfigMatchTable(p[2], p[len(p)-1])
        
        @self.pg.production('blockMatchTable : blockMatchElement')
        def blockMatchTable_blockMatchElement(p):
            return BlockMatchTable(p[0])
        @self.pg.production('blockMatchTable : blockMatchElement blockMatchTable')
        def blockMatchTable_blockMatchElement_blockMatchTable(p):
            if type(p[1]) is BlockMatchTable:
                b = p[1]
            else:
                b = BlockMatchTable(p[1])
            b.add_statement(p[0])
            return b

        @self.pg.production('blockMatchElement : SPACE SPACE SPACE SPACE KEY space " space IPV6 space " space VALUE space " space IDENTIFIER space "')
        @self.pg.production('blockMatchElement : SPACE SPACE SPACE SPACE KEY space " space IPV6 space " space VALUE space " space stringIPv6 space "')
        #@self.pg.production('blockMatchElement : SPACE SPACE SPACE KEY space " IPV6 " space VALUE space " stringIPv6 "')
        def blockMatchElement(p):
            if type(p[16]) is StringIPv6:
                return TableElement(p[8], p[16])
            elif p[16].gettokentype() == "IDENTIFIER":
                return MatchTableElement(p[8], p[16])
    
            
        @self.pg.production('stringIPv6 : ipv6Element')
        def stringIPv6_ipv6Element(p):
            return StringIPv6(p[0])
        @self.pg.production('stringIPv6 : ipv6Element stringIPv6')
        def stringIPv6_ipv6Element_stringIPv6(p):
            if type(p[1]) is StringIPv6:
                b = p[1]
            else:
                b = StringIPv6(p[1])
            b.add_statement(p[0])
            return b

        @self.pg.production('ipv6Element : IPV6')
        @self.pg.production('ipv6Element : IPV6 space , space')
        def ipv6Element(p):
            return Ipv6(p[0])
        
        @self.pg.production('statement : ENTRYPOINT space IDENTIFIER')
        def statement_configMatchTable(p):
            return EntryPoint(p[1])

        
        #### Error
        @self.pg.error
        def error_handle(token):
            #raise Exception("Error with token: " + token.getstr())
            raise Exception(token)
            #raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
