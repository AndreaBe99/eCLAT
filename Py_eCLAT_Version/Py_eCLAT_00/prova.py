import re

f = open('token.csv', "r")
token_list = []
for line in f:
    if line[0] != '#' and len(line) != 0:
        m = line.split(",")
        token_list.append(m[0][1:(len(m[0])-1)])
        print(m[1].strip("\n") + " d")
        print("self.lexer.add("+ m[0] + "," + m[1].strip("\n") +")")
print(token_list)
