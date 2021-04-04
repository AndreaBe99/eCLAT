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
        
        "Packet.readU8": "hike_packet_read_u8(",
        "Packet.readU16": "hike_packet_read_u16(",
        #"Packet.readU64": "bpf_ntohl(__READ_PACKET(__be64",
        "Packet.writeU8": "hike_packet_write_u8(",
        "Packet.writeU16": "hike_packet_write_u16(",
        #"Packet.writeU32": "__WRITE_PACKET(__u32",
        #"Packet.writeU64": "__WRITE_PACKET(__u64",
    }
    
    in_function = False             # variabile per capire se sono o meno all'interno di una funzione
    indent_level = 0                # Contatore per l'indentazione del file .c
    funzioni_alias = {}             # dict per gli Alias quando assegno una funzione ad un parametro
    funzioni_variabili_locali = {}  # dict costruito alla PRIMA PASSATA contenente le funzioni con associte le variabili in esse contenute
    funzioni_parametri_locali = {}  # dict costruito alla PRIMA PASSATA contenente le funzioni con associte i parametri in esse contenute
    funzioni_call_locali = {}       # dict per memorizzare le call create in una funzione
    variabili_globali = {}          # dict contenente le variabili globali con associato la stringa #define per il file .c
    funzione_corrente = ""          # Variabile di appoggio in cui viene memorizzato il nome della funzione corrente
    funzioni_eclat = {}             # dict delle Funzioni prese dal file eclat_program_list
    funzioni_registry = {}          # dict delle Funzioni prese dal file regisrty

###### FUNZIONE PROVVISORIA ########
# Trova il programma nei file se presente.
def find_Program(statement):
    if statement in Appoggio.funzioni_eclat:
        return str(Appoggio.funzioni_eclat[statement][0]) + " " + str(Appoggio.funzioni_eclat[statement][1])
    if statement in Appoggio.funzioni_registry:
        return str(Appoggio.funzioni_registry[statement][0])
    raise Exception("\"" + statement +"\" Hike Program/Function not defined")


