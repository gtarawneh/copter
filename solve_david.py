#!/usr/bin/env python

from parse_sg     import mine_concepts
from json         import dumps as jsons
from itertools    import product
from itertools    import starmap
from itertools    import combinations
from itertools    import permutations
from cover        import solve
from concepts     import *
from collections  import defaultdict

def main():
	file = "examples/david_cell.sg"
	sg, cause_concepts, or_cause_concepts = mine_concepts(file, False)
	concepts = cause_concepts + or_cause_concepts
	costs = defaultdict(lambda : 1)
	spec = [
		OrCause(
			Literal("a1", "+"),
			Literal("r", "+"),
			Literal("a", "-")
		),
		Cause(
			Literal("a1", "-"),
			Literal("a", "+")
		),
		Cause(
			Literal("r", "-"),
			Literal("a", "+")
		)
	]
	spec = concepts
	graph = dict()
	all_signals = sg.encoding
	literals = starmap(Literal, product(all_signals, "+-"))
	# for cause in cause_concepts:
	for cond, tran in permutations(literals, 2):
		if cond == ~tran:
			continue
		signals = set(sg.encoding)
		signals.discard(cond.signal)
		signals.discard(tran.signal)
		other_literals = starmap(Literal, product(signals, "+-"))
		mk_or_conc = lambda cond2 : OrCause(cond, cond2, tran)
		cause = Cause(cond, tran)
		cause_children = map(mk_or_conc, other_literals)
		if all([x in spec for x in cause_children]) or cause in spec:
			graph[cause] = cause_children
	# "orGate a b c = or_cause_rrr a b c . cause a- c- . cause b- c-"
	# "norGate a b c = or_cause_rrf a b c . cause a- c+ . cause b- c+",
	or_causes = set().union(*map(set, graph.values()))
	for y in all_signals:
		remaining = set(all_signals) - set([y])
		for a, b in combinations(remaining, 2):
			or_cause = OrCause(
				Literal(a, "+"),
				Literal(b, "+"),
				Literal(y, "-")
			)
			nor_gate = NorGate(a, b, y)
			cause1 = Cause(Literal(a, "-"), Literal(y, "+"))
			cause2 = Cause(Literal(b, "-"), Literal(y, "+"))
			nor_children = [or_cause, cause1, cause2]
			if all([x in spec for x in nor_children]) or nor_gate in spec:
				graph[nor_gate] = nor_children
	solve(graph, costs, spec)

if __name__ == "__main__":
	main()
