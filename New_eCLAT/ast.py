import ast
from re import A, S
from rply.token import BaseBox
from integer import Integer
import csv
from random import randint

### CLASSE DI APPOGGIO PER SCRIVERE LE DICHIARAZIONI ###
class Appoggio():
    # dict provvisorio per la funzione Packet
    funzioni = {
        "Packet.readU8": "bpf_ntohs(__READ_PACKET(__u8",
        "Packet.readU16": "bpf_ntohs(__READ_PACKET(__be16",
        "Packet.readU32": "bpf_ntohl(__READ_PACKET(__be32",
        #"Packet.readU64": "bpf_ntohl(__READ_PACKET(__be64",
        "Packet.writeU8": "__WRITE_PACKET(__u8",
        "Packet.writeU16": "__WRITE_PACKET(__u16",
        "Packet.writeU32": "__WRITE_PACKET(__u32",
        #"Packet.writeU64": "__WRITE_PACKET(__u64",
    }
    # variabile per capire se sono o meno all'interno di una funzione
    in_function = False
    # Contatore per l'indentazione del file .c
    indent_level = 0
    # dict contenente le funzioni con associte le variabili in esse contenute
    funzioni_prima_passata = {}
    # dict contenente le variabili globali con associato la stringa #define per il file .c
    variabili_globali_prima_passata = {}
    # Variabile di appoggio in cui viene memorizzato il nome della funzione corrente
    funzione_corrente = ""

###### FUNZIONE PROVVISORIA ########
# Trova il programma nei file se presente.
## mod = 1 per quando faccio hike_call
## mod = 2 per quando faccio l'import e quindi per scrivere i #define 
#### in cui ho bisogno sia del nome che del numero associato
def find_Program(statement, mod):
    result = ''
    with open("csv/eclat_program_list.csv", mode='r') as csv_file:
        string = csv.reader(csv_file, delimiter=';')
        for row in string:
            if statement == row[0]:
                if mod == "1":
                    return row[1]
                if mod == "2":
                    return row[1] + ' ' + row[2]
    with open("csv/regisrty.csv", mode='r') as csv_file:
        string = csv.reader(csv_file, delimiter=';')
        for row in string:
            if statement == row[0]:
                    return row[1]
    raise Exception("\"" + statement +"\" Hike Program/Function not defined")


