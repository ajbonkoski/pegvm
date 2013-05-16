from peg import *

# grammar = Grammer([
#         Expresion([
#     Sequence([
#             Prefix([
#                     Suffix([
#                             Literal(["peg"]),
#                             "+"
#                     ])
#             ])
#      ])
# ])

basic_grammar = Grammar([Rule("basic", [
                    Suffix([
                            Literal(["peg"]),
                            "*"
                    ])])
            ])


def basic():
    print basic_grammar
    result = basic_grammar.parse('')
    print result

arithmetic = Grammar([
        Rule("expr", [
                Sequence([
                        Name(["integer"]),
                        Suffix([Name(["space"]), '*']),
                        Suffix([Name(["expr_end"]), '*']),
#                        Name(["eof"])
                ])
        ]),
        Rule("expr_end", [
                Sequence([
                        Name(["add_sub"]),
                        Suffix([Name(["space"]), '*']),
                        Name(["integer"]),
                        Suffix([Name(["space"]), '*']),
                ])
        ]),
        Rule("integer", [
                Suffix([Class(['0', '9']), '+'])
        ]),
        Rule("space", [
                Class([' ', ' '])
        ]),
        Rule("eof", [
                Prefix(["!", Any([])])
        ]),
        Rule("add_sub", [
                Expresion([
                        Class(['+', '+']),
                        Class(['-', '-'])
                ])
        ]),
])