class Program(BaseBox):
    def __init__(self, statement):
        self.statements = []
        self.statements.append(statement)

    def add_statement(self, statement):
        self.statements.insert(0, statement)

    def eval(self, env):
        # SALVO I PROGRAMMI DI eclat_program_list.csv IN UN DICT PER COMODITA'
        with open("csv/eclat_program_list.csv", mode='r') as csv_file:
            string = csv.reader(csv_file, delimiter=';')
            for row in string:
                Appoggio.funzioni_eclat[row[0]] = [row[1], row[2]]

        # prima passata per "scorrere" le funzioni e le variabili
        prima_passata = ""
        for statement in self.statements:
            prima_passata += statement.prima_passata()

        # CONTATORE DI INIZIO PER I #DEFINE, PROVVISORIO
        count = 64
        # Scrivo tutte le funzioni trovate in un registry e nel dict con associato un contatore
        funzioni = ""
        with open('csv/regisrty.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            for fun in Appoggio.funzioni_variabili_locali:
                funzioni += "#define " + str(fun.upper()) + " " + str(count) + "\n"
                Appoggio.funzioni_registry[fun] = [fun.upper(), count]
                writer.writerow([str(fun), str(fun.upper()), str(count)])
                count += 1

        
        result = ""  # SIMULAZIONE ESECUZIONE
        output = ""  # CONVERTO IN .C
        for statement in self.statements:
            result = statement.eval(env)
            output += statement.to_c()

        # Incollo le variabili trovate durante la prima passata
        variabili_globali = ""
        for variabile_globale in Appoggio.variabili_globali:
            variabili_globali += Appoggio.variabili_globali[variabile_globale]

        # Importo i #define di default e incollo (in ordine):
        # - le funzioni (chain) dichiaratee
        # - le variabili globali
        # - il codice .c calcolato
        output = "#include <hike_vm.h>\n" + funzioni + variabili_globali + output
        print(output)
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
        result = ""
        for statement in self.statements:
            result = statement.eval(env)
        return result

    def to_c(self):
        result = ''
        Appoggio.indent_level += 1
        for statement in self.statements:
            result += '\t'*Appoggio.indent_level + statement.to_c()
            if result[-1] != '{' and result[-1] != '}' and result[-1] != ';':
                result += ';'
            result += '\n'

        Appoggio.indent_level -= 1
        return result

    def prima_passata(self):
        result = ""
        for statement in self.statements:
            if statement.prima_passata() != "":
                result += statement.prima_passata() + ","
        return result[:-1]



class Null(BaseBox):
    def eval(self, env):
        return self

    def prima_passata(self):
        return "Null()"

    def to_c(self):
        #return 'NULL'
        return 'Null()'


class Boolean(BaseBox):
    def __init__(self, value):
        self.value = bool(value)

    def eval(self, env):
        return self.value

    def prima_passata(self):
        return str(self.value)

    def to_c(self):
        if self.value:
            return "1"
        else:
            return "0"


#class Integer(Integer):
class Integer():
    def __init__(self, value, base):
        self.value = int(value)
        self.base = base

    def eval(self, env):
        return self.value

    def prima_passata(self):
        return str(self.value)

    def to_c(self):
        # Per gestire le basi
        if self.base == 16:
            return str(hex(self.value))
        if self.base == 10:
            return str(self.value)


class Float(BaseBox):
    def __init__(self, value):
        self.value = float(value)

    def eval(self, env):
        return self.value

    def prima_passata(self):
        return str(self.value)

    def to_c(self):
        return str(self.value)


class String(BaseBox):
    def __init__(self, value):
        self.value = str(value)

    def eval(self, env):
        return self.value

    def prima_passata(self):
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

    def prima_passata(self):
        return str(self.name)

    def to_c(self):
        # Se sono all'interno di una funzione
        if Appoggio.funzione_corrente != "":
            if Appoggio.funzione_corrente in Appoggio.funzioni_variabili_locali:
                if self.name in Appoggio.funzioni_variabili_locali[Appoggio.funzione_corrente]:
                    return self.name
                if self.name in Appoggio.funzioni_parametri_locali[Appoggio.funzione_corrente]:
                    return self.name
            if self.name in Appoggio.variabili_globali:
                return self.name
            raise Exception("Variable \"" + str(self.name) + "\" not declared")
        else:
            if self.name in Appoggio.variabili_globali:
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

    def prima_passata(self):
        return ' ' + self.left.prima_passata() + ' ' + self.operator + ' ' + self.right.prima_passata() + ' '


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

    def prima_passata(self):
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

    def prima_passata(self):
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
            result += '#define ' + find_Program(statement) + '\n'
        return result
        return self.args.to_c()

    def prima_passata(self):
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
            result += '#define ' + find_Program(statement) + '\n'
        return result

    def prima_passata(self):
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
        #res = '\n__section("__sec_chain_' + self.name + '")\n'
        #res += 'int __chain_' + self.name + '(void) {\n'
        res = "\nHIKE_CHAIN(" + find_Program(self.name)

        #### Se la funzione ha parametri?
        i = 1
        if isinstance(self.args, Array):
            for statement in self.args.get_statements():
                if i > 4:
                    raise Exception("You can only pass 4 parameters")
                res += ', __s64 ' + statement
                i += 1
        #result += '\t(\n'
        res += ") {\n"
        Appoggio.indent_level += 1

        ### PASTE VARIABLE
        # Se esistono variabili locali
        if len(Appoggio.funzioni_variabili_locali[self.name]) != 0:
            res += Appoggio.indent_level*"\t" + "__s64 " + ', '.join(Appoggio.funzioni_variabili_locali[self.name]) + ";"

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
            result += '\n' + '\t'*Appoggio.indent_level + 'return 0;'
        result += '\n}\n'

        result = res + result
        Appoggio.indent_level -= 1
        Appoggio.in_function = False
        Appoggio.funzione_corrente = ""
        return result

    def prima_passata(self):
        # Controllo se sia già stata dichiarata
        if self.name in Appoggio.funzioni_variabili_locali:
            raise Exception("Function \"" + str(self.name) + "\" already exists")

        Appoggio.in_function = True
        Appoggio.funzione_corrente = self.name

        ##### Metto i parametri in un dict
        array_parametri = []
        if isinstance(self.args, Array):
            for statement in self.args.get_statements():
                array_parametri.append(statement)
        Appoggio.funzioni_parametri_locali[self.name] = array_parametri

        ##### Metto le variabili locali in un dict 
        result = []
        for statement in self.block.get_statements():
            array_appoggio = statement.prima_passata().split(",")
            for var in array_appoggio:
                # Nel caso in cui sia un parametro
                if not var in Appoggio.funzioni_parametri_locali[self.name]:
                    result.append(var)
        # Elimina eventuali spazi vuoti delle stringhe e i return Null()
        result = [i for i in result if i != "" and i != "Null()"]
        # Elimina eventuali duplicati
        result = list(dict.fromkeys(result))
        Appoggio.funzioni_variabili_locali[str(self.name)] = result

        Appoggio.in_function = False
        Appoggio.funzione_corrente = ""
        return str(self.name)


class BinaryOp(BaseBox):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def to_c(self):
        return 'BinaryOp(%s, %s)' % (self.left.to_c(), self.right.to_c())

    def prima_passata(self):
        return self.left.prima_passata() + self.right.prima_passata()



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
        # Se la parte destra è una Call
        if type(self.right) is Call:
            # Se corrisponde ad una Packet.read
            if self.right.name[:11] == "Packet.read":
                return Appoggio.funzioni[self.right.name] + "&" + self.left.getname() + self.right.to_c()

        # Se sono all'interno di una funzione
        if Appoggio.funzione_corrente != "":
            # Se la funzione è stata dichiarata
            if Appoggio.funzione_corrente in Appoggio.funzioni_variabili_locali:
                # prendo le variabili e i parametri dichiarati al suo interno
                array_variabili = Appoggio.funzioni_variabili_locali[Appoggio.funzione_corrente]
                array_parametri = Appoggio.funzioni_parametri_locali[Appoggio.funzione_corrente]
                # Se la variabile è stata già dichiarata OK
                if self.left.getname() in array_variabili or self.left.getname() in array_parametri:
                    return self.left.getname() + ' = ' + self.right.to_c()
                raise Exception("ERROR: Variable not definied")
        # Se sono al di fuori delle funzioni
        else:
            # Se NON è tra le variabili globali già dichiarate
            if not (self.left.getname() in Appoggio.variabili_globali):
                raise Exception("ERROR: Variable \"" + self.left.getname() + "\" not definied")
            else:
                return ""
                # COME VIENE SOVRASCITTO IL VALORE ???
                #Appoggio.variabili_globali[self.left.getname()] = '#define ' + self.left.getname().upper() + ' ' + str(self.right) + '\n'
                #return Appoggio.variabili_globali[self.left.getname()]

    def prima_passata(self):
        # Se la parte destra è una call significa che sto facendo una ALIAS
        if type(self.right) is Call:
            chiavi = Appoggio.funzioni_alias.keys()
            if self.left.getname() in chiavi:
                Appoggio.funzioni_alias[self.left.getname()].append(self.right.name)
            else:
                Appoggio.funzioni_alias[self.left.getname()] = [self.right.name]
                
            # Elimina eventuali duplicati
            Appoggio.funzioni_alias[self.left.getname()] = list(dict.fromkeys(Appoggio.funzioni_alias[self.left.getname()]))

        # Se sono al di fuori di una chain significa che sto dichiarando una variabile globale
        # perciò la metto dentro l'apposito dict
        if not Appoggio.in_function:
            Appoggio.variabili_globali[self.left.getname()] = '#define ' + self.left.getname().upper() + ' ' + str(self.right.to_c()) + '\n'
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
        # Stringa dei parametri
        parametri = ''
        # Numero parametri trovati
        param_number = 0
        # Metto i parametri in una stringa di appoggio (parametri)
        for statement in self.args.get_statements():
            param_number += 1
            ### Se è globale ovvero #define occorre fare .upper()
            if statement.to_c() in Appoggio.variabili_globali:
                parametri += ', ' + statement.to_c().upper()
            else:
                parametri += ', ' + statement.to_c()
        parametri += ')'

        if self.name in Appoggio.funzioni:
            # Se corrisponde alla funzione Packet.wtite il primo parametro va assegnato mentre il secondo va tra parentesi
            if self.name[:12] == "Packet.write":
                return Appoggio.funzioni[self.name] + self.args.get_statements()[0].to_c() +", " + self.args.get_statements()[1].to_c() + ')'
            # Se corrisponde alla funzione Packet.read, prende come primo parametro
            # la variabile .right dell'Assignment sotto forma di puntatore (&var)
            # mentre come parametri i parametri passati
            if self.name[:11] == "Packet.read":
                return parametri

        ###### Quando faccio una Call la funzione potrebbe essere:
        # - un programma eCLAT, contenuto in eclat_program_list.csv
        # - una chain, contenuta in registry.csv
        # - un alias, ovvero una variabile a cui è stato assegnato un programma eCLAT o una chain

        # Controllo se è un alias
        if self.name in Appoggio.funzioni_alias:
            ###### NON POSSO FARE L'ESECUZIONE ESSENDO A BASSO LIVELLO QUINDI NON POSSO SAPERE QUALE ALIAS SARA'
            ###### DI CONSEGUENZA NON POSSO FARE UN CONTROLLO SUL NUMERO DI PARAMETRI 
            ##### PER ESEMPIO NON SO SE L'ALIAS SARA' UNA CHAIN O UN PROGRAMMA eCLAT
            return 'hike_elem_call_' + str(param_number+1) + '(' + self.name + parametri

        # Controllo se è una chain
        if self.name in Appoggio.funzioni_registry:
            # Controllo che il numero di parametri passati sia giusto
            if len(Appoggio.funzioni_parametri_locali[self.name]) != param_number:
                raise Exception("The expected number of parameter in " + self.name + " is: " + str(len(Appoggio.funzioni_parametri_locali[self.name])) + ", found: " + str(param_number))
            return 'hike_elem_call_' + str(param_number+1) + '(' + Appoggio.funzioni_registry[self.name][0] + parametri
        
        if self.name in Appoggio.funzioni_eclat:
            ######### CONTROLLO NUMERO PARAMETRI MAX 4 ?????????????? ###############
            if param_number > 4:
                raise Exception("The expected number of parameter in " + self.name + " is max 4, found: " + str(param_number))

            return 'hike_elem_call_' + str(param_number+1) + '(' + Appoggio.funzioni_eclat[self.name][0] + parametri

        #return 'hike_elem_call_' + str(param_number+1) + '(' + find_Program(self.name) + parametri

    def prima_passata(self):
        return ''


class Return(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return self.value.eval(env)

    def to_c(self):
        if self.value.to_c() == "Null()":
            return "return 0"
            #return "return XDP_ABORTED"
        return 'return %s' % (self.value.to_c())

    def prima_passata(self):
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

    def prima_passata(self):
        return self.body.prima_passata() + "," + self.else_body.prima_passata()


class Else(BaseBox):
    def __init__(self, else_body=Null()):
        self.else_body = else_body

    def eval(self, env):
        return self.else_body.eval(env)

    def to_c(self):
        #result = '\n' + Appoggio.indent_level*'\t' + 'else {\n' + self.else_body.to_c() + Appoggio.indent_level*'\t' + '}'
        result = self.else_body.to_c()
        return result

    def prima_passata(self):
        return self.else_body.prima_passata()


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

    def prima_passata(self):
        return self.body.prima_passata()


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

    def prima_passata(self):
        return ""
