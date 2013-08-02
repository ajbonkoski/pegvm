from inputter import *
import imp
from peg_action_sugar import *

ALLOW_NO_ACTIONS = False
ENABLE_ENTER_EXIT_DEBUG = False
ENABLE_RULE_DEBUG = False
ENABLE_ACTION_DEBUG = False
ENABLE_ACTION_DEBUG_ALL = False
def ConfigureParserInt(n):
    global ALLOW_NO_ACTIONS
    global ENABLE_ENTER_EXIT_DEBUG, ENABLE_RULE_DEBUG
    global ENABLE_ACTION_DEBUG, ENABLE_ACTION_DEBUG_ALL
    ALLOW_NO_ACTIONS = (n>>4)&1 == 1
    ENABLE_ENTER_EXIT_DEBUG = (n>>3)&1 == 1
    ENABLE_RULE_DEBUG = (n>>2)&1 == 1
    ENABLE_ACTION_DEBUG = (n>>1)&1 == 1
    ENABLE_ACTION_DEBUG_ALL = (n>>0)&1 == 1

class Grammar:
    def __init__(self, rules, lib_name=None):
        assert len(rules) >= 1
        self.lib_name = lib_name
        self.lib = imp.load_source('lib', self.lib_name+'.py') if self.lib_name != None else None
        self.top_rule = rules[0]
        self.rules = rules
        self.rule_dict = {}
        assert "EOI" not in rules
        for rule in rules:
            rule.set_grammar(self)
            self.rule_dict[rule.name] = rule
        self.rule_dict["EOI"] = EOI([])

    def set_top_rule(self, top_rule):
        rule = self.rule_dict[top_rule]
        self.top_rule = rule

    def parse(self, string, top_rule=None):
        inputter = Inputter(string)
        rule = self.top_rule if top_rule == None else self.rule_dict[top_rule]
        return rule.parse(inputter)

    def lookup_name(self, name):
        return self.rule_dict[name]

    def add_rule_ext(self, parent_name, rule_name, method):
        rule = self.rule_dict[parent_name]
        rule.rule_ext(rule_name, method)

    def add_new_rule(self, rule):
        rule.set_grammar(self)
        self.rule_dict[rule.name] = rule
        self.rules.append(rule)

    def __repr__(self):
        return "Grammar("+repr(self.rules)+(", lib_name='{0}'".format(self.lib_name) if self.lib_name != None else "")+")"

class Result:
    """returned by each node"""
    def __init__(self, good, elements, action):
        self.good = good
        self.elements = elements
        self.action = action
        self.name = None

    @staticmethod
    def success(elements, action=None):
        return Result(True, elements, action)

    @staticmethod
    def fail(elements, action=None):
        return Result(False, elements, action)

    @staticmethod
    def reduce_list(lst):
        return Result.success(sum([e.elements for e in lst]))

    def is_good_but_empty(self):
        return self.good and self.name == None and len(self.elements) == 0

    def set_name(self, name):
        self.name = name

    def _elements_to_arg_list(self):
        result_type = type(self)
        arg_list = []
        for elem in self.elements:
            if type(elem) == result_type:
                arg_list.append(elem._elements_to_arg_list())
            else:
                arg_list.append(elem)
        return arg_list

    def execute_action(self, action, lib):
        if not self.good:
            return self
        #print "_Action: "+self.name+"{"+str(action)+"}\n{", self._elements_to_arg_list(), "}"
        if action == None:
            if ALLOW_NO_ACTIONS:
                action = "self.name + '(' + str(arg) + ')'"
            else:
                print "Error: No Action for '"+self.name+"'"
                print "For: {"+str(self._elements_to_arg_list())+"}"
                exit(1)

        arg = self._elements_to_arg_list()
        if ENABLE_ACTION_DEBUG:
            print "Action: "+self.name+"{"+str(action)+"}\n{", self._elements_to_arg_list(), "}"
        val = eval(action if action != None else "''")
        if ENABLE_ACTION_DEBUG:
            print "Value: '"+str(val)+"'\n"
        new_result = Result.success([val])
        new_result.set_name(self.name)
        if action == None and not (ENABLE_ACTION_DEBUG and ENABLE_ACTION_DEBUG_ALL):
            return self
        else:
            return new_result

    def __bool__(self):
        return self.good
    __nonzero__ = __bool__

    def __repr__(self):
        return 'Result('+str(self.name)+', '+str(self.good)+', '+str([repr(elem) for elem in self.elements])+')'

    indent_level = 0
    def __str__(self):
        s = str(self.name)+': '+str(self.good)+'\n'
        self.__class__.indent_level += 1
        for elem in self.elements:
            str_elem = str(elem)
            if type(elem) == type(''):
                str_elem += '\n'
            s+= ' '*(4*self.__class__.indent_level) + str_elem
        self.__class__.indent_level -= 1
        return s

