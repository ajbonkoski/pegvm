import peg
import imp
from sys import argv

peg_peg = open('peg_grammars/simpler_peg.peg').read()

def peg_peg_test(debug_mode):
    global result
    peg.ConfigureParserInt(debug_mode)
    result = PEG_GRAMMAR.parse(peg_peg)

def gen():
    print 'from peg import *'
    print 'PEG_GRAMMAR='+result.elements[0]

def usage(name):
    print name+" <grammar-name> <debug-mode> [-gen]"

if __name__ == '__main__':
    if len(argv) < 3:
	usage(argv[0])
	exit(1)

    ## extract args
    grammar_name = argv[1]
    debug_mode = int(argv[2])
    is_gen_mode = len(argv) >= 4 and argv[3] == '-gen'

    ## load grammar
    peg_grammar = imp.load_source('peg_grammar', 'generated_grammars/'+grammar_name+'.py')
    PEG_GRAMMAR = peg_grammar.PEG_GRAMMAR

    ## run it!
    peg_peg_test(debug_mode)
    if is_gen_mode: gen()
    else: print result
