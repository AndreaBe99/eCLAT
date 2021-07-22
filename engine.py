from parser.parser import getParser, getEnvironment
from parser.lexer import getLexer
from parser.utils import lexer_preprocessor
import os


class EclatEngine:
    def __init__(self, package_name):
        """
        Build lexer and parser
        """
        self.lexer, syntax_tokens = getLexer()                  # lg.build()
        self.parser = getParser(syntax_tokens, package_name)    # pg.build()
        self.env = getEnvironment()                             # get Environment for eclat variable                         

    def translate_to_c(self, script):
        """
        Translate the script from Eclat to C
        Generate the Hyke program
        """
        print(f"Translating script: \n{script}")

        # Checking indentation and remove comment
        preprocessed_script = lexer_preprocessor(script)

        # Lexical analysis
        tokens = self.lexer.lex(preprocessed_script)

        # Syntactic analysis
        program = self.parser.parse(tokens)

        # Run the AST's root for translation
        code = program.exec(self.env)

        print(f"Translated to: \n{code}")

        return code


    def run(self, script):
        """
        Translate an ECLAT script into an HIKe Chain.
        Compile the chain and load it to memory.
        """
        # Ogni volta che viene eseguita la traduzione viene
        # riscritto/aggiornato il file "registry.csv" che si trova 
        # all'interno della cartella "runtime". In questo file 
        # vengono memorizzate tutte le chain "caricate" tramite eCLAT, 
        # con associato: 
        # - ID progressivo delle chain;
        # - il nome del modulo;
        # - nome della chain.
        # NOTA: Se presenti due chain con lo stesso nome all'interno
        #       dello stesso modulo genera un errore visto che devono
        #       essere univoche. 

        hike_source = self.translate_to_c(script)

        # Write C file in runtime/output
        hike_source_file = os.path.join(os.path.dirname(__file__), "runtime/output/eclat_output.hike.c")
        f = open(hike_source_file, "w")
        f.write(hike_source)
        f.close()

        return True
