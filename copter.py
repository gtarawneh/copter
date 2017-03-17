#!/usr/bin/env python

import graphs
import json
import parser
import docopt
from z3 import *

usage = """Composability Optimizer (Copter)

Usage:
  copter.py [--mode=<m>] [--output=<file>] [--quiet] <problem.json>
  copter.py --version

Options:
  -m --mode=<m>       Choose optimization mode (unique/count) [default: unique].
  -o --output=<file>  Write solution to json file.
  -q --quiet          Suppress output.

"""

def get_atoms(rules):
	"""
	Return atom modules.

	Atoms are modules that cannot be decomposed.
	"""
	modules = graphs.get_nodes(rules)
	non_atoms = rules.keys()
	atoms = set(modules).difference(non_atoms)
	return list(atoms)

def prune_problem(problem):
	"""
	Remove rules that cannot be applied to the system.
	"""
	system = problem["system"]
	rules = problem["rules"]
	# compute closure and reverse closure
	rev_rules = graphs.get_reversed(rules)
	closure = graphs.get_closure(rules)
	rev_closure = graphs.get_closure(rev_rules)
	# compute lineage and family
	lineage = set() # ancestors and descendents of modules in system
	lineage.update(system)
	for module in system:
		lineage.update(closure.get(module, []))
		lineage.update(rev_closure.get(module, []))
	family = set() # lineage + ancestors and descendents of all members
	for module in lineage:
		family.update(closure.get(module, []))
		family.update(rev_closure.get(module, []))
	# keep rules of family members, remove everything else
	problem["rules"] = {k:v for k,v in rules.iteritems() if k in family}

def optimize(problem, mode="unique"):

	# in "unique" mode : a . a == a
	# in "count" mode  : a . a != a

	prune_problem(problem)

	rules, system = problem["rules"], problem["system"]

	costs = problem.get("costs", {})

	s = Optimize()

	modules = graphs.get_nodes(rules)

	atoms = get_atoms(rules)

	parent_graph = graphs.get_reversed(rules)

	ancestor_graph = graphs.get_closure(parent_graph)

	d = {} # dict: module -> (z3_int, z3_int)

	iff = Function('iff', BoolSort(), BoolSort(), BoolSort())
	s.add(iff(False, False) == True)
	s.add(iff(False, True)  == False)
	s.add(iff(True,  False) == False)
	s.add(iff(True,  True)  == True)

	# constraints

	for module in modules:
		a1 = Int(module + "_1")
		a2 = Int(module + "_2")
		d[module] = (a1, a2)
		s.add(a1 >= 0)
		s.add(a2 >= 0)
		if mode == "unique":
			s.add(a1 == (1 if module in system else 0))
		else:
			s.add(a1 == sum([(1 if x == module else 0) for x in system]))

	for a in atoms:
		pedigree = list(ancestor_graph[a]) + [a]
		p1 = [d[ancestor][0] for ancestor in pedigree]
		p2 = [d[ancestor][1] for ancestor in pedigree]
		if mode == "unique":
			s.add(iff(sum(p1) > 0, sum(p2) > 0))
		else:
			s.add(sum(p1) == sum(p2))

	cost_list = [d[module][1] * costs.get(module, 1) for module in modules]

	s.minimize(sum(cost_list))

	if s.check() == sat:
		m = s.model()
		counts = {c:m[d[c][1]].as_long() for c in modules}
		sol_cost_list = [counts[c] * costs.get(c, 1) for c in modules]
		solution = {
			"cost": sum(sol_cost_list)
		}
		if mode == "unique":
			solution["system"] = [c for c in modules if m[d[c][1]].as_long() > 0]
		else:
			solution["system"] = []
			for module in modules:
				units = m[d[module][1]].as_long()
				if units > 0:
					solution["system"] += [module] * units
		return solution
	else:
		print None

def print_solution(solution):
	if solution is None:
		print "unsat"
	else:
		lines = [
			"Solution:",
			"",
			json.dumps(solution["system"]),
			"",
			"Cost : %d" % solution["cost"]
		]
		for line in lines:
			print line

def write_solution(file, solution):
	with open(file, "w") as f:
		json.dump(solution, f, indent=4)

def load_problem(file):
	with open(file, "r") as f:
		content = json.load(f)
	return parser.parse(content)

def print_problem(problem):
	stats = [
		("System Modules", len(problem["system"])),
		("Unique Cost Elements", len(problem["costs"])),
		("Unique Rules", len(problem["rules"]))
	]
	for tup in stats:
		print "%-26s : %d" % tup
	print ""

def main():
	args = docopt.docopt(usage, version="Composability Optimizer (Copter) 0.1")
	problem = load_problem(args["<problem.json>"])
	mode = args.get("<m>", "unique")
	if mode not in ["unique", "count"]:
		raise Exception("Invalid mode: %s" % mode)
	solution = optimize(problem, mode)
	if args["--output"]:
		write_solution(args["--output"], solution)
	if not args["--quiet"]:
		print_problem(problem)
		print_solution(solution)

if __name__ == "__main__":
	main()
