from peg import *
PEG_GRAMMAR  = Grammar([
	Rule(Name(["Grammar"]), [
		Sequence([
		       	Name(["S"]),
			Suffix([Name(["Definition"]), '+']),
			Name(["EOI"])
		]),
	], """ "Grammar([" + ", ".join([a[0] for a in arg[1]]) + "])" """),
	Rule(Name(["Definition"]), [
		Sequence([
			Name(["Name"]),
			Name(["Arrow"]),
			Name(["Expression"]),
			Suffix([Name(["Action"]), '?']),
			Name(["S"])
		])
	], """ "Rule("+ arg[0][0] + ", [" + arg[2][0] + "]" + (", "+'""'+'" '+arg[3][0]+' "'+'""' if arg[3][0] != '' else "") + ")" """),
	Rule(Name(["Expression"]), [
		Sequence([
			Name(["Sequence"]),
			Suffix([Group([
				Sequence([
					Name(["OR"]),
					Name(["Sequence"])
				])
			]), '*'])
		])
	], """ "Expression([" + ", ".join([arg[0][0]] + ([a[1][0] for a in arg[1]] if len(arg) > 1 else [])) + "])" """),
	Rule(Name(["Sequence"]), [
		Suffix([Name(["Prefix"]), '+'])
	], """ "Sequence([" + ", ".join([a[0] for a in arg]) +"])" """),
	Rule(Name(["Prefix"]), [
		Sequence([
			Suffix([Group([
				Expression([
					Name(["LOOKAHEAD"]),
					Name(["NOT"]),
				])
			]), '?']),
			Name(["Suffix"])
		]),
	], """ "Prefix([" + ("'"+arg[0][0]+"'" + ", " + arg[1][0] if len(arg) > 1 != '' else arg[0][0]) + "])" """),
	Rule(Name(["Suffix"]), [
		Sequence([
			Name(["Primary"]),
			Suffix([Group([
				Expression([
					Name(["OPTION"]),
					Name(["ONEORMORE"]),
					Name(["ZEROORMORE"])
				])
			]), '?']),
			Name(["S"])
		])
	], """ "Suffix([" + arg[0][0] + (", '"+arg[1][0]+"'" if arg[1][0] != '' else '') + "])" """),
	Rule(Name(["Primary"]), [
		Expression([
			Sequence([
				Name(["Name"]),
				Prefix(['!', Name(["Arrow"])])
			]),
			Name(["GroupExpr"]),
			Name(["Literal"]),
			Name(["Class"]),
			Name(["ANY"])
		])
	], """ arg[0][0] if len(arg) > 1 else arg[0] """),
	Rule(Name(["Name"]), [
		Sequence([
			Name(["Identifier"]),
			Name(["S"])
		])
	], """ "Name(['"+arg[0][0]+"'])" """),
	Rule(Name(["GroupExpr"]), [
		Sequence([
			Name(["OPEN"]),
			Name(["Expression"]),
			Name(["CLOSE"]),
		])
	], """ arg[1][0] """),
	Rule(Name(["Literal"]), [
		Expression([
			Sequence([
				Name(["Quote"]),
				Suffix([Sequence([
					Prefix(['!', Name(["Quote"])]),
					Name(["Char"])
				]), '*']),
				Name(["Quote"]),
				Name(["S"]),
			]),
			Sequence([
				Name(["DoubleQuote"]),
				Suffix([Sequence([
					Prefix(['!', Name(["DoubleQuote"])]),
					Name(["Char"])
				]), '*']),
				Name(["DoubleQuote"]),
				Name(["S"]),
			]),
		])
	], """ "Literal([" + quot(''.join([a[1][0] for a in arg[1]])) + "])" """),
	Rule(Name(["Class"]), [
		Sequence([
			Literal(['[']),
			Suffix([Sequence([
				Prefix(['!', Literal([']'])]),
				Name(["CharRange"])
			]), '*']),
			Literal([']']),
			Name(["S"])
		])
	], """ "Class(" + str([a[1][0] for a in arg[1]]) + ")" """),
	Rule(Name(["CharRange"]), [
		Expression([
			Sequence([
				Name(["Char"]),
				Literal(['-']),
				Name(["Char"])
			]),
			Name(["Char"])
		])
	], """ arg[0] if len(arg) == 1 else (arg[0][0], arg[2][0]) """),

	Rule(Name(["Char"]), [Any([])], """ arg[0] """),  ## The actual grammar uses this for allowing
                                  ## Special Escaped Chars in the Char class, but
                                  ## this isn't needed for the bootstrapping

	Rule(Name(['Action']), [
		Sequence([
			Literal('{'),
			Suffix([
				Sequence([
					Prefix(['!', Literal('}')]),
					Any([])
				]),
			'*']),
			Literal('}')
		])
	], """ ''.join([a[1][0] for a in arg[1]]) """),

	Rule(Name(["Arrow"]),       [Sequence([ Literal(["<-"]), Name(["S"])]) ], "''"),
	Rule(Name(["OR"]),          [Sequence([ Literal(["/"]),  Name(["S"])]) ], "''"),
	Rule(Name(["LOOKAHEAD"]),   [Sequence([ Literal(["&"]),  Name(["S"])]) ], """ '&' """),
	Rule(Name(["NOT"]),         [Sequence([ Literal(["!"]),  Name(["S"])]) ], """ '!' """),
	Rule(Name(["OPTION"]),      [Sequence([ Literal(["?"]),  Name(["S"])]) ], """ '?' """),
	Rule(Name(["ZEROORMORE"]),  [Sequence([ Literal(["*"]),  Name(["S"])]) ], """ '*' """),
	Rule(Name(["ONEORMORE"]),   [Sequence([ Literal(["+"]),  Name(["S"])]) ], """ '+' """),
	Rule(Name(["OPEN"]),        [Sequence([ Literal(["("]),  Name(["S"])]) ], """ '(' """),
	Rule(Name(["CLOSE"]),       [Sequence([ Literal([")"]),  Name(["S"])]) ], """ ')' """),
	Rule(Name(["ANY"]),         [Sequence([ Literal(["."]),  Name(["S"])]) ], """ 'Any([])' """),
	Rule(Name(["Quote"]),       [Literal(["'"])], """ "'" """),
	Rule(Name(["DoubleQuote"]), [Literal(['"'])], """ '"' """),

	Rule(Name(["EOL"]), [Expression([ Literal(['\r\n']), Literal(['\n']), Literal(['\r']) ])], "''"),
	Rule(Name(["Comment"]), [
		Sequence([
			Literal(['#']),
			Suffix([
				Sequence([ Prefix(['!', Name(["EOL"])]), Any([])]),
				'*'
			]),
			Expression([
				Name(["EOL"]),
				Name(["EOI"])
			])
		]),
	], "''"),
	Rule(Name(["S"]), [
		Suffix([ Expression([
			Literal([' ']),
			Literal(['\t']),
			Name(["EOL"]),
			Name(["Comment"])
		]), '*'])
	], "''"),

	Rule(Name(["Identifier"]), [
		Sequence([
			Class([('a', 'z'), ('A', 'Z')]),
			Suffix([ Class([('a', 'z'), ('A', 'Z'), ('0', '9')]), '*' ])
		]),
	], """arg[0][0] + (''.join([a[0] for a in arg[1]]) if len(arg) > 1 else '') """)
])
