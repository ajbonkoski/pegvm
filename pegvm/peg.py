""""PegVM main module including each of the classes implementing
the parsing engine."""

import imp
from inputter import *
from peg_action_lib import *

class PegvmError(Exception): pass


OPTIONS = {
  'allow-no-actions':  False,
  'enter-exit-debug':  False,
  'rule-debug':        False,
  'action-debug':      False,
  'action-debug-all':  False
}

def ConfigureParserInt(n):
    global OPTIONS
    OPTIONS['allow-no-actions'] = (n>>4)&1 == 1
    OPTIONS['enter-exit-debug'] = (n>>3)&1 == 1
    OPTIONS['rule-debug']       = (n>>2)&1 == 1
    OPTIONS['action-debug']     = (n>>1)&1 == 1
    OPTIONS['action-debug-all'] = (n>>0)&1 == 1

###################################################################
##################### Action Helper functions #####################
###################################################################
def _action_transform(action):
    for i in range(10):
        s = str(i)
        action = action.replace('...'+s, 'Nth3('+s+')')
    for i in range(10):
        s = str(i)
        action = action.replace('..'+s, 'Nth2('+s+')')
    for i in range(10):
        s = str(i)
        action = action.replace('.'+s,  'Nth1('+s+')')
    return action


STR_TYPE = type('')
LIST_TYPE = type([])
DATA = None    # args is dropped here for each Action
SZ = 0
def p(d): print d; return d
def pexit(*args): print args; exit(1)

def _merge_recursive(data):
    t = type(data)
    if t == STR_TYPE:
        return data
    assert(t == LIST_TYPE)
    return ''.join([_merge_recursive(a) for a in data])

def merge(i=None, n=None):
    if i == None:
        return _merge_recursive(DATA)
    elif i < len(DATA) and (n == len(DATA) or n == None):
        return _merge_recursive(DATA[i])
    else:
        return ''

def Nth1(i): return DATA[i]
def Nth2(i): return DATA[i][0]
def Nth3(i): return DATA[i][0][0]

def arg_array1(i, j, require=None):
    if require != None and len(DATA) < require:
        return []
    return [a[j] for a in DATA[i]]

def arg_array2(i, j, require=None):
    if require != None and len(DATA) < require:
        return []
    return [a[j][0] for a in DATA[i]]

def merge_array1(i, j, require=None):
    return _merge_recursive(arg_array1(i, j, require))
merge_array = merge_array1

def merge_array2(i, j, require=None):
    return _merge_recursive(arg_array2(i, j, require))

def arg_array3(i, j, require=None):
    if require != None and len(DATA) < require:
        return []
    return [a[j][0][0] for a in DATA[i]]

def merge_array3(i, j, require=None):
    return _merge_recursive(arg_array3(i, j, require))

def stringify(data):
    assert(type(data) == STR_TYPE)
    return '"{}"'.format(data)

def sel(a, b, ck): return a if ck == SZ else b

###################################################################
########################### PEG Classes ###########################
###################################################################

class Grammar:
    def __init__(self, rules, lib_name=None):
        """Create a grammar with a list of Rules and optionally a python
        library module to call from the actions"""
        if len(rules) < 1:
            raise PegvmException("Cannot create a grammar with no rules!")
        if "EOI" in rules:
            raise PegvmException("Invalid rule name: 'EOI'")

        self.lib_name = lib_name
        self.lib = imp.load_source('lib', self.lib_name+'.py') if self.lib_name != None else None
        self.top_rule = rules[0]
        self.rules = rules
        self.rule_dict = {}
        for rule in rules:
            rule.set_grammar(self)
            self.rule_dict[rule.name] = rule
        self.rule_dict["EOI"] = EOI([])

    def __repr__(self):
        return "Grammar({}, lib_name='{}'".format(self.rules, self.lib_name)

    def parse(self, string, top_rule=None):
        """Parse the passed string using this Grammar. Optionally, user can
        provide a top_rule to start the parsing."""
        inputter = Inputter(string)
        rule = self.top_rule if top_rule == None else self.rule_dict[top_rule]
        return rule.parse(inputter)

    def lookup_name(self, name):
        """Finds and returns the Rule object corresponding to 'name'"""
        if name not in self.rule_dict:
            raise PegvmException("Failed to find rule named '{}'".format(name))
        return self.rule_dict[name]


