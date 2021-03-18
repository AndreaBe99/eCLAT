import ast
from re import A
from rply.token import BaseBox
from integer import Integer
import csv

### CLASSE DI APPOGGIO PER SCRIVERE LE DICHIARAZIONI ###
class Appoggio():
    in_function = False
    variabili_locali = {}
    variabili_globali = {}
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
    return result

class Program(BaseBox):
    def __init__(self, statement):
        self.statements = []
        self.statements.append(statement)

    def add_statement(self, statement):
        self.statements.insert(0, statement)

    def eval(self, env):
        #print "count: %s" % len(self.statements)
        result = None
        output = ""
        for statement in self.statements:
            result = statement.eval(env)
            output += statement.rep()
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
        #print "count: %s" % len(self.statements)
        result = None
        for statement in self.statements:
            result = statement.eval(env)
            #print result.to_string()
        return result
    
    def rep(self):
        result = ''
        Appoggio.indent_level += 1
        for statement in self.statements:
            result += '\t'*Appoggio.indent_level + statement.rep() #+ ';'
            if result[-1] != '{' and result[-1] != '}':
                result += ';'
            result += '\n'
        Appoggio.indent_level -= 1
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
            #print(self.values)
        return self

    def rep(self):
        #result = ''
        #for statement in self.statements:
        #    result += '#define ' + find_Program(statement, "2") + '\n'
        result = 'Array('
        #result += ",".join(self.map(lambda x: x.rep(), self.statements))
        result += ",".join(self.map(lambda x: x, self.statements))
        result += ')'
        return result

    def to_string(self):
        return '[%s]' % (", ".join(self.map(lambda x: x.to_string(), self.values)))



class Null(BaseBox):
    def eval(self, env):
        return self
    
    def to_string(self):
        return 'null'

    def rep(self):
        #return 'NULL'
        return 'Null()'


class Boolean(BaseBox):
    def __init__(self, value):
        self.value = bool(value)

    def eval(self, env):
        return self.value
    
    def rep(self):
        return str(self.value)
        #return 'Boolean(%s)' % self.value


class Integer(Integer):
    def __init__(self, value):
        self.value = int(value)  

    def eval(self, env):
        return self.value

    def to_string(self):
        return str(self.value)

    def rep(self):
        return str(self.value)
        #return 'Integer(%s)' % self.value


class Float(BaseBox):
    def __init__(self, value):
        self.value = float(value)

    def eval(self, env):
        return self.value
    
    def to_string(self):
        return str(self.value)

    def rep(self):
        return str(self.value)
        #return 'Float(%s)' % self.value


class String(BaseBox):
    def __init__(self, value):
        self.value = str(value)

    def eval(self, env):
        return self.value
    
    def to_string(self):
        return '"%s"' % str(self.value)

    def rep(self):
        return str(self.value)
        #return 'String("%s")' % self.value



class Variable(BaseBox):
    def __init__(self, name):
        self.name = str(name)
        self.value = None
        
    def getname(self):
        return str(self.name)
    
    def eval(self, env):
        #print("VAR: " + str(self.name) + " is " + str(self.value))
        if env.variables.get(self.name, None) is not None:
            self.value = env.variables[self.name]
            ##print("VAR: " + str(self.name) + " is " + str(self.value))
            return self.value
        raise Exception("Not yet defined " + str(self.name))
    
    def to_string(self):
        return str(self.name)

    def rep(self):
        return self.name
        #return 'Variable(%s)' % self.name




class BinaryOperation():
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right
        #self.value = 0

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
    
    def rep(self):
        return ' ' + self.left.rep() + ' ' + self.operator + ' ' + self.right.rep() + ' '
        #return 'BinaryOp(%s, %s, %s)' % (self.left.rep(), self.operator, self.right.rep())



