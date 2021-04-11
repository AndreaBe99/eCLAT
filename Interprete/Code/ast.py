import ast
from re import A, S
from rply.token import BaseBox
from integer import Integer
import csv
from random import randint


# --------------------------------------- #
#           CLASSE DI APPOGGIO            #
#     PER SCRIVERE LE DICHIARAZIONI       #
# --------------------------------------- #
class Appoggio():    
    in_function = False             # variabile per capire se sono o meno all'interno di una funzione
    indent_level = 0                # Contatore per l'indentazione del file .c
    funzioni_alias = {}             # dict per gli Alias quando assegno una funzione ad un parametro
    funzioni_parametri_locali = {}  # dict costruito alla PRIMA PASSATA contenente le funzioni con associte i parametri in esse contenute
    funzioni_variabili_locali = {}  # dict costruito alla PRIMA PASSATA contenente le funzioni con associte le variabili in esse contenute
    tipo_variabili_locali = {}      # dict costruito alla PRIMA PASSATA alias del precedente con all'interno tuple per i tipi
    variabili_globali = {}          # dict contenente le variabili globali con associato la stringa #define per il file .c
    funzione_corrente = ""          # Variabile di appoggio in cui viene memorizzato il nome della funzione corrente
    hike_program = {}               # dict dei programmi Hike presenti nel file eclat_program_list
    chain_registry = {}             # dict delle Chain prese dal file regisrty
    net_packet = {}                  # dict provvisorio per la funzione Packet

# --------------------------------------- #
#           FUNZIONE PROVVISORIA          #
# Trova il programma nei file se presente #
# --------------------------------------- #
def find_Program(statement):
    if statement in Appoggio.hike_program:
        return str(Appoggio.hike_program[statement][0]) \
            + " " + str(Appoggio.hike_program[statement][1])
    if statement in Appoggio.chain_registry:
        return "HIKE_CHAIN_" \
            + str(Appoggio.chain_registry[statement][0]) + "_ID"
    raise Exception("\"" + statement \
        +"\" Hike Program/Function not defined")


