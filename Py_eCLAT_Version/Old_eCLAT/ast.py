from rply.token import BaseBox
import ipaddress


class Variable():
    def __init__(self, name):
        self.name = str(name)
        self.value = None

    def getname(self):
        return str(self.name)

    def eval(self, env):
        if env.variables.get(self.name, None) is not None:
            self.value = env.variables[self.name].eval(env)
            return self.value
        print("LogicError: Not yet defined")

    def to_string(self):
        return str(self.name)

class BinaryOp():
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
        
        
class Program():
    def __init__(self, value):
        self.value = []
        self.value.append(value)
    
    def add_value(self, value):
        self.value.insert(0,value)
    
    def eval(self, env):
        print("Statement count: %s" % len(self.value))
        result = None
        for statement in self.value:
            result = statement.eval(env)
            
        #print("VARIABLES:")
        #print(env.variables)
        return result
    
    def get_value(self):
        return self.value


##### Sezione dichiarativa tabelle
class DefineTable():
    def __init__(self, value, key_type, key_value):
        self.value = value
        self.key_type = key_type
        self.key_value = key_value

    def to_string(self):
        return str(self.value)

    def eval(self, env):
        return self.value
    

##### Sezione dichiarativa chains/programs
# Controlla che i programmi siamo presenti nel file "eclat_program_list.txt"
# se presenti crea un variabile d'ambiente con il nome del programma e come valore l' hex number associato
class DefineProgram():
    def __init__(self, value):
        self.value = value

    def to_string(self):
        return str(self.value)

    def eval(self, env):
        f = open('eclat_program_list.txt', "r")
        found = False
        for line in f:
            words = line.split()
            if words[0] == self.value.getstr():
                found = True
                env.variables[self.value.getstr()] = words[1]
        if found == False:
            raise Exception( "Error: " + self.value.getstr() + " is not present in eclat_program_list.txt.")
        return self.value


##### Sezione alias
# Crea una variabile d'ambiente con il nome e il valore associato
class Def(BinaryOp):
    def to_string(self):
        return str(self.right.name)

    def eval(self, env):
        if isinstance(self.left, Variable):
            if env.variables.get(self.left.getname(), None) is None:
                env.variables[self.left.getname()] = self.right
                return self.right
            else:
                raise Exception("ImmutableError")
        else:
            raise Exception("LogicError: Cannot assign to this")

    
##### Sezione scrittura chains
# Per ogni blocco chain crea una variabile con nome "chainNameObj" seguito da 
# un numero incrementale e il valore corrisponde all' oggetto Chain
class ChainDeclaration():
    def __init__(self, chainName, block):
        self.chainName = chainName
        self.block = block

    def to_string(self):
        return str(self.chainName)

    def eval(self, env):
        print("     Name: " + self.chainName.getstr())
        ChainCount().up_count()
        env.variables["chainNameObj" + str(ChainCount().get_count())] = ChainObj(self.chainName.getstr())
        self.block.eval(env)
    
class Block():
    def __init__(self, statement):
        self.statements = []
        self.statements.append(statement)

    def add_statement(self, statement):
        self.statements.insert(0, statement)

    def get_statements(self):
        return self.statements

    def get_len(self):
        return len(self.statements)

    def eval(self, env):
        print("Chain Block count: %s" % len(self.statements))
        result = None
        for statement in self.statements:
            result = statement.eval(env)
        return result

# Prende l'oggetto chain tramite l'ultima variabile d'ambiente 
# e aggiunge alla lista dell'oggetto gli statement all'interno del blocco chain
class Chain():
    def __init__(self, program, value):
        self.program = program
        self.value = value

    def to_string(self):
        return str(self.value)

    def eval(self, env):
        print("         Program: " + self.program + "  Value: " + self.value.getstr())
        chain_obj = env.variables["chainNameObj" + str(ChainCount().get_count())]
        program_list = chain_obj.get_program_list()
        program_list.append(env.variables[self.program] + " " + self.value.getstr())
        env.variables["chainNameObj" + str(ChainCount().get_count())].set_program_list(program_list)
        return self.value   

 ##### Sezione match
 # Controlla se è presente la tabella nel file "eclat_table_list.txt"
class Match():
    def __init__(self, value, block):
        self.value = value
        self.block = block

    def to_string(self):
        return str(self.value)

    def eval(self, env):
        f = open('eclat_table_list.txt', "r")
        found = False
        for line in f:
            if line == self.value.getstr():
                found = True
        if found == False:
            raise Exception( "Error: " + self.value.getstr() + " is not present in eclat_table_list.txt.")
        return self.value


 ##### Sezione popolazione delle matchTable
 # Crea una variabile d'ambiente con nome tableName e valore il nome della tabella
class ConfigMatchTable():
    def __init__(self, value, block):
        self.value = value
        self.block = block

    def to_string(self):
        return str(self.value)

    def eval(self, env):
        env.variables["tableName"] = self.value.getstr()
        self.block.eval(env)
        #return self.value