class Result:
    """Result is a generic object returned by each parsing Node."""

    def __init__(self, good, elements, action):
        """Initialize a new Result with a boolean denoting whether the parse
        was successful (good), the individual elements, and an action to
        perform on the elements."""
        self.good = good
        self.elements = elements
        self.action = action
        self.name = None

    def __bool__(self):
        return self.good
    __nonzero__ = __bool__

    def __repr__(self):
        return 'Result({}, {}, {})'.format(self.name, self.good, self.elements)

    indent_level = 0
    def __str__(self):
        s = '{}: {}\n'.format(self.name, self.good)
        self.__class__.indent_level += 1
        for elem in self.elements:
            str_elem = str(elem)
            if type(elem) == type(''):
                str_elem += '\n'
            s+= ' '*(4*self.__class__.indent_level) + str_elem
        self.__class__.indent_level -= 1
        return s

    @staticmethod
    def success(elements, action=None):
        """Create a Result object that denotes parse success."""
        return Result(True, elements, action)

    @staticmethod
    def fail(elements, action=None):
        """Create a Result object that denotes parse failure."""
        return Result(False, elements, action)

    def is_good_but_empty(self):
        """Deprecated: Removal coming to an API near you."""
        return self.good and self.name == None and len(self.elements) == 0

    def set_name(self, name):
        """Set the name of the parsing Node that created this Result"""
        self.name = name

    def _elements_to_arg_list(self):
        """Deprecated: Removal coming to an API near you."""
        result_type = type(self)
        arg_list = []
        for elem in self.elements:
            if type(elem) == result_type:
                arg_list.append(elem._elements_to_arg_list())
            else:
                arg_list.append(elem)
        return arg_list

    def execute_action(self, action, lib):
        """Execute the associated action on the 'elements', producing a new result."""
        if not self.good:
            return self
        #print "_Action: "+self.name+"{"+str(action)+"}\n{", self._elements_to_arg_list(), "}"
        if action == None:
            if OPTIONS['allow-no-actions']:
                action = "self.name + '(' + str(arg) + ')'"
            else:
                print "Error: No Action for '"+self.name+"'"
                print "For: {"+str(self._elements_to_arg_list())+"}"
                exit(1)

        ## setup the helpers, and goodies
        arg = self._elements_to_arg_list()
        global DATA; DATA = arg
        global SZ; SZ = len(DATA)
        action = _action_transform(action);

        if OPTIONS['action-debug']:
            print "Action: "+self.name+"{"+str(action)+"}\n{", self._elements_to_arg_list(), "}"
        val = eval(action if action != None else "''")
        if OPTIONS['action-debug']:
            print "Value: '"+str(val)+"'\n"
        new_result = Result.success([val])
        new_result.set_name(self.name)
        if action == None and not (OPTIONS['action-debug'] and OPTIONS['action-debug-all']):
            return self
        else:
            return new_result


class Node:
    """Base class for all "parsing" nodes. Each node should have a children
    list, containing its sub-parsing-nodes."""

    def __init__(self, children):
        """Initialize a new Node with a list of children"""
        self.children = children
        self.grammar = None

    def __str__(self):
        name = self.__class__.__name__
        return '[{}:{}]'.format(name, ','.join(map(str, self.children)))

    _recurse_depth = 0
    def parse(self, data):
        """Perform the parsing of this Node. This is a wrapper function
        around the "real" virtual method "do_parse"""

        ## before actions
        if OPTIONS['enter-exit-debug']:
            self.__class__._recurse_depth += 1
            print str(self.__class__._recurse_depth) + ": Entering 'do_parse' for: "+self.__class__.__name__+" with '"+data.peek_clean()+"'"

        ## real work
        result = self.do_parse(data)

        ## after actions
        if OPTIONS['enter-exit-debug']:
            self.__class__._recurse_depth -= 1
            print str(self.__class__._recurse_depth) + ": Leaving 'do_parse' for: "+self.__class__.__name__+"("+str(bool(result))+")"+" with '"+data.peek_clean()+"'"

        return result

    def set_grammar(self, grammar):
        """Set the Grammar object containing this Node"""
        self.grammar = grammar
        for child in self.children:
            if 'set_grammar' in dir(child):
                child.set_grammar(self.grammar)


def PEGNode(cls):
    """Decorates all PEG Node classes. Currently is a noop."""
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
        if OPTIONS['rule-debug']:
            pre_str = ' '*(rule_announce_indent*4)
            print pre_str+"Entering Rule: "+self.name+" with '"+data.peek_clean()+"'"
            rule_announce_indent += 1
        result = self.children[0].parse(data)
        result.set_name(self.name)
        if OPTIONS['rule-debug']:
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
