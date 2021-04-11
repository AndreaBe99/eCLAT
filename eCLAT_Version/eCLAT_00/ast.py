import ast
from re import A, S
from rply.token import BaseBox
from integer import Integer
import csv
from random import randint

### CLASSE DI APPOGGIO PER SCRIVERE LE DICHIARAZIONI ###
class Appoggio():
    in_function = False
    define_function = {}
    define_function_number = 0
    variabili_locali = {}
    variabili_globali = {}
    funzioni = {
        #"Packet.readU8": "bpf_ntohs(__READ_PACKET(__be8",
        "Packet.readU16": "bpf_ntohs(__READ_PACKET(__be16",
        "Packet.readU32": "bpf_ntohl(__READ_PACKET(__be32",
        #"Packet.readU64": "bpf_ntohs(__READ_PACKET(__be64",
        "Packet.writeU8": "__WRITE_PACKET(__u8",
        #"Packet.writeU16": "__WRITE_PACKET(__u16",
        #"Packet.writeU32": "__WRITE_PACKET(__u32",
        #"Packet.writeU64": "__WRITE_PACKET(__u64",
    }
    indent_level = 0

###### FUNZIONE PROVVISORIA ########
def find_Program(statement, mod):
    result = ''
    with open("eclat_program_list.csv", mode='r') as csv_file:
        str = csv.reader(csv_file, delimiter=';')
        for row in str:
            if statement == row[0]:
                if mod == "1":
                    return row[1]
                if mod == "2":
                    return row[1] + ' ' + row[2]
    raise Exception("\"" + statement +"\" Hike Program not defined")


class Program(BaseBox):
    def __init__(self, statement):
        self.statements = []
        self.statements.append(statement)

    def add_statement(self, statement):
        self.statements.insert(0, statement)

    def eval(self, env):
        result = None
        output = ""
        define_function_list = ""
        for statement in self.statements:
            result = statement.eval(env)
            output += statement.to_c()
        
        for define in Appoggio.define_function:
            define_function_list += Appoggio.define_function[define] + "\n"
        output = "#include <hike_vm.h>\n" + define_function_list + output
        print(output)

        #print("\nVARIABILI: ")
        #for var in env.variables:
        #    print(var, env.variables[var])
        f = open("output.c", "w")
        f.write(output)
        f.close()
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
            #print result.to_string()
        return result
    
    def to_c(self):
        num_var = len(Appoggio.variabili_locali)

        result = ''
        Appoggio.indent_level += 1
        for statement in self.statements:
            result += '\t'*Appoggio.indent_level + statement.to_c() #+ ';'
            if result[-1] != '{' and result[-1] != '}' and result[-1] != ';':
                result += ';'
            result += '\n'
        

        variabili = ''
        num_var_add = len(Appoggio.variabili_locali) - num_var
        for i in range(num_var_add):
            variabili += '\t'*Appoggio.indent_level + str(Appoggio.variabili_locali.popitem()[1])

        Appoggio.indent_level -= 1
        return variabili + result



class Null(BaseBox):
    def eval(self, env):
        return self
    
    def to_string(self):
        return 'null'

    def to_c(self):
        #return 'NULL'
        return 'Null()'


class Boolean(BaseBox):
    def __init__(self, value):
        self.value = bool(value)

    def eval(self, env):
        return self.value
    
    def to_c(self):
        return str(self.value)


class Integer(Integer):
    def __init__(self, value):
        self.value = int(value)  

    def eval(self, env):
        return self.value

    def to_string(self):
        return str(self.value)

    def to_c(self):
        return str(self.value)


class Float(BaseBox):
    def __init__(self, value):
        self.value = float(value)

    def eval(self, env):
        return self.value
    
    def to_string(self):
        return str(self.value)

    def to_c(self):
        return str(self.value)


class String(BaseBox):
    def __init__(self, value):
        self.value = str(value)

    def eval(self, env):
        return self.value
    
    def to_string(self):
        return '"%s"' % str(self.value)

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
    
    def to_string(self):
        return str(self.name)

    def to_c(self):
        if self.name in Appoggio.variabili_locali or self.name in Appoggio.variabili_locali:
            return self.name
        else:
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


