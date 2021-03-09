from rply import LexerGenerator

#espressione regolare che considera tutto eccetto i commenti
IGNORE = r'^((?!(\/\*([^*]|[\r\n]|(\*+([^*\/]|[\r\n])))*\*+\/)).*)'

class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
       # self.lexer.add('CCODE', IGNORE)
        self.lexer.add('SLASH', r'/')
        self.lexer.add('STAR', r'\*')
        self.lexer.add('AT', r'@eclat')
        #self.lexer.add('AT', r'@')
        #self.lexer.add('ECLAT', r'eclat')
        self.lexer.add('TABLE', r'table')
        self.lexer.add('OPEN_PAREN', r'\{')
        self.lexer.add('CLOSE_PAREN', r'\}')
        self.lexer.add('KEY', r'key=')
        self.lexer.add('COMMA', r',')
        self.lexer.add('VALUE', r'value=')
        self.lexer.add('SEMI_COLON', r'\;')

        # Identifier
        #### DA RIVEDERE COSA E' AMMESSO E COSA NO ###
        # /* @eclat table encap_sid_list_1 {key=in6_addr,value=sidlist_1}; */  NO, in6_addr non esiste
        # /* @eclat table encap_sid_list_1 {key=in6_addr,value=in6_addr[1]}; */
        # /* @eclat table encap_sid_list_1 {key=int, value=Inet6Address[3]}; */
        # /* @eclat table encap_sid_list_1 {key=IPv6Address,value=IPv6Address}; */   	ok 
        # /* @eclat table encap_sid_list_1 {key=IPv6Address,value=IPv6AddressList}; */   	NO 
        self.lexer.add('IDENTIFIER', r'[_a-zA-Z][_a-zA-Z0-9]*(\[\d+\])*') 
        # Token che non ci interessano
        self.lexer.add('CCODE', r'[-!$%^&*()_+|~=`\{\}\[\]:";<>?,.\/]') 
        self.lexer.add('CCODE', r'\d+') 
        
        # Ignore spaces
        self.lexer.ignore('\s+')


    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
