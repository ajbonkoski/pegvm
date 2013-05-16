#!/usr/bin/python
import imp
import peg
from peg import *
from sys import argv
import os

DIR = os.path.dirname(os.path.realpath(__file__))
# peg_grammar = imp.load_source('peg_grammar', DIR+'/generated_grammars/gen_peg_grammar.py')
# PEG_GRAMMAR = peg_grammar.PEG_GRAMMAR

def usage(name):
    print "usage: {} <syntax> <input-file> <input-debug-mode>".format(name)

if __name__ == '__main__':
    if len(argv) < 4:
	usage(argv[0])
	exit(1)

    ## extract args
    syntax_file = argv[1]
    input_file = argv[2]
    input_debug_mode = int(argv[3])

    ## run it!
    input_data = open(input_file).read()
    peg.ConfigureParserInt(input_debug_mode)
    GRAMMAR = imp.load_source('grammar', syntax_file).GRAMMAR
    result = GRAMMAR.parse(input_data)
    if result:
        print result.elements[0]
    else:
        "Error: Failed to correctly parse"

