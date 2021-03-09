from lexer import Lexer
from parser import Parser

text_input = """
int i = 0;
/* @eclat table encap_sid_list_1 {key=IPv6Address,value=Inet6Address[3]}; */
if(i == 0){
	i++;
}
printf("i: %d", i);
"""

class Environment(object):
    def __init__(self):
        self.variables = {}

lexer = Lexer().get_lexer()
tokens = lexer.lex(text_input)

#for token in tokens:
#   print(token)

pg = Parser()
pg.parse()
parser = pg.get_parser()
parser.parse(tokens).eval(Environment())

