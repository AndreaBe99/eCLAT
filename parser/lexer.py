from rply import LexerGenerator
import settings
import csv


def getLexer():
    """
    Return the Lexer and a token list
    """
    lg = LexerGenerator()
    
    # List of allowed tokens that the parser will need
    tokens = []

    # Read token name (row[0]) associated with the regular expression (row[1])
    # in a csv file
    with open(settings.TOKEN_MAP_FILE, mode='r') as csv_file:
        str = csv.reader(csv_file, delimiter=';')
        for row in str:
            lg.add(row[0], eval(row[1]))
            tokens.append(row[0])
    tokens.append('$end')
    lg.ignore('[ \t\r\f\v]+')
    return lg.build(), tokens
