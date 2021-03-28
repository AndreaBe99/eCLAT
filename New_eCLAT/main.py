#!/usr/bin/python3
# -*- coding: utf-8 -*-

__title__ = "eCLAT"
__version__ = "2.0"
__status__ = "unreleased"
__author__ = "Andrea Bernini"
__date__ = "2021 Marzo 03"


import sys
import argparse
import re
from lexer import Lexer
from parser import Parser

from rply.errors import ParserGeneratorWarning
import warnings


# Soppressione dei Token inutilizzati
if not sys.warnoptions:
    warnings.simplefilter("ignore")
    warnings.warn("deprecated", ParserGeneratorWarning)


class Environment(object):
    def __init__(self):
        self.variables = {}


def run_file(args):
    fname = args
    with open(fname) as f:
        text_input = f.read()
    lexer = Lexer().get_lexer()
    tokens = detect_indent(lexer, text_input)
    #for i in tokens:
    #    print(i)
    pg = Parser()
    pg.parse()
    parser = pg.get_parser()
    parser.parse(tokens).eval(Environment())

def detect_indent(lexer, source):
    text = ""
    block = False
    indent_symbol = " "
    dedent_number = 0
    indent_number = 0
    indent_stack = [0]
    
    comments = r'(#.*)(?:\n|\Z)'
    
    for line_num, line in enumerate(source.splitlines(), 0):
        line = line.rstrip()
        line = line.replace("\t", indent_symbol*4)

        # Rimuovi il commento dalla riga
        comment = re.search(comments, line)
        while comment is not None:
            start, end = comment.span(1)
            assert start >= 0 and end >= 0
            # rimuovi la stringa che matcha con il commento
            line = line[0:start] + line[end:]
            comment = re.search(comments, line)
        
        # Se la riga non è vuota
        if line.strip():
            
            # Controlla se l'indentazione è corretta altrimenti inseririsci il token DEDENT
            if line[0:indent_number] == indent_symbol*indent_number:
                if line[indent_number] == " ":
                    raise IndentationError("at line " + str(1+line_num))
            elif not block:
                while line[0:indent_number] != indent_symbol*indent_number:
                    indent_number -= 4
                    indent_stack.pop()
                    dedent_number += 1
                line = " _dedent "*dedent_number + line
                dedent_number = 0
            else: 
                raise IndentationError("at line " + str(1+line_num))
            
            # Se è la riga successiva al Block aggiungi il token INDENT    
            if block:
                line = " _indent " + line
                indent_stack.append(indent_number)
                block = False
            
            # Se lo statement successivo è un Block (ovvero :)    
            if line[len(line)-1:len(line)] == ":":
                indent_number += 4
                block = True  
            
            # Se è l'ultima riga aggiungi i token DEDENT rimasti nello stack  
            if line_num == len(source.splitlines()) - 1:
                while len(indent_stack) > 1:
                    indent_number -= 4
                    indent_stack.pop()
                    dedent_number += 1
            
            text = text + line + " _dedent "*dedent_number + "\n"
    
    # Nel caso le ultime righe siano vuote o commenti inserisce i DEDENT rimanenti
    for dedent in range(len(indent_stack)-1):
        text += " _dedent "
    #print(text)
    return lexer.lex(text)



#run_file("test2.eclat")
#"""
def show_chain():
    print("Show Chain")

def show_chain_id(id_chain):
    print("Show Chain ID: " + id_chain)

def show_table():
    print("Show Table")

def show_table_name(name):
    print("Show Table Name: " + name)

def show_table_name_key(name, key):
    print("Show Table Name: " + name + " Key: " + key)

def show_table_dump():
    print("Show Table Dump")

def flush_chain():
    print("Flush Chain")

def flush_chain_name(name):
    print("Flush Chain Name: " + name)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('--run', type=run_file, help='Interpreter')

    #### PROVA #####
    group = parser.add_argument_group('show chain | table')
    group.add_argument('--show', metavar='chain | table', help='Show Chain or Table')
    
    group.add_argument('--id', type=str, help='Use after --show')
    
    group.add_argument('--name', type=str, help='Show Table Name | Flush Chain Name')
    group.add_argument('--key', type=str, help='Use only after --name')
    group.add_argument('--dump', action='store_true', help='Show Table Dump')
    
    
    group = parser.add_argument_group('flush chain')
    group.add_argument('--flush', metavar='chain', help='Flush Chain')
    #group.add_argument('--name', type=str, help='Flush Chain Name')
    #################
    
    #### PROVA SUBPARSER ####
    # subparsers = parser.add_subparsers(help='eclat sub-commands')
    
    # showChain = subparsers.add_parser('--show chain', help='sub-command show chain and show table')
    # group = showChain.add_argument_group("Show Chain")
    # #group.add_argument('--show', metavar='chain', help='Show Chain or Table')
    # group.add_argument('--id', type=str, help='Use after --show')
    
    # showTable = subparsers.add_parser('--show table', help='sub-command show chain and show table')
    # group = showTable.add_argument_group("Show Table")
    # #group.add_argument('--show', metavar='table', help='Show Chain or Table')
    # group.add_argument('--name', type=str, help='Show Table Name')
    # group.add_argument('--key', type=str, help='Use only after --name')
    # group.add_argument('--dump', action='store_true', help='Show Table Dump')
    
    # flushChain = subparsers.add_parser('--flush chain', help='sub-command show chain and show table')
    # group = flushChain.add_argument_group("Flush Chain")
    # #group.add_argument('--flush', metavar='chain', help='Flush Chain')
    # group.add_argument('--name', type=str, help='Flush Chain Name')
    ############

    args = parser.parse_args()
    
    
    #### SHOW CHAIN
    if args.show == "chain":
        if not args.show and args.id:
            raise TypeError("Need --show chain before --id")
        elif args.show and args.id:
            show_chain_id(args.id)
        elif args.show:
            show_chain()
            
    #### SHOW TABLE      
    elif args.show == "table":
        if not args.show and args.name and args.key:
            raise TypeError("Need --show table before --name")
        elif  args.show and not args.name and args.key:
            raise TypeError("Need --name before --key")
        elif args.show and args.name and args.key:
            show_table_name_key(args.name, args.key)
        elif args.show and args.name and not args.key:
            show_table_name(args.name)
        elif args.show and args.dump:
            show_table_dump()
        elif args.show:
            show_table()
    
    #### FLUSH CHAIN
    else:
        if not args.flush and args.name:
            raise TypeError("Need --flush chain before --name")
        elif args.flush and args.name:
            flush_chain_name(args.name)
        elif args.flush:
            flush_chain()   
#"""
