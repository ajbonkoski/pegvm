#!/usr/bin/python
import imp
import peg
from peg import *
from sys import argv
import os

DIR = os.path.dirname(os.path.realpath(__file__))
peg_grammar = imp.load_source('peg_grammar', DIR+'/generated_grammars/gen_peg_grammar.py')
PEG_GRAMMAR = peg_grammar.PEG_GRAMMAR

def usage(name):
    print name+" <syntax-file> <syntax-debug-mode> <input-file> <input-debug-mode> [-gen]"

def parse_grammar(name, grammar):
    parsed = PEG_GRAMMAR.parse(grammar)
    if not parsed:
        print "Error: Failed to correctly parse '{}'".format(name)
        exit(1)
    return parsed.elements[0]

def gen(result):
    elem = result.elements[0]
    print "from peg import *"
    print "GRAMMAR="+elem

if __name__ == '__main__':
    if len(argv) < 5:
        usage(argv[0])
        exit(1)

    ## extract args
    syntax_file = argv[1]
    syntax_debug_mode = int(argv[2])
    input_file = argv[3]
    input_debug_mode = int(argv[4])
    is_gen = argv[5] == '-gen' if len(argv) >= 6 else False

    syntax_data = open(syntax_file).read()
    input_data  = open(input_file).read()

    ## run it!
    peg.ConfigureParserInt(syntax_debug_mode)
    GRAMMAR = eval(parse_grammar('syntax', syntax_data))

    peg.ConfigureParserInt(input_debug_mode)
    result = GRAMMAR.parse(input_data)
    if result:
        if is_gen: gen(result)
        else: print result.elements[0]
    else:
        "Error: Failed to correctly parse"

