import sys

def parse_grammar(syntax_grammar, name, data):
    parsed = syntax_grammar.parse(data)
    if not parsed:
        sys.stderr.write("error: failed to correctly parse '{}'\n".format(name))
        sys.exit(1)
    return parsed.elements[0]
