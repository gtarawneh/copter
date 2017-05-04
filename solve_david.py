#!/usr/bin/env python

from parse_sg import mine_concepts
from json     import dumps as jsons
from causality import *
from itertools import product
from itertools import starmap
from itertools import combinations

def main():
	file = "examples/david_cell.sg"
	sg, cause_concepts, or_cause_concepts = mine_concepts(file, False)
	concepts = cause_concepts + or_cause_concepts
	graph = dict()
	signals = sg.encoding
	literals = starmap(Literal, product(signals, "+-"))
	# for cause in cause_concepts:
	for cond, tran in combinations(literals, 2):
		signals = set(sg.encoding)
		signals.discard(cond.signal)
		signals.discard(tran.signal)
		other_literals = starmap(Literal, product(signals, "+-"))
		mk_or_conc = lambda cond2 : OrCause(cond, cond2, tran)
		cause = Cause(cond, tran)
		graph[cause] = map(mk_or_conc, other_literals)
	for key, val in graph.iteritems():
		print "%-16s : %s" % (key, map(str, val))
	# "orGate a b c = or_cause_rrr a b c . cause a- c- . cause b- c-"

if __name__ == "__main__":
	main()