class BitWise_Not(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        result = self.value.eval(env)
        return ~bin(result.value)
        raise LogicError("Cannot 'not' that")

    def to_c(self):
        return 'BitWise_Not(%s)' % (self.value.to_c())



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
    
class FunctionDeclaration(BaseBox):
    def __init__(self, name, args, block):
        self.name = name
        self.args = args
        self.block = block

    def eval(self, env):
        #print("def " + str(self.name))       
        self.block.eval(env)
        #raise LogicError("Cannot assign to this")
    
    def to_c(self):
        Appoggio.in_function = True
        if self.name in Appoggio.funzioni:
            raise Exception(self.name + " function already defined.")
        
        Appoggio.define_function[self.name] = "#define " + self.name.upper() + " " + str(Appoggio.define_function_number)
        Appoggio.define_function_number += 1
        Appoggio.funzioni[self.name] = self.name.upper()

        res = '\n__section("__trp_chain_' + self.name + '")\n'
        res += 'int __trp_chain_' + self.name + '(void) {\n'

        #### Se la funzione ha parametri?
        #result = 'FunctionDeclaration %s (' % self.name
        #if isinstance(self.args, Array):
        #    for statement in self.args.get_statements():
        #        result += ' ' + statement.to_c()
        #result += ')'
        #result += '\t(\n'

        #if isinstance(self.args, Block):
        Appoggio.indent_level += 1
        return_presente = False
        result = ''
        for statement in self.block.get_statements():
            # Se c'èlo statement RETURN non c'è bisogno di inserirlo
            if statement.to_c().split()[0] == "return":
                return_presente = True
            result += '\n' + '\t'*Appoggio.indent_level + statement.to_c()
            if result[-1] != '{' and result[-1] != '}' and result[-1] != ';':
                result += ';'

        ### PASTE VARIABLE
        variabili = ''
        for var in Appoggio.variabili_locali:
            variabili += '\t'*Appoggio.indent_level + Appoggio.variabili_locali[var]

        # RETURN statement trovato
        if return_presente:
            result += '\n' + '\t'*Appoggio.indent_level
        # RETURN statement NON trovato metto RETURN XDP_DROP di default
        else:
            result += '\n' + '\t'*Appoggio.indent_level + 'return XDP_ABORTED;'
        result += '\n}\n'

        result = res + variabili + result

        Appoggio.indent_level -= 1
        Appoggio.in_function = False
        Appoggio.variabili_locali.clear()
        return result

    def to_string(self):
        return "<function '%s'>" % self.name


class BinaryOp(BaseBox):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def to_c(self):
        return 'BinaryOp(%s, %s)' % (self.left.to_c(), self.right.to_c())


    
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
        if not Appoggio.in_function:
            if not (self.left.getname() in Appoggio.variabili_globali):
                Appoggio.variabili_globali[self.left.getname()] = '#define ' + self.left.getname().upper() + ' ' + str(self.right) + '\n'
                return Appoggio.variabili_globali[self.left.getname()]
        else:
            if not (self.left.getname() in Appoggio.variabili_locali):
                Appoggio.variabili_locali[self.left.getname()] = '__s64 ' + self.left.getname() + ';\n' 
                #return Appoggio.variabili_locali[self.left.getname()] + ' = ' + self.right.to_c()    
            return self.left.getname() + ' = ' + self.right.to_c()
        raise Exception("ERRORE: Variabile")


class Call(BaseBox):
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.value = 0

    def eval(self, env):
        result = Null()
        return result

    def to_c(self):
        result = ''
        param_number = 1
        #if isinstance(self.args, Array):
        for statement in self.args.get_statements():
            param_number += 1
            ### Se è globale ovvero #define occorre fare .upper()
            if statement.to_c() in Appoggio.variabili_globali:
                result += ', ' + statement.to_c().upper()
            else: 
                result += ', ' + statement.to_c()
        result += ')'
        
        if self.name in Appoggio.funzioni:
            if self.name[:12] == "Packet.write":
                return Appoggio.funzioni[self.name] + result
            if self.name[:11] == "Packet.read":
                return Appoggio.funzioni[self.name] + result + ')'
            return 'hike_call_' + str(param_number) + '(' + Appoggio.funzioni[self.name]  + result  

        call = 'hike_call_' + str(param_number) + '(' + find_Program(self.name, "1") + result    
        return call


    def to_string(self):
        return "<call '%s'>" % self.name


class Return(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return self.value.eval(env)

    def to_c(self):
        if self.value.to_c() == "Null()":
            return "return XDP_ABORTED"
        return 'return %s' % (self.value.to_c())

    def to_string(self):
        return "<return '%s'>" % self.name



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
