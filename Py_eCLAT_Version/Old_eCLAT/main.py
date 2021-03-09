#!/usr/bin/python3
# -*- coding: utf-8 -*-

__title__ = "eCLAT"
__version__ = "1.0"
__status__ = "unreleased"
__author__ = "Andrea Bernini"
__date__ = "2020 Dicembre 21"

import os
import struct
import sys
import argparse
import re
from lexer import Lexer
from parser import Parser


class Environment(object):
    def __init__(self):
        self.variables = {}
     

def run_file(args):
    fname = args
    with open(fname) as f:
        text_input = f.read()
    lexer = Lexer().get_lexer()
    tokens = delete_comment(lexer, text_input)    
    #for i in tokens:
    #    print(i)
    pg = Parser()
    pg.parse()
    parser = pg.get_parser()
    parser.parse(tokens).eval(Environment())

def delete_comment(lexer, source):
    comments = r'(#.*)(?:\n|\Z)'
    multiline = r'([\s]+)(?:\n)'

    comment = re.search(comments, source)
    while comment is not None:
        start, end = comment.span(1)
        assert start >= 0 and end >= 0
        # remove string part that was a comment
        source = source[0:start] + source[end:]
        comment = re.search(comments, source)

    line = re.search(multiline, source)
    while line is not None:
        start, end = line.span(1)
        assert start >= 0 and end >= 0
        # remove string part that was an empty line
        source = source[0:start] + source[end:]
        line = re.search(multiline, source)

    #print "source is now: %s" % source
    detect_indent(source)
    return lexer.lex(source)


def detect_indent(source):
    block = False
    indent_symbol = "    "
    line_num = 0
    for line_num, line in enumerate(source.splitlines(), 0):
        line = line.rstrip()
        line1 = line.replace("\t", indent_symbol)
    
        if line_num != 0:   
            #print(line_num, line1)
            if block == False and line1[0] == " ":
                raise Exception("Indentation Error at line " + str(line_num))
            
            if block and line1[0] != " ":
                block = False
                             
            if block:
                line_dedent = line1[:len(indent_symbol)]
                if line_dedent != indent_symbol:
                    raise Exception("Indentation Error at line " + str(line_num))         
                  
            config_chain = line1.split()
            if config_chain[0] == "config" or config_chain[0] == "chain":
                block = True          

def _count_leading_characters(line, char):
    count = 0
    for c in line:
        if c != char:
            break
        count += 1
    return count

def indent(line):
    if line[0] in (' ', '\t'):
        count = _count_leading_characters(line, line[0])
        if count > 8:
            raise Exception("Indentation Error")
        return line[0] * count         
            
      
            
            
#run_file("esempio.eclat")

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