recurse_depth = 0
class Node:
    """base class: each node must have a 'children' list"""
    def __init__(self, children):
        self.children = children
        self.grammar = None

    def __str__(self):
        name = self.__class__.__name__
        return '[' + name + ': ' + ','.join([str(c) for c in self.children]) + ']'

    def parse(self, data):
        global recurse_depth
        if ENABLE_ENTER_EXIT_DEBUG:
            recurse_depth += 1
            print str(recurse_depth) + ": Entering 'do_parse' for: "+self.__class__.__name__+" with '"+data.peek_clean()+"'"
        result = self.do_parse(data)
        if ENABLE_ENTER_EXIT_DEBUG:
            recurse_depth -= 1
            print str(recurse_depth) + ": Leaving 'do_parse' for: "+self.__class__.__name__+"("+str(bool(result))+")"+" with '"+data.peek_clean()+"'"
        return result

    def set_grammar(self, grammar):
        self.grammar = grammar
        for child in self.children:
            if 'set_grammar' in dir(child):
                child.set_grammar(self.grammar)


def PEGNode(cls):
    return cls

@PEGNode
class EOI(Node):
    def do_parse(self, data):
        if data.eof():
            return Result.success([])
        else:
            return Result.fail([])

rule_announce_indent = 0
@PEGNode
class Rule(Node):
    def __init__(self, name_elem, children, action=None):
        self.children = children
        self.name = name_elem.get_name()
        self.action = action

    def do_parse(self, data):
        global rule_announce_indent
        if ENABLE_RULE_DEBUG:
            pre_str = ' '*(rule_announce_indent*4)
            print pre_str+"Entering Rule: "+self.name+" with '"+data.peek_clean()+"'"
            rule_announce_indent += 1
        result = self.children[0].parse(data)
        result.set_name(self.name)
        if ENABLE_RULE_DEBUG:
            rule_announce_indent -= 1
            print pre_str+"Leaving Rule: "+self.name+" with "+str(bool(result))
        return result.execute_action(self.action, self.grammar.lib)

    def rule_ext(self, rule_name, method):
        self.children[0].expr_ext(rule_name, method)

    def __repr__(self):
        return "Rule("+repr(Name([self.name]))+", "+repr(self.children)+(', action="""{0}"""'.format(self.action.replace("\\n", "\\\\n").replace("\n", "\\n")) if self.action != None else "")+")"

@PEGNode
class Expression(Node):
    def do_parse(self, data):
        for seq in self.children:
            data.save_state()
            result = seq.parse(data)
            if result:
                data.pop_backup_state()
                return result
            data.restore_state()
        return Result.fail([])

    def expr_ext(self, rule_name, method):
        expr = Expression([Prefix([Suffix([Name([rule_name])])])])
        if method == "prepend":
            self.children.insert(0, expr)
        elif method == "append":
            self.children.append(expr)
        else: assert False, "Method of extension not supported: '{0}'".format(method)

    def __repr__(self):
        return 'Expression('+repr(self.children)+')'