class BlockMatchTable():
    def __init__(self, statement):
        self.statements = []
        self.statements.append(statement)

    def add_statement(self, statement):
        self.statements.insert(0, statement)

    def get_statements(self):
        return self.statements

    def get_len(self):
        return len(self.statements)

    def eval(self, env):
        print("Popolazione delle Matchtable Block count: %s" % len(self.statements))
        result = None
        for statement in self.statements:
            result = statement.eval(env)
        # elimino la variabile tableName nel caso venisse dischiarato un ulteriore 
        # blocco ConfigMatchTable
        env.variables.pop('tableName')
        return result


class TableElement():
    def __init__(self, value, ipv6):
        self.value = value
        self.ipv6 = ipv6

    def to_string(self):
        return str(self.value)

    def eval(self, env):
        #env.variables["key"] = self.value.getstr()
        print("     KEY: " + self.value.getstr())
        #print("IPv6: " + self.ipv6.getstr())
        self.ipv6.eval(env)
        return self.value


class StringIPv6():
    def __init__(self, statement):
        self.statements = []
        self.statements.append(statement)

    def add_statement(self, statement):
        self.statements.insert(0, statement)

    def get_statements(self):
        return self.statements

    def get_len(self):
        return len(self.statements)

    def eval(self, env):
        #print("Chain Block count: %s" % len(self.statements))
        result = None
        for statement in self.statements:
            result = statement.eval(env)
        return result


class Ipv6():
    def __init__(self, value):
        self.value = value

    def to_string(self):
        return str(self.value)

    def eval(self, env):
        print("         IPV6: " + self.value.getstr())
        return self.value


# Per ogni statement della match table crea un file con nome corrispondente a 
# quello della chain chiamando la funzione "write_match_table"
class MatchTableElement():
    def __init__(self, ipv6, chain):
        self.ipv6 = ipv6
        self.chain = chain

    def to_string(self):
        return str(self.ipv6)
     
    def eval(self, env):
        found = False
        # Controllo se i nomi delle chain corrispondono alle chain definite
        for i in range(ChainCount().get_count()):
            chain = env.variables["chainNameObj" + str(i+1)]
            if chain.get_name() == self.chain.getstr():
                found = True
        if found:
            print("     IPv6: " + self.ipv6.getstr())
            print("         Chain: " + self.chain.getstr())
            # Controllo che non ci siano chain con lo stesso nome
            if env.variables.get(self.chain.getstr(), None) is None:
                env.variables[self.chain.getstr()] = self.chain
                f = open(self.chain.getstr() + ".txt","w+")
                write_match_table(env, self.chain, self.ipv6, f)
                f.close()
            else:
                raise Exception("You cannot give the same name to multiple chains")
        else:
            raise Exception("The chain with name " + self.chain.getstr() + " has not been defined")


class EntryPoint():
    def __init__(self, value):
        self.value = value

    def to_string(self):
        return str(self.value)

    def eval(self, env):
        return self.value
        
# Funzione che si occupa di scrivere il file          
def write_match_table(env, chainName, chainIpv6, f):
    for i in range(ChainCount().get_count()):
        chain = env.variables["chainNameObj" + str(i+1)]
    #for chain in chain_list:
        if chain.get_name() == chainName.getstr():
            f.write("bpftool map update\n")
            f.write("        pinned /sys/fs/bpf/ebpfgen/"+ env.variables["tableName"] + "\n")
            
            ## WRITE KEY
            f.write("        key   hex ")
            addr = ipaddress.ip_address(chainIpv6.getstr())
            # replace ':' and insert ' '
            s = addr.exploded.replace(':','')
            s = ' '.join([s[i:i+2] for i in range(0, len(s), 2)])
            # Write ipv6
            f.write(s + "\n")    
            
            ## WRITE PROGRAM
            f.write("        value hex 00 00 ")
            program_list = chain.get_program_list()
            i = 0
            for program in program_list:
                i = i +1
                value = program.split()
                f.write(value[0][2:] + " ")
                string = value[1]
                if string[:2] == "0x":
                    num = string[2:]
                    if len(num) == 1:
                        num = '0'+ num
                    f.write(num + " ")
                elif not string.isnumeric():
                    f.write(stringToHex(env.variables[string].getstr()) + " ")
                else:
                    f.write(stringToHex(string) + " ")
            
            ## Scrive i restanti 00 o ff ff         
            if i < 7:
                f.write("ff ff ")
            if i == 7:
                f.close()
            # 6 = 8-2 - 1x[00 00] and 1x[ff ff]
            for j in range (6 - i):
                f.write("00 00 ")
            f.write("\n")
                
def stringToHex(s):
    num = hex(int(s))
    num = num[2:]
    if len(num) == 1:
        num = '0'+ num
    return num

# Contuer for ChainDeclaration
class ChainCount():
    count = 0
    def get_count(self):
        return self.id 
    def up_count(self):
        ChainCount.count += 1
    def __init__(self):
        self.id = ChainCount.count

# Oggetto Chain da memorizzare nelle variabili
class ChainObj():
    def __init__(self, name):
        self.name = name
        self.ipv6 = None
        self.program_list = []
        
    def set_name(self, name):
        self.name = name
    def get_name(self):
        return self.name
    
    def set_ipv6(self, ipv6):
        self.ipv6 = ipv6
    def get_ipv6(self):
        return self.ipv6
    
    def set_program_list(self, program_list):
        self.program_list = program_list
    def get_program_list(self):
        return self.program_list