class Program(BaseBox):
    def __init__(self, statement):
        self.statements = []
        self.statements.append(statement)

    def add_statement(self, statement):
        self.statements.insert(0, statement)

    def exec(self, env):
        # ----------------------------------------- #
        # prima passata per "scorrere" le funzioni  #
        # e le variabili                            #
        prima_passata = ""
        for statement in self.statements:
            prima_passata += statement.prima_passata(env)
        # ----------------------------------------- #

        # ----------------------------------------- #
        # Scrivo tutte le funzioni trovate in un    #
        # registry e nel dict con associato un      #
        # contatore                                 #
        funzioni = ""
        count = 64  # CONTATORE INIZIO PER I #define
        with open('Lib/regisrty.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            for fun in Appoggio.funzioni_variabili_locali:
                funzioni += "#define " +  "HIKE_CHAIN_" \
                    + str(fun.upper())+"_ID" + " " + str(count) + "\n"
                Appoggio.chain_registry[fun] = [fun.upper(), count]
                writer.writerow([str(fun), "HIKE_CHAIN_" \
                    + str(fun.upper())+"_ID", str(count)])
                count += 1
        # ----------------------------------------- #
        
        # ----------------------------------------- #
        # CONVERTO IN C, Il risultato è in 'output' #
        result = ""  # SIMULAZIONE ESECUZIONE
        output = "" 
        for statement in self.statements:
            result = statement.exec(env)
            output += statement.to_c()
        # ----------------------------------------- #

        # ----------------------------------------- #
        # Importo i #define di default e            #
        # incollo (in ordine):                      #
        # - le funzioni (chain) dichiarate          #
        # - il codice .c calcolato                  #
        # output = "#include <hike_vm.h>\n" + funzioni + variabili_globali + output
        output = funzioni + output
        # ----------------------------------------- #

        print("'eclat_output.c' was generated.")
        f = open("eclat_output.c", "w")
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

    def exec(self, env):
        result = ""
        for statement in self.statements:
            result = statement.exec(env)
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

    def prima_passata(self, env):
        result = ""
        for statement in self.statements:
            if statement.prima_passata(env) != "":
                result += statement.prima_passata(env) + ","
        return result[:-1]


class Expression(BaseBox):
    def __init__(self, value):
        self.value = value

    def exec(self, env):
        return self.value.exec(env)

    def prima_passata(self, env):
        return ""

    def to_c(self):
        #return 'NULL'
        return "(" + self.value.to_c() + ")"

class Null(BaseBox):
    def exec(self, env):
        return self

    def prima_passata(self, env):
        return "Null()"

    def to_c(self):
        #return 'NULL'
        return 'Null()'

class Boolean(BaseBox):
    def __init__(self, value):
        self.value = bool(value)

    def exec(self, env):
        return self.value

    def prima_passata(self, env):
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

    def exec(self, env):
        return self.value

    def prima_passata(self, env):
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

    def exec(self, env):
        return self.value

    def prima_passata(self, env):
        return str(self.value)

    def to_c(self):
        return str(self.value)


class String(BaseBox):
    def __init__(self, value):
        self.value = str(value)

    def exec(self, env):
        return self.value

    def prima_passata(self, env):
        return str(self.value)

    def to_c(self):
        return str(self.value)



class Variable(BaseBox):
    def __init__(self, name):
        self.name = str(name)
        self.value = None

    def getname(self):
        return str(self.name)

    def exec(self, env):
        if env.variables.get(self.name, None) is not None:
            self.value = env.variables[self.name]
            return self.value
        raise Exception("Not yet defined " + str(self.name))

    def to_c(self):
        # +++++++++++ CONTROLLO ERRORE ++++++++++++ #
        # Se è una variabile globale.               #
        # +++++++++++++++++++++++++++++++++++++++++ #
        if self.name in Appoggio.variabili_globali:
            return self.name.upper()
        # ----------------------------------------- #
        # Se sono all'interno di una funzione       #
        if Appoggio.funzione_corrente != "":
            if Appoggio.funzione_corrente in Appoggio.funzioni_variabili_locali:
                # ----------------------------------------- #
                # PARAMETRO o VARIABILE locale              #
                if self.name in Appoggio.funzioni_variabili_locali[Appoggio.funzione_corrente]:
                    return self.name
                if self.name in Appoggio.funzioni_parametri_locali[Appoggio.funzione_corrente]:
                    return self.name
        raise Exception("Variable \"" + str(self.name) + "\" not declared")
    
    def prima_passata(self, env):
        # ----------------------------------------- #
        # Il controllo dell'errore è in .to_c(),    #
        # ----------------------------------------- #
        return str(self.name)




class BinaryOperation():
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def exec(self, env):
        if self.operator == '+':
            return self.left.exec(env).__add__(self.right.exec(env))
        elif self.operator == '-':
            return self.left.exec(env).__sub__(self.right.exec(env))
        elif self.operator == '*':
            return self.left.exec(env).__mul__(self.right.exec(env))
        elif self.operator == '/':
            return self.left.exec(env).__div__(self.right.exec(env))
        elif self.operator == '==':
            return self.left.exec(env).__eq__(self.right.exec(env))
        elif self.operator == '!=':
            result = self.left.exec(env).__eq__(self.right.exec(env))
            result.value = not result.value
            return result
        elif self.operator == '>=':
            return self.left.exec(env).__ge__(self.right.exec(env))
        elif self.operator == '<=':
            return self.left.exec(env).__le__(self.right.exec(env))
        elif self.operator == '>':
            return self.left.exec(env).__gt__(self.right.exec(env))
        elif self.operator == '<':
            return self.left.exec(env).__lt__(self.right.exec(env))
        elif self.operator == 'AND':
            one = self.left.exec(env).equals(Boolean(True))
            two = self.right.exec(env).equals(Boolean(True))
            return Boolean(one.value and two.value)
        elif self.operator == 'OR':
            one = self.left.exec(env).equals(Boolean(True))
            two = self.right.exec(env).equals(Boolean(True))
            return Boolean(one.value or two.value)
        ### BITWISE OPERATION #####
        elif self.operator == '&':
            return int(self.left.exec(env)) & int(self.right.exec(env))
        elif self.operator == '|':
            return int(self.left.exec(env)) | int(self.right.exec(env))
        elif self.operator == '^':
            return int(self.left.exec(env)) ^ int(self.right.exec(env))
        elif self.operator == '<<':
            return int(self.left.exec(env)) << int(self.right.exec(env))
        elif self.operator == '>>':
            return int(self.left.exec(env)) >> int(self.right.exec(env))
        else:
            raise Exception("Shouldn't be possible")

    def to_c(self):
        return ' ' + self.left.to_c() + ' ' \
            + self.operator + ' ' + self.right.to_c() + ' '

    def prima_passata(self, env):
        return ' ' + self.left.prima_passata() + ' ' \
            + self.operator + ' ' + self.right.prima_passata() + ' '


class Not(BaseBox):
    def __init__(self, value):
        self.value = value

    def exec(self, env):
        result = self.value.exec(env)
        if isinstance(result, Boolean):
            return Boolean(not result.value)
        raise LogicError("Cannot 'not' that")

    def to_c(self):
        return 'not%s ' % (self.value.to_c())

    def prima_passata(self, env):
        return ""


class BitWise_Not(BaseBox):
    def __init__(self, value):
        self.value = value

    def exec(self, env):
        result = self.value.exec(env)
        return ~bin(result.value)
        raise LogicError("Cannot 'not' that")

    def to_c(self):
        return 'BitWise_Not(%s)' % (self.value.to_c())

    def prima_passata(self, env):
        return ""



class FromImport(BaseBox):
    def __init__(self, to_co, args):
        self.to_co = to_co
        self.args = args

    def exec(self, env):
        self.args.exec(env)
        #raise LogicError("Cannot assign to this")

    def to_c(self):
        result = ''
        for statement in self.args.get_statements():
            if statement[:6] != "Packet":
                result += '#define ' + Appoggio.hike_program[statement][0] + " " \
                + Appoggio.hike_program[statement][1] + '\n'
        return result
        return self.args.to_c()

    def prima_passata(self, env):
        # +++++++++++ CONTROLLO ERRORE ++++++++++++ #
        # PER ORA SOLO hike and net                 #
        # +++++++++++++++++++++++++++++++++++++++++ #
        if self.to_co != "hike" and self.to_co != "net":
            raise Exception(str(self.to_co) + " not found.")

        # ----------------------------------------- #
        # Per ogni programma hike importato leggo i #
        # valori dal file eclat_program_list.csv e  #
        # li salvo IN UN DICT PER COMODITA'.        #
        trovato = False
        if self.to_co == "hike":
            for statement in self.args.get_statements():
                with open("lib/eclat_program_list.csv", mode='r') as csv_file:
                    string = csv.reader(csv_file, delimiter=';')
                    for row in string:
                        if statement == row[0]:
                            trovato = True
                            Appoggio.hike_program[row[0]] = [row[1], row[2]]
                    # +++++++++++ CONTROLLO ERRORE ++++++++++++ #
                    # Se non trovo il programma nel .csv        #
                    # +++++++++++++++++++++++++++++++++++++++++ #
                    if not trovato:
                        raise Exception("Hike Program '" + statement + "' not found.")
                    trovato = False
        # ----------------------------------------- #
        # Se c'è l'import da net di Packet assegno  #
        # le funzioni di Packet in un dict.         #
        if self.to_co == "net":
            for statement in self.args.get_statements():
                if statement == "Packet":
                    Appoggio.net_packet = {
                        "Packet.readU8": "hike_packet_read_u8(",
                        "Packet.readU16": "hike_packet_read_u16(",
                        #"Packet.readU32": "hike_packet_read_u32(",
                        #"Packet.readU64": "hike_packet_read_u64(",
                        "Packet.writeU8": "hike_packet_write_u8(",
                        "Packet.writeU16": "hike_packet_write_u16(",
                        #"Packet.writeU32": "hike_packet_write_u32(",
                        #"Packet.writeU54": "hike_packet_write_u64(",
                    }
                else:
                    # +++++++++++ CONTROLLO ERRORE ++++++++++++ #
                    # Per ora NET ammette solo Packet           #
                    # +++++++++++++++++++++++++++++++++++++++++ #
                    raise Exception("Net Class '" + statement + "' not found.")
        return ""

class Import(BaseBox):
    def __init__(self, args):
        self.args = args

    def exec(self, env):
        self.args.exec(env)
        #raise LogicError("Cannot assign to this")

    def to_c(self):
        result = ''
        for statement in self.args.get_statements():
            result += '#define ' + find_Program(statement) + '\n'
        return result

    def prima_passata(self, env):
        return ""

class FunctionDeclaration(BaseBox):
    def __init__(self, name, args, block):
        self.name = name
        self.args = args
        self.block = block

    def exec(self, env):
        self.block.exec(env)
        #raise LogicError("Cannot assign to this")

    def to_c(self):
        Appoggio.in_function = True
        Appoggio.funzione_corrente = self.name

        res = "\nHIKE_CHAIN(" + find_Program(self.name)

        #### Se la funzione ha parametri?
        if isinstance(self.args, Array):
            for statement in self.args.get_statements():
                res += ', __u64 ' + statement
        #result += '\t(\n'
        res += ") {\n"
        Appoggio.indent_level += 1

        ### PASTE VARIABLE
        # Se esistono variabili locali
        if len(Appoggio.tipo_variabili_locali[self.name]) != 0:
            for var in Appoggio.tipo_variabili_locali[self.name]:
                res += Appoggio.indent_level*"\t_u" + \
                    str(var[1]) + " " + str(var[0]) + ";\n"

        return_presente = False
        result = ''
        for statement in self.block.get_statements():
            # Se c'è lo statement RETURN non c'è bisogno di inserirlo
            if statement.to_c().split()[0] == "return":
                return_presente = True
            result += '\n' + '\t'*Appoggio.indent_level + statement.to_c()
            if result[-1] != '{' and result[-1] != '}' and result[-1] != ';':
                result += ';'

        # RETURN statement trovato
        if return_presente:
            result += '\n' + '\t'*Appoggio.indent_level
        # RETURN statement NON trovato metto RETURN 0 di default
        else:
            result += '\n' + '\t'*Appoggio.indent_level + 'return 0;'
        result += '\n}\n'

        result = res + result
        Appoggio.indent_level -= 1
        Appoggio.in_function = False
        Appoggio.funzione_corrente = ""
        return result

    def prima_passata(self, env):
        # +++++++++++ CONTROLLO ERRORE ++++++++++++ #
        # Controllo se sia già stata dichiarata     #
        # +++++++++++++++++++++++++++++++++++++++++ #
        if self.name in Appoggio.funzioni_variabili_locali or self.name in Appoggio.net_packet:
            raise Exception("Function \"" + str(self.name) + "\" already exists.")

        Appoggio.in_function = True
        Appoggio.funzione_corrente = self.name

        # ----------------------------------------- #
        # Metto i parametri in un dict              #
        array_parametri = []
        if isinstance(self.args, Array):
            for statement in self.args.get_statements():
                array_parametri.append(statement)

        # +++++++++++ CONTROLLO ERRORE ++++++++++++ #
        # Controllo il numero dei parametri, se     #
        # giusto lo assegno al dict                 #
        # +++++++++++++++++++++++++++++++++++++++++ #
        if len(array_parametri) > 4:
            raise Exception("You can only pass 4 parameters")
        Appoggio.funzioni_parametri_locali[self.name] = array_parametri
        # ----------------------------------------- #

        # ----------------------------------------- #
        # Metto le variabili locali in un dict      #
        result = []
        for statement in self.block.get_statements():
            array_appoggio = statement.prima_passata(env).split(",")
            for var in array_appoggio:
                # Nel caso in cui sia un parametro
                if not var in Appoggio.funzioni_parametri_locali[self.name]:
                    result.append(var)
        # Elimina eventuali spazi vuoti delle stringhe e i return Null()
        result = [i for i in result if i != "" and i != "Null()"]
        # Elimina eventuali duplicati
        result = list(dict.fromkeys(result))
        Appoggio.funzioni_variabili_locali[str(self.name)] = result
        # ----------------------------------------- #
        
        Appoggio.in_function = False
        Appoggio.funzione_corrente = ""
        return str(self.name)


class BinaryOp(BaseBox):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def to_c(self):
        return 'BinaryOp(%s, %s)' % (self.left.to_c(), self.right.to_c())

    def prima_passata(self, env):
        return self.left.prima_passata() + self.right.prima_passata()



class Assignment(BinaryOp):
    def exec(self, env):
        if isinstance(self.left, Variable):
            if type(self.right) is BinaryOperation:
                env.variables[self.left.getname()] = self.right.exec(env)
            elif type(self.right) is Variable:
                env.variables[self.left.getname()] = self.right.exec(env)
            else:
                env.variables[self.left.getname()] = self.right.value
            return self.right.exec(env)
            # otherwise raise error
            #raise ImmutableError(self.left.getname())
        else:
            raise LogicError("Cannot assign to this")

    def to_c(self):
        # ----------------------------------------- #
        # Se la parte destra è una Call             #
        # ----------------------------------------- #
        if type(self.right) is Call:
            # Se corrisponde ad una Packet.read
            if self.right.name[:11] == "Packet.read":
                return Appoggio.net_packet[self.right.name] + "&" \
                    + self.left.getname() + self.right.to_c()
        # ----------------------------------------- #
        # Se sono all'interno di una funzione       #
        # ----------------------------------------- #
        if Appoggio.funzione_corrente != "":
            # Se la funzione è stata dichiarata
            if Appoggio.funzione_corrente in Appoggio.funzioni_variabili_locali:
                    return self.left.getname() + ' = ' + self.right.to_c()
        # ----------------------------------------- #
        # Se sono al di fuori delle funzioni        #
        # ----------------------------------------- #
        else:
            # ----------------------------------------- #
            # Se è tra le variabili globali già         #
            # già dichiarate, faccio #undef e la        #
            # ridefinisco.                              #
            # Altrimenti la inserisco nel dict con      #
            # associata la stringa tradotta in .c       #
            # ----------------------------------------- #
            if self.left.getname() in Appoggio.variabili_globali:
                ##############  PROBLEMA  ##############
                # COME VIENE SOVRASCITTO IL VALORE ??? #
                #    Per adesso faccio un #undef       #
                ########################################
                return '#undef ' + self.left.getname().upper() \
                    + "\n#define " + self.left.getname().upper() + ' ' + \
                    str(self.right.to_c()) + '\n'
            else:
                Appoggio.variabili_globali[self.left.getname()] = '#define '\
                    + self.left.getname().upper() + ' ' + str(self.right.to_c()) + '\n'
                return Appoggio.variabili_globali[self.left.getname()]


    def prima_passata(self, env):
        # ----------------------------------------- #
        # Se sono all'interno di una funzione,      #
        # controllo se già esiste nel dict, se no   #
        # la creo e gli assegno un array vuoto.     # 
        # ----------------------------------------- #
        chiavi = Appoggio.funzioni_variabili_locali.keys()
        if Appoggio.funzione_corrente != "":
            if not Appoggio.funzione_corrente in chiavi:
                Appoggio.funzioni_variabili_locali[Appoggio.funzione_corrente] = []
                Appoggio.tipo_variabili_locali[Appoggio.funzione_corrente] = []
            # ----------------------------------------- #
            # Quando assegno una variabile per la prima #
            # volta significa che la sto dichiarando.   #
            # PER DEFINIRE IL TIPO (u8, u16, u32, u64,  #
            # The min and max values are based on the   #
            # following equation; from 0 to 2ⁿ-1)       #
            # devo vedere il valore della parte destra: #
            # - se è una Call vedo se è Read/Write e    #
            #   assegno il tipo corrispettivo, di       #
            #   default è a 32.                         #
            # - se è un numero vedo la grandezza        #
            # - se è una BinaryOp la eseguo e vedo il   #
            #   il risultato.                           #
            # ----------------------------------------- #
            if not self.left.getname() in Appoggio.funzioni_variabili_locali[Appoggio.funzione_corrente] and \
                not self.left.getname() in Appoggio.funzioni_parametri_locali[Appoggio.funzione_corrente]:
                Appoggio.funzioni_variabili_locali[Appoggio.funzione_corrente].append(self.left.getname()) 
                # ----------------------------------------- #
                # Se è una Call controllo se è una Packet   #
                # in tal caso deduco la dimensione.         #
                # Altrimenti se è un Call di un Hike Prog   #
                # o di una Chain di default è a 32.         #
                # ----------------------------------------- #
                if type(self.right) is Call:
                    if self.right.name[:11] == "Packet.read" or self.right.name[:12] == "Packet.write":
                        if self.right.name[11:] == "U8" or self.right.name[12:] == "U8":
                            Appoggio.tipo_variabili_locali[Appoggio.funzione_corrente].append((self.left.getname(), 8))
                        if self.right.name[11:] == "U16" or self.right.name[12:] == "U16":
                            Appoggio.tipo_variabili_locali[Appoggio.funzione_corrente].append((self.left.getname(), 16))
                        if self.right.name[11:] == "U32" or self.right.name[12:] == "U32":
                            Appoggio.tipo_variabili_locali[Appoggio.funzione_corrente].append((self.left.getname(), 32))
                        if self.right.name[11:] == "U64" or self.right.name[12:] == "U64":
                            Appoggio.tipo_variabili_locali[Appoggio.funzione_corrente].append((self.left.getname(), 64))
                    else:
                        Appoggio.tipo_variabili_locali[Appoggio.funzione_corrente].append((self.left.getname(), 32))
                # ----------------------------------------- #
                # Se assegno un numero, tramite la formula  #
                # calcolo la dimensione.                    #
                # ----------------------------------------- #
                elif type(self.right) is Integer or type(self.right) is Float:
                    if int(self.right.exec(env)) < 2**8 -1:
                        Appoggio.tipo_variabili_locali[Appoggio.funzione_corrente].append((self.left.getname(), 8))
                    if 2**8 - 1 < int(self.right.exec(env)) < 2**16 - 1:
                        Appoggio.tipo_variabili_locali[Appoggio.funzione_corrente].append((self.left.getname(), 16))
                    if 2**16 - 1 < int(self.right.exec(env)) < 2**32 - 1:
                        Appoggio.tipo_variabili_locali[Appoggio.funzione_corrente].append((self.left.getname(), 32))
                    if 2**32 - 1 < int(self.right.exec(env)) < 2**64 - 1:
                        Appoggio.tipo_variabili_locali[Appoggio.funzione_corrente].append((self.left.getname(), 64))
                # ----------------------------------------- #
                # Se è un espressione matematica, la eseguo #
                # e guardo il risultato finale, e tramite   #
                # la formula calcolo la dimensione          #
                # ----------------------------------------- #
                elif type(self.right) is BinaryOperation:
                    if self.right.exec(env) < 2**8 - 1:
                        Appoggio.tipo_variabili_locali[Appoggio.funzione_corrente].append((self.left.getname(), 8))
                    if 2**8 - 1 < self.right.exec(env) < 2**16 - 1:
                        Appoggio.tipo_variabili_locali[Appoggio.funzione_corrente].append((self.left.getname(), 16))
                    if 2**16 - 1 < self.right.exec(env) < 2**32 - 1:
                        Appoggio.tipo_variabili_locali[Appoggio.funzione_corrente].append((self.left.getname(), 32))
                    if 2**32 - 1 < self.right.exec(env) < 2**64 - 1:
                        Appoggio.tipo_variabili_locali[Appoggio.funzione_corrente].append((self.left.getname(), 64))
                else:
                    Appoggio.tipo_variabili_locali[Appoggio.funzione_corrente].append((self.left.getname(), 64))

            # ----------------------------------------- #
            # Se la parte destra è una call significa   #
            # che sto facendo una ALIAS                 #
            # ----------------------------------------- #
            if type(self.right) is Call:
                chiavi = Appoggio.funzioni_alias.keys()
                if self.left.getname() in chiavi:
                    Appoggio.funzioni_alias[self.left.getname()].append(self.right.name)
                else:
                    Appoggio.funzioni_alias[self.left.getname()] = [self.right.name]
                # Elimina eventuali duplicati
                appoggio = Appoggio.funzioni_alias[self.left.getname()]
                Appoggio.funzioni_alias[self.left.getname()] = list(dict.fromkeys(appoggio))

        return str(self.left.getname())


class Call(BaseBox):
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.value = 0

    def exec(self, env):
        result = Null()
        return result

    def to_c(self):
        # +++++++++++ CONTROLLO ERRORE ++++++++++++ #
        # Controllo se è un programma hike, chain,  #
        # o un alias di una chai o programma hike   #
        # ------------------------------------------#
        if not self.name in Appoggio.hike_program and \
            not self.name in Appoggio.chain_registry and \
                not self.name in Appoggio.funzioni_alias and \
                    not self.name in Appoggio.net_packet.keys():
            raise Exception("'" +str(self.name) + "' does not exist")
        
        parametri = ''      # Stringa dei parametri
        param_number = 0    # Numero parametri trovati
        # ----------------------------------------- #
        # Metto i parametri in una stringa di       #
        # appoggio (parametri)                      #
        # ----------------------------------------- #
        for statement in self.args.get_statements():
            param_number += 1
            # ----------------------------------------- #
            # Se è globale ovvero #define occorre       #
            # fare .upper()                             #
            # ----------------------------------------- #
            if statement.to_c() in Appoggio.variabili_globali:
                parametri += ', ' + statement.to_c().upper()
            else:
                parametri += ', ' + statement.to_c()
        parametri += ')'

        # ----------------------------------------- #
        # Se è una funzione Packet                  #
        # ----------------------------------------- #
        if self.name in Appoggio.net_packet:
            # ----------------------------------------- #
            # Se corrisponde alla funzione Packet.wtite # 
            # ----------------------------------------- #
            if self.name[:12] == "Packet.write":
                return Appoggio.net_packet[self.name] + \
                    self.args.get_statements()[0].to_c() +", " \
                        + self.args.get_statements()[1].to_c() + ')'
            # ----------------------------------------- #
            # Se corrisponde alla funzione Packet.read, # 
            # prende come primo parametro la variabile  #
            # .left dell'Assignment sotto forma di      #
            # puntatore (&var) mentre come parametri    #
            # i parametri passati a Packet.read         #
            #                                           #
            # QUESTO LO FACCIO IN ASSIGNEMT()           #
            # ----------------------------------------- #
            if self.name[:11] == "Packet.read":
                return parametri

        # -------------------------------------------#
        # Quando faccio una Call la funzione         #
        # potrebbe essere:                           #
        # - un programma eCLAT,                      #
        #   contenuto in eclat_program_list.csv      #
        # - una chain, contenuta in registry.csv     #
        # - un alias, ovvero una variabile a cui     #
        #   è stato assegnato un programma eCLAT     #
        #   o una chain.                             #
        # -------------------------------------------#
        hike_elem_call_ = 'hike_elem_call_'

        #-------- Controllo se è un alias -----------#
        if self.name in Appoggio.funzioni_alias:
            ##############  PROBLEMA  #################
            # NON POSSO FARE L'ESECUZIONE ESSENDO A   #
            # BASSO LIVELLO QUINDI NON POSSO SAPERE   #
            # QUALE ALIAS SARA'DI CONSEGUENZA NON     #
            # POSSO FARE UN CONTROLLO SUL NUMERO DI   #
            # PARAMETRI PER ESEMPIO NON SO SE L'ALIAS #
            # SARA' UNA CHAIN O UN PROGRAMMA eCLAT    #
            ###########################################
            return hike_elem_call_ + str(param_number+1) + '(' + self.name + parametri

        #------- Controllo se è una chain  ----------#
        if self.name in Appoggio.chain_registry:
            # +++++++++++ CONTROLLO ERRORE ++++++++++++ #
            # Controllo che il numero di parametri      #
            # passati sia giusto                        #
            if len(Appoggio.funzioni_parametri_locali[self.name]) != param_number:
                raise Exception("The expected number of parameter in " \
                    + self.name + " is: " \
                        + str(len(Appoggio.funzioni_parametri_locali[self.name])) \
                            + ", found: " + str(param_number))
            return hike_elem_call_ + str(param_number+1) \
                + '(' + find_Program(self.name) + parametri

        #-------- Controllo se è importata ----------#
        if self.name in Appoggio.hike_program:
            ##############  PROBLEMA  #################
            # CONTROLLO NUMERO PARAMETRI MAX 4 ????   #
            ###########################################

            # +++++++++++ CONTROLLO ERRORE ++++++++++++ #
            # Controllo che il numero di parametri      #
            # passati sia al più 4                      #
            if param_number > 4:
                raise Exception("The expected number of parameter in " \
                    + self.name + " is max 4, found: " + str(param_number))

            return hike_elem_call_ + str(param_number+1) \
                + '(' + Appoggio.hike_program[self.name][0] + parametri

    def prima_passata(self, env):
        # -------------------------------------------#
        # Il controllo dell'errore è fatto in .to_c()#
        # questo perchè non ho ancora a disposizione #
        # tutte le chain scritte nel file .eclat, le #
        # quali sono poi riportate nel dict:         #
        # Appoggio.chain_registry.                #
        # Quindi il controllo va fatto alla seconda  #
        # passata.                                   #
        # -------------------------------------------#
        return ''


class Return(BaseBox):
    def __init__(self, value):
        self.value = value

    def exec(self, env):
        return self.value.exec(env)

    def to_c(self):
        if self.value.to_c() == "Null()":
            return "return 0"
            #return "return XDP_ABORTED"
        return 'return %s' % (self.value.to_c())

    def prima_passata(self, env):
        return ""



class If(BaseBox):
    def __init__(self, condition, body, else_body=Null()):
        self.condition = condition
        self.body = body
        self.else_body = else_body

    def exec(self, env):
        condition = self.condition.exec(env)
        if condition:
            return self.body.exec(env)
        else:
            if type(self.else_body) is not Null:
                return self.else_body.exec(env)
        return Null()

    def to_c(self):
        result = 'if (' + self.condition.to_c() + ') {\n' \
            + self.body.to_c() + Appoggio.indent_level*'\t' + '}'
        if type(self.else_body) is not Null:
            result += '\n' + Appoggio.indent_level*'\t' \
                +'else {\n' + self.else_body.to_c() \
                    + Appoggio.indent_level*'\t' +'}'
        return result

    def prima_passata(self, env):
        return self.body.prima_passata(env) + "," + self.else_body.prima_passata(env)


class Else(BaseBox):
    def __init__(self, else_body=Null()):
        self.else_body = else_body

    def exec(self, env):
        return self.else_body.exec(env)

    def to_c(self):
        result = self.else_body.to_c()
        return result

    def prima_passata(self, env):
        return self.else_body.prima_passata(env)


class While(BaseBox):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def exec(self, env):
        i = 0
        while True:
            if not self.condition.exec(env):
                break
            i += 1
            self.body.exec(env)
        return Null()

    def to_c(self):
        result = 'while (' + self.condition.to_c() \
            + ') {\n' + self.body.to_c() \
                + Appoggio.indent_level*'\t' + '}'
        return result

    def prima_passata(self, env):
        return self.body.prima_passata(env)


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

    def exec(self, env):
        if len(self.values) == 0:
            for statement in self.statements:
                #self.values.append(statement.exec(env))
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

    def prima_passata(self, env):
        return ""