@PEGNode
class Sequence(Node):
    def do_parse(self, data):
        result_list = []
        for pre in self.children:
            result = pre.parse(data)
            if not result.is_good_but_empty():
                result_list.append(result)
            if not result:
                return Result.fail(result_list)
        return Result.success(result_list)

    def __repr__(self):
        return 'Sequence('+repr(self.children)+')'

@PEGNode
class Prefix(Node):
    def do_parse(self, data):
        # no prefix?
        if len(self.children) == 1:
            return self.children[0].parse(data)

        ## lookahead
        else:
            lookahead_type = self.children[0]
            lookahead_suffix = self.children[1]
            data.save_state()
            result = lookahead_suffix.parse(data)
            data.restore_state()
            if (result and lookahead_type == "&") or \
               (not result and lookahead_type == "!"):
                result.good = True
                return result
            else:
                return Result.fail(result.elements)

    def __repr__(self):
        return 'Prefix('+repr(self.children)+')'

@PEGNode
class Suffix(Node):
    def do_parse(self, data):
        primary = self.children[0]

        # no modifier?
        if len(self.children) == 1:
            return primary.parse(data)

        # has a modifier - and its greedy (because this is PEG)
        mod = self.children[1]

        if mod == "?":
            data.save_state()
            result = primary.parse(data)
            if result:
                data.pop_backup_state()
                return result
            else:
                data.restore_state()
                return Result.success([])

        else:
            ## its either "+" or "*", so try to get as many as possible until failure
            result_list = []
            while True:
                data.save_state()
                result = primary.parse(data)
                if not result:
                    data.restore_state()
                    break
                else:
                    data.pop_backup_state()
                    result_list.append(result)

            if mod == "+" and len(result_list) < 1:
                return Result.fail(result_list)
            else:
                return Result.success(result_list)

    def __repr__(self):
        return 'Suffix('+repr(self.children)+')'

@PEGNode
class Primary(Node):
    """base class for all primaries"""

@PEGNode
class Literal(Primary):
    def do_parse(self, data):
        literal = self.children[0]
        sofar = ''

        for i in range(len(literal)):
            if data.eof():
                return Result.fail([sofar, "eof"])
            ch = data.get_next()
            if ch != literal[i]:
                return Result.fail([sofar])
            else:
                sofar += ch

        return Result.success([sofar])

    def __repr__(self):
        return 'Literal(["'+self.children[0].replace("\n", "\\n").replace("\r", "\\r")+'"])'

@PEGNode
class Class(Primary):
    def do_parse(self, data):
        if data.eof():
            return Result.fail(["", "eof"])
        ch = data.get_next()
        for elem in self.children:
            if type(elem) == type(tuple()):
                start, end = elem
                if ord(ch) >= ord(start) and ord(ch) <= ord(end):
                    return Result.success([ch])
            else: ## its just a single char...
                if ord(ch) == ord(elem):
                    return Result.success([ch])

        # Searched all chars, but still not found... Fail!
        return Result.fail([ch])

    def __repr__(self):
        return 'Class('+repr(self.children)+')'

@PEGNode
class Any(Primary):
    def do_parse(self, data):
        if data.eof():
            return Result.fail(["", "eof"])
        ch = data.get_next()
        return Result.success([ch])

    def __repr__(self):
        return 'Any('+repr(self.children)+')'

@PEGNode
class Group(Primary):
    def do_parse(self, data):
        exp = self.children[0]
        return exp.parse(data)

    def __repr__(self):
        return 'Group('+repr(self.elements)+')'

class Name(Primary):
    def do_parse(self, data):
        name = self.get_name()
        exp = self.grammar.lookup_name(name)
        return exp.parse(data)

    def get_name(self):
        return self.children[0]

    def __repr__(self):
        return 'Name('+repr(self.children)+')'
