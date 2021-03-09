from rply.token import BaseBox

class Program():
    def __init__(self, value):
        self.value = []
        self.value.append(value)
    
    def add_value(self, value):
        self.value.insert(0,value)
    
    def eval(self, env):
        #print("Statement count: %s" % len(self.value))
        result = None
        for statement in self.value:
            result = statement.eval(env)
        return result
    
    def get_value(self):
        return self.value


class CodeC():
    def __init__(self, value):
        self.value = value

    def to_string(self):
        return str(self.value)

    def eval(self, env):
        return self.value

class Annotation():
    def __init__(self, table_name, key, value):
        self.table_name = table_name
        self.key = key
        self.value = value

    def to_string(self):
        return str(self.value)

    def eval(self, env):
        # Qui va richiamata la funzione per la gestione delle "annotazioni"
        print(self.table_name, self.key, self.value)
        return self.value