class Not(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        result = self.value.eval(env)
        if isinstance(result, Boolean):
            return Boolean(not result.value)
        raise LogicError("Cannot 'not' that")

    def rep(self):
        return 'not%s ' % (self.value.rep())


class BitWise_Not(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        result = self.value.eval(env)
        return ~bin(result.value)
        raise LogicError("Cannot 'not' that")

    def rep(self):
        return 'BitWise_Not(%s)' % (self.value.rep())



class FromImport(BaseBox):
    def __init__(self, repo, args):
        self.repo = repo
        self.args = args

    def eval(self, env):
        #print("from " + str(self.repo))
        #print("import")
        self.args.eval(env)
        #raise LogicError("Cannot assign to this")
    
    def rep(self):
        result = ''
        for statement in self.args.get_statements():
            result += '#define ' + find_Program(statement, "2") + '\n'
        return result
        return self.args.rep()
        #return 'From(%s) Import(%s)' % (self.repo, self.args.rep())

class Import(BaseBox):
    def __init__(self, args):
        self.args = args

    def eval(self, env):
        #print("import ")
        self.args.eval(env)
        #raise LogicError("Cannot assign to this")

    def rep(self):
        result = ''
        for statement in self.args.get_statements():
            result += '#define ' + find_Program(statement, "2") + '\n'
        return result
        return 'Import(%s)' % (self.args.rep())

    
class FunctionDeclaration(BaseBox):
    def __init__(self, name, args, block):
        self.name = name
        self.args = args
        self.block = block

    def eval(self, env):
        #print("def " + str(self.name))       
        self.block.eval(env)
        #raise LogicError("Cannot assign to this")
    
    def rep(self):
        Appoggio.in_function = True
        result = '\n__section("__trp_chain_' + self.name + '")\n'
        result += 'int __trp_chain_' + self.name + '(void) {\n'
        #result = 'FunctionDeclaration %s (' % self.name
        #if isinstance(self.args, Array):
        #    for statement in self.args.get_statements():
        #        result += ' ' + statement.rep()
        #result += ')'
        #result += '\t(\n'

        #if isinstance(self.args, Block):
        Appoggio.indent_level += 1
        for statement in self.block.get_statements():
            result += '\n' + '\t'*Appoggio.indent_level + statement.rep()
            if result[-1] != '{' and result[-1] != '}':
                result += ';'
        result += '\n' + '\t'*Appoggio.indent_level + 'return XDP_DROP;'
        result += '\n}\n'
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

    def rep(self):
        return 'BinaryOp(%s, %s)' % (self.left.rep(), self.right.rep())


    
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
    
    def rep(self):
        if not Appoggio.in_function:
            if not (self.left.getname() in Appoggio.variabili_globali):
                Appoggio.variabili_globali[self.left.getname()] = '#define ' + self.left.getname() + ' ' + str(self.right) + '\n'
                return Appoggio.variabili_globali[self.left.getname()]
        else:
            if not (self.left.getname() in Appoggio.variabili_locali):
                Appoggio.variabili_locali[self.left.getname()] = '__u64 ' + self.left.getname() #+ ';' 
                return Appoggio.variabili_locali[self.left.getname()] + ' = ' + self.right.rep()
            else:
                return self.left.getname() + ' = ' + self.right.rep()
        raise Exception("ERRORE: Variabile")
        #return 'Assignment(%s, %s)' % (self.left.rep(), self.right.rep())


class Call(BaseBox):
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.value = 0

    def eval(self, env):
        result = Null()
        return result

    def rep(self):
        #result = 'Call %s (' % self.name
        result = ''
        param_number = 0
        #if isinstance(self.args, Array):
        for statement in self.args.get_statements():
            param_number += 1
            result += ', ' + statement.rep()
        result += ')'
        call = 'hike_call_' + str(param_number) + '(' + find_Program(self.name, "1") + result
        return call


    def to_string(self):
        return "<call '%s'>" % self.name


class Return(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return self.value.eval(env)

    def rep(self):
        return 'return %s ' % (self.value.rep())

    def to_string(self):
        return "<return '%s'>" % self.name



class If(BaseBox):
    def __init__(self, condition, body, else_body=Null()):
        self.condition = condition
        self.body = body
        self.else_body = else_body

    def eval(self, env):
        condition = self.condition.eval(env)
        #print("IF Condition: " + str(self.condition.left.eval(env)) + " " + str(self.condition.operator) +" " + str(self.condition.right.eval(env)))
        if condition:
        #if Boolean(True).equals(condition).value:
            return self.body.eval(env)
        else:
            if type(self.else_body) is not Null:
                return self.else_body.eval(env)
        return Null()

    def rep(self):
        result = 'if (' + self.condition.rep() + ') {\n' + self.body.rep() + Appoggio.indent_level*'\t' + '}'
        if type(self.else_body) is not Null:
            result += '\n' + Appoggio.indent_level*'\t' +'else {\n' + self.else_body.rep() + Appoggio.indent_level*'\t' +'}'
        return result
        #return 'If(%s) \n\tThen(%s) \tElse(%s)' % (self.condition.rep(), self.body.rep(), self.else_body.rep())


class While(BaseBox):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def eval(self, env):
        #condition = self.condition.eval(env)
        i = 0
        while True:
            if not self.condition.eval(env):
                break
            #if i > 12: break
            i += 1
            self.body.eval(env)
        return Null()

    def rep(self):
        #Appoggio.indent_level += 1
        result = 'while (' + self.condition.rep() + ') {\n' + self.body.rep() + Appoggio.indent_level*'\t' + '}'
        return result
        #return 'while ( %s ) { \n %s \n}' % (self.condition.rep(), self.body.rep())
