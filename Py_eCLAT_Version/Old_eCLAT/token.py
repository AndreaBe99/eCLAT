##### Simboli
#self.lexer.add('{', r'\{')
#self.lexer.add('}', r'\}')
self.lexer.add(',', r',')
self.lexer.add('"', r'"|\'')
#self.lexer.add(';', r';')
self.lexer.add(':', r':')
#self.lexer.add('=', r'=')

##### Sezione dichiarativa tabelle
self.lexer.add('TABLE', r'table(?!\w)')
self.lexer.add('KEY_TYPE', r'key_type(?!\w)')
self.lexer.add('VALUE_TYPE', r'value_type(?!\w)')

##### Sezione scrittura tabelle
self.lexer.add('CONFIG', r'config(?!\w)')
self.lexer.add('KEY', r'key(?!\w)')
self.lexer.add('VALUE', r'value(?!\w)')
        
##### Sezione dichiarativa chains/programs
self.lexer.add('PROGRAM', r'program(?!\w)')
self.lexer.add('XDP', r'xdp(?!\w)')
self.lexer.add('TC', r'tc(?!\w)')

##### Sezione alias
self.lexer.add('DEF', r'def(?!\w)')
        
##### Sezione scrittura chain
self.lexer.add('CHAIN', r'chain(?!\w)')
# xdp
#self.lexer.add('TRIGGER', r'trigger(?!\w)')
#self.lexer.add('IPV6_DA', r'ipv6_da(?!\w)')
self.lexer.add('IPV6', IPV6ADDR)
##### Sezione match
self.lexer.add('MATCHTABLE', r'matchtable(?!\w)')
#key_type
self.lexer.add('ENTRYPOINT', r'entrypoint(?!\w)')
#### Popolazione delle matchtable
# config
# paren_open/paren_close
# key_equal
# value_equal
# semi_colon

# Hex-Add
self.lexer.add('HEXADDR', HEXADDR)  
# Number
self.lexer.add('NUMBER', r'\d+')
# Identifier
self.lexer.add('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*')

#self.lexer.add('NEWLINE', r'\n')
#self.lexer.add('TAB', r'[\t]')
self.lexer.add('SPACE', r' ')