class Program(BaseBox):
    def __init__(self, statement):
        self.statements = []
        self.statements.append(statement)

    def add_statement(self, statement):
        self.statements.insert(0, statement)

    def eval(self, env):
        result = ""
        output = ""

        # prima passata per "scorrere" le funzioni e le variabili
        prima_passata = ""
        for statement in self.statements:
            prima_passata += statement.get_chain_variables()
        count = 0
    
        # Scrivo tutte le funzioni trovate in un registry con associato un contatore
        with open('csv/regisrty.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            for fun in Appoggio.funzioni_prima_passata:
                writer.writerow([str(fun), str(fun.upper()), str(count)])
                count += 1

        for statement in self.statements:
            result = statement.eval(env)
            output += statement.to_c()

        var = ""
        # Incollo le variabili trovate durante la prima passata
        for var_globale in Appoggio.variabili_globali_prima_passata:
            var += Appoggio.variabili_globali_prima_passata[var_globale]

        # Importo i #define di default e le incollo le variabili globali
        output = "#include <hike_vm.h>\n" + var + output
        print(output)
        # Scrivo il file .c di output
        f = open("output.c", "w")
        f.write(output)
        f.close()

        #print("\nVARIABILI: ")
        #for var in env.variables:
        #    print(var, env.variables[var])
        return result

    def get_statements(self):
        return self.statements


class Block(BaseBox):
    def __init__(self, statement):
        self.statements = []
        self.statements.append(statement)

    def add_statement(self, statement):
        self.statements.insert(0, statement)

    def get_statements(self):
        return self.statements
    
    def eval(self, env):
        result = None
        for statement in self.statements:
            result = statement.eval(env)
        return result
    
    def to_c(self):

        result = ''
        Appoggio.indent_level += 1
        for statement in self.statements:
            result += '\t'*Appoggio.indent_level + statement.to_c() #+ ';'
            if result[-1] != '{' and result[-1] != '}' and result[-1] != ';':
                result += ';'
            result += '\n'

        Appoggio.indent_level -= 1
        return result
    
    def get_chain_variables(self):
        result = ""
        for statement in self.statements:
            if statement.get_chain_variables() != "":
                result += statement.get_chain_variables() + ","  
        return result[:-1]



class Null(BaseBox):
    def eval(self, env):
        return self
    
    def get_chain_variables(self):
        return "Null()"

    def to_c(self):
        #return 'NULL'
        return 'Null()'


class Boolean(BaseBox):
    def __init__(self, value):
        self.value = bool(value)

    def eval(self, env):
        return self.value
    
    def get_chain_variables(self):
        return str(self.value)
    
    def to_c(self):
        return str(self.value)


#class Integer(Integer):
class Integer():
    def __init__(self, value, base):
        self.value = int(value)
        self.base = base

    def eval(self, env):
        return self.value

    def get_chain_variables(self):
        return str(self.value)

    def to_c(self):
        #print()
        if self.base == 16:
            return str(hex(self.value))
        if self.base == 10:
            return str(self.value)


class Float(BaseBox):
    def __init__(self, value):
        self.value = float(value)

    def eval(self, env):
        return self.value
    
    def get_chain_variables(self):
        return str(self.value)

    def to_c(self):
        return str(self.value)


class String(BaseBox):
    def __init__(self, value):
        self.value = str(value)

    def eval(self, env):
        return self.value
    
    def get_chain_variables(self):
        return str(self.value)

    def to_c(self):
        return str(self.value)



class Variable(BaseBox):
    def __init__(self, name):
        self.name = str(name)
        self.value = None
        
    def getname(self):
        return str(self.name)
    
    def eval(self, env):
        if env.variables.get(self.name, None) is not None:
            self.value = env.variables[self.name]
            return self.value
        raise Exception("Not yet defined " + str(self.name))
    
    def get_chain_variables(self):
        return str(self.name)

    def to_c(self):
        if Appoggio.funzione_corrente != "":
            if Appoggio.funzione_corrente in Appoggio.funzioni_prima_passata:
                if self.name in Appoggio.funzioni_prima_passata[Appoggio.funzione_corrente]:
                    return self.name
                if self.name in Appoggio.variabili_globali_prima_passata:
                    return self.name
            raise Exception("Variable \"" + str(self.name) + "\" not declared")
        else:
            if self.name in Appoggio.variabili_globali_prima_passata:
                return self.name
            raise Exception("Variable \"" + str(self.name) + "\" not declared")




class BinaryOperation():
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def eval(self, env):
        if self.operator == '+':
            return self.left.eval(env).__add__(self.right.eval(env))
        elif self.operator == '-':
            return self.left.eval(env).__sub__(self.right.eval(env))
        elif self.operator == '*':
            return self.left.eval(env).__mul__(self.right.eval(env))
        elif self.operator == '/':
            return self.left.eval(env).__div__(self.right.eval(env))
        elif self.operator == '==':
            return self.left.eval(env).__eq__(self.right.eval(env))
        elif self.operator == '!=':
            result = self.left.eval(env).__eq__(self.right.eval(env))
            result.value = not result.value
            return result
        elif self.operator == '>=':
            return self.left.eval(env).__ge__(self.right.eval(env))
        elif self.operator == '<=':
            return self.left.eval(env).__le__(self.right.eval(env))
        elif self.operator == '>':
            return self.left.eval(env).__gt__(self.right.eval(env))
        elif self.operator == '<':
            return self.left.eval(env).__lt__(self.right.eval(env))
        elif self.operator == 'AND':
            one = self.left.eval(env).equals(Boolean(True))
            two = self.right.eval(env).equals(Boolean(True))
            return Boolean(one.value and two.value)
        elif self.operator == 'OR':
            one = self.left.eval(env).equals(Boolean(True))
            two = self.right.eval(env).equals(Boolean(True))
            return Boolean(one.value or two.value)
        ### BITWISE OPERATION #####
        elif self.operator == '&':
            return int(self.left.eval(env)) & int(self.right.eval(env))
        elif self.operator == '|':
            return int(self.left.eval(env)) | int(self.right.eval(env))
        elif self.operator == '^':
            return int(self.left.eval(env)) ^ int(self.right.eval(env))
        elif self.operator == '<<':
            return int(self.left.eval(env)) << int(self.right.eval(env))
        elif self.operator == '>>':
            return int(self.left.eval(env)) >> int(self.right.eval(env))
        else:
            raise Exception("Shouldn't be possible")
    
    def to_c(self):
        return ' ' + self.left.to_c() + ' ' + self.operator + ' ' + self.right.to_c() + ' '
    
    def get_chain_variables(self):
        return ' ' + self.left.get_chain_variables() + ' ' + self.operator + ' ' + self.right.get_chain_variables() + ' '


class Not(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        result = self.value.eval(env)
        if isinstance(result, Boolean):
            return Boolean(not result.value)
        raise LogicError("Cannot 'not' that")

    def to_c(self):
        return 'not%s ' % (self.value.to_c())
    
    def get_chain_variables(self):
        return ""


class BitWise_Not(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        result = self.value.eval(env)
        return ~bin(result.value)
        raise LogicError("Cannot 'not' that")

    def to_c(self):
        return 'BitWise_Not(%s)' % (self.value.to_c())
    
    def get_chain_variables(self):
        return ""



class FromImport(BaseBox):
    def __init__(self, to_co, args):
        self.to_co = to_co
        self.args = args

    def eval(self, env):
        self.args.eval(env)
        #raise LogicError("Cannot assign to this")
    
    def to_c(self):
        result = ''
        for statement in self.args.get_statements():
            result += '#define ' + find_Program(statement, "2") + '\n'
        return result
        return self.args.to_c()
    
    def get_chain_variables(self):
        return ""

class Import(BaseBox):
    def __init__(self, args):
        self.args = args

    def eval(self, env):
        self.args.eval(env)
        #raise LogicError("Cannot assign to this")

    def to_c(self):
        result = ''
        for statement in self.args.get_statements():
            result += '#define ' + find_Program(statement, "2") + '\n'
        return result
    
    def get_chain_variables(self):
        return ""
    
class FunctionDeclaration(BaseBox):
    def __init__(self, name, args, block):
        self.name = name
        self.args = args
        self.block = block

    def eval(self, env):
        self.block.eval(env)
        #raise LogicError("Cannot assign to this")
    
    def to_c(self):
        Appoggio.in_function = True
        Appoggio.funzione_corrente = self.name
        if self.name in Appoggio.funzioni:
            raise Exception(self.name + " function already defined.")
        res = '\n__section("__sec_chain_' + self.name + '")\n'
        res += 'int __chain_' + self.name + '(void) {\n'

        #### Se la funzione ha parametri?
        #result = 'FunctionDeclaration %s (' % self.name
        #if isinstance(self.args, Array):
        #    for statement in self.args.get_statements():
        #        result += ' ' + statement.to_c()
        #result += ')'
        #result += '\t(\n'
        
        Appoggio.indent_level += 1

        ### PASTE VARIABLE
        # Se esistono variabili locali
        if len(Appoggio.funzioni_prima_passata[self.name]) != 0:
            res += Appoggio.indent_level*"\t" + "_s64 " + ', '.join(Appoggio.funzioni_prima_passata[self.name]) + ";"

        return_presente = False
        result = ''
        for statement in self.block.get_statements():
            # Se c'èlo statement RETURN non c'è bisogno di inserirlo
            if statement.to_c().split()[0] == "return":
                return_presente = True
            result += '\n' + '\t'*Appoggio.indent_level + statement.to_c()
            if result[-1] != '{' and result[-1] != '}' and result[-1] != ';':
                result += ';'

        # RETURN statement trovato
        if return_presente:
            result += '\n' + '\t'*Appoggio.indent_level
        # RETURN statement NON trovato metto RETURN XDP_DROP di default
        else:
            result += '\n' + '\t'*Appoggio.indent_level + 'return XDP_ABORTED;'
        result += '\n}\n'

        result = res + result
        Appoggio.indent_level -= 1
        Appoggio.in_function = False
        Appoggio.funzione_corrente = ""
        return result

    def get_chain_variables(self):
        if self.name in Appoggio.funzioni_prima_passata:
            raise Exception("Function \"" + str(self.name) + "\" already exists")
        Appoggio.in_function = True
        result = []
        for statement in self.block.get_statements():
            array_appoggio = statement.get_chain_variables().split(",")
            for var in array_appoggio:
                result.append(var)

        # Elimina eventuali spazi vuoti delle stringhe e i return Null()
        result = [i for i in result if i != "" and i != "Null()"]
        # Elimina eventuali duplicati
        result = list(dict.fromkeys(result))

        Appoggio.funzioni_prima_passata[str(self.name)] = result
        Appoggio.in_function = False
        return str(self.name)


class BinaryOp(BaseBox):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def to_c(self):
        return 'BinaryOp(%s, %s)' % (self.left.to_c(), self.right.to_c())
    
    def get_chain_variables(self):
        return self.left.get_chain_variables() + self.right.get_chain_variables()


    
class Assignment(BinaryOp):
    def eval(self, env):
        if isinstance(self.left, Variable):
            if type(self.right) is BinaryOperation:
                env.variables[self.left.getname()] = self.right.eval(env)
            elif type(self.right) is Variable:
                env.variables[self.left.getname()] = self.right.eval(env)
            else:
                env.variables[self.left.getname()] = self.right.value
            return self.right.eval(env)
            # otherwise raise error
            #raise ImmutableError(self.left.getname())
        else:
            raise LogicError("Cannot assign to this")
    
    def to_c(self):
        # Se sono all'interno di una funzione
        if Appoggio.funzione_corrente != "":
            # Se la funzione è stata dichiarata
            if Appoggio.funzione_corrente in Appoggio.funzioni_prima_passata:
                # prendo le variabili dichiarate al suo interno
                array_variabili = Appoggio.funzioni_prima_passata[Appoggio.funzione_corrente]
                # Se la variabile è stata già dichiarata OK
                if self.left.getname() in array_variabili:
                    return self.left.getname() + ' = ' + self.right.to_c()
                raise Exception("ERROR: Variable not definied")
        # Se sono al di fuori delle funzioni
        else:
            # Se NON è tra le variabili globali già dichiarate
            if not (self.left.getname() in Appoggio.variabili_globali_prima_passata):
                raise Exception("ERROR: Variable \"" + self.left.getname() + "\" not definied")
            else:
                return ""
                # COME VIENE SOVRASCITTO IL VALORE ???
                #Appoggio.variabili_globali_prima_passata[self.left.getname()] = '#define ' + self.left.getname().upper() + ' ' + str(self.right) + '\n'
                #return Appoggio.variabili_globali_prima_passata[self.left.getname()]

    def get_chain_variables(self):
        if not Appoggio.in_function:
            Appoggio.variabili_globali_prima_passata[self.left.getname()] = '#define ' + self.left.getname().upper() + ' ' + str(self.right) + '\n'
        return str(self.left.getname())


class Call(BaseBox):
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.value = 0

    def eval(self, env):
        result = Null()
        return result

    def to_c(self):
        parametri = ''
        param_number = 1
        # Metto i parametri in una stringa di appoggio (parametri)
        for statement in self.args.get_statements():
            param_number += 1
            ### Se è globale ovvero #define occorre fare .upper()
            if statement.to_c() in Appoggio.variabili_globali_prima_passata:
                parametri += ', ' + statement.to_c().upper()
            else: 
                parametri += ', ' + statement.to_c()
        parametri += ')'
        
        if self.name in Appoggio.funzioni:
            # Se corrisponde alla funzione Packet.wtite il primo parametro va assegnato mentre il secondo va tra parentesi
            if self.name[:12] == "Packet.write":
                return Appoggio.funzioni[self.name] + ", " + self.args.get_statements()[1].to_c() + ') = ' + self.args.get_statements()[0].to_c()
            # Se corrisponde alla funzione Packet.read
            if self.name[:11] == "Packet.read":
                return Appoggio.funzioni[self.name] + parametri + ')'
            # Se è una funzione dichiarata nel file eclat
            return 'hike_elem_call_' + str(param_number) + '(' + Appoggio.funzioni[self.name] + parametri
        # Se è una funzione dichiarata all'interno del regisrty o un programma Hike, 
        # la cerco con find_Program che ritorna l'errore se non la trova
        return 'hike_elem_call_' + str(param_number) + '(' + find_Program(self.name, "1") + parametri

    def get_chain_variables(self):
        return ''


class Return(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return self.value.eval(env)

    def to_c(self):
        if self.value.to_c() == "Null()":
            return "return XDP_ABORTED"
        return 'return %s' % (self.value.to_c())

    def get_chain_variables(self):
        return ""



class If(BaseBox):
    def __init__(self, condition, body, else_body=Null()):
        self.condition = condition
        self.body = body
        self.else_body = else_body

    def eval(self, env):
        condition = self.condition.eval(env)
        if condition:
            return self.body.eval(env)
        else:
            if type(self.else_body) is not Null:
                return self.else_body.eval(env)
        return Null()

    def to_c(self):
        result = 'if (' + self.condition.to_c() + ') {\n' + self.body.to_c() + Appoggio.indent_level*'\t' + '}'
        if type(self.else_body) is not Null:
            result += '\n' + Appoggio.indent_level*'\t' +'else {\n' + self.else_body.to_c() + Appoggio.indent_level*'\t' +'}'
        return result
    
    def get_chain_variables(self):
        return self.body.get_chain_variables() + "," + self.else_body.get_chain_variables()


class Else(BaseBox):
    def __init__(self, else_body=Null()):
        self.else_body = else_body

    def eval(self, env):
        return self.else_body.eval(env)

    def to_c(self):    
        #result = '\n' + Appoggio.indent_level*'\t' + 'else {\n' + self.else_body.to_c() + Appoggio.indent_level*'\t' + '}'
        result = self.else_body.to_c()
        return result

    def get_chain_variables(self):
        return self.else_body.get_chain_variables()


class While(BaseBox):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def eval(self, env):
        i = 0
        while True:
            if not self.condition.eval(env):
                break
            i += 1
            self.body.eval(env)
        return Null()

    def to_c(self):
        result = 'while (' + self.condition.to_c() + ') {\n' + self.body.to_c() + Appoggio.indent_level*'\t' + '}'
        return result
    
    def get_chain_variables(self):
        return self.body.get_chain_variables()


class InnerArray(BaseBox):
    def __init__(self, statements=None):
        self.statements = []
        self.values = []
        if statements:
            self.statements = statements

    def push(self, statement):
        self.statements.insert(0, statement)

    def append(self, statement):
        self.statements.append(statement)

    def extend(self, statements):
        self.statements.extend(statements)

    def get_statements(self):
        return self.statements


class Array(BaseBox):
    def map(self, fun, ls):
        nls = []
        for l in ls:
            nls.append(fun(l))
        return nls

    def __init__(self, inner):
        self.statements = inner.get_statements()
        self.values = []

    def get_statements(self):
        return self.statements

    def push(self, statement):
        self.statements.insert(0, statement)

    def append(self, statement):
        self.statements.append(statement)

    def index(self, i):
        if type(i) is Integer:
            return self.values[i.value]
        if type(i) is Float:
            raise LogicError("Cannot index with that value")

    def add(self, right):
        if type(right) is Array:
            result = Array(InnerArray())
            result.values.extend(self.values)
            result.values.extend(right.values)
            return result
        raise LogicError("Cannot add that to array")

    def eval(self, env):
        if len(self.values) == 0:
            for statement in self.statements:
                #self.values.append(statement.eval(env))
                self.values.append(statement)
        return self

    def to_c(self):
        result = '['
        #result += ",".join(self.map(lambda x: x.to_c(), self.statements))
        result += ",".join(self.map(lambda x: x, self.statements))
        result += ']'
        return result

    def to_string(self):
        return '[%s]' % (", ".join(self.map(lambda x: x.to_string(), self.values)))
    
    def get_chain_variables(self):
        return ""
