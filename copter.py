#!/usr/bin/env python

import graphs
import json
import parser
import docopt
import traceback
from z3 import *
from time import time

usage = """Composability Optimizer (Copter)

Usage:
  copter.py [--mode=<m>] [--output=<file>] [--quiet|--print]
            [--costs=<list>] <problem.json>...
  copter.py --version

Options:
  -m --mode=<m>       Choose optimization mode [default: unique].
  -o --output=<file>  Write solution to json file.
  -c --costs=<list>   Override costs (<list> is mod1:cost1,mod2:cost2 ...).
  -p --print          Print problem (rules, costs and system).
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

	solver = Optimize()

	modules = graphs.get_nodes(rules)

	atoms = get_atoms(rules)

	parent_graph = graphs.get_reversed(rules)

	ancestor_graph = graphs.get_closure(parent_graph)

	d = {} # dict: module -> (z3_int, z3_int)

	# note: iff is no longer needed but removing it causes a segmentation
	# fault for some reason (TODO: debug)
	iff = Function('iff', BoolSort(), BoolSort(), BoolSort())
	solver.add(iff(False, False) == True)
	solver.add(iff(False, True)  == False)
	solver.add(iff(True,  False) == False)
	solver.add(iff(True,  True)  == True)

	# constraints

	for module in modules:
		mod = Int(module) # Z3 object
		d[module] = mod
		if mode in ["unique", "inclusive"]:
			constraint = Or(mod == 0, mod == 1)
		elif mode == "count":
			constraint = mod >= 0

		solver.add(constraint)

	in_system = lambda module : 1 if module in system else 0
	count_inst = lambda module : sum([1 if x == module else 0 for x in system])

	for a in atoms:
		pedigree = list(ancestor_graph[a]) + [a]
		if mode in ["unique", "inclusive"]:
			p1 = [in_system(ancestor) for ancestor in pedigree]
		else:
			p1 = [count_inst(ancestor) for ancestor in pedigree]
		p2 = [d[ancestor] for ancestor in pedigree] # Z3 object
		s1 = sum(p1)
		s2 = sum(p2) # Z3 object
		if mode == "unique":
			solver.add((s2>0) if (s1>0) else (s2==0))
		elif mode == "inclusive":
			if s1>0:
				solver.add(s2>0)
		elif mode == "count":
			solver.add(s1 == s2)

	cost_list = [d[module] * costs.get(module, 1) for module in modules]

	start_solve = time()

	solver.minimize(sum(cost_list))

	end_solve = time()

	if solver.check() == sat:
		m = solver.model()
		counts = {c:m[d[c]].as_long() for c in modules}
		sol_cost_list = [counts[c] * costs.get(c, 1) for c in modules]
		solution = {
			"cost": sum(sol_cost_list),
			"solve_time": (end_solve - start_solve).real
		}
		if mode == "unique":
			solution["system"] = [c for c in modules if m[d[c]].as_long() > 0]
		else:
			solution["system"] = []
			for module in modules:
				units = m[d[module]].as_long()
				if units > 0:
					solution["system"] += [module] * units
		return solution
	else:
		print None

def print_solution(solution):
	print "Z3 Time: %1.2f sec"% solution["solve_time"]
	print ""
	if solution is None:
		print "unsat"
	else:
		lines = [
			"Solution (cost = %d):" % solution["cost"],
			"",
			" . ".join(solution["system"]),
		]
		for line in lines:
			print line

def write_solution(file, solution):
	with open(file, "w") as f:
		json.dump(solution, f, indent=4)

def load_problem(files, override_costs):
	"""
	Load problem by concatenating `rules`, `costs` and `system` entries in a
	list of files.

	If conflicting `costs` entries are present then those in later files
	take priority.

	`override_costs` is a string in the form 'mod1:cost1,mod2:cost2...'].
	Cost definitions in `override_costs` take precedence over those in files.
	"""
	all_content = {
		"rules" : [],
		"costs": {},
		"system": [],
		"input-meta-rules": {}
	}
	# load file content
	for file in files:
		try:
			with open(file, "r") as f:
				content = json.load(f)
		except ValueError as e:
			print "Could not load file %s\n" % file
			print e
			return None
		if "rules" in content:
			all_content["rules"] += content["rules"]
		if "system" in content:
			system = content["system"]
			if type(system) is not list:
				# Assume system is in string format and convert it to a list
				system = [module.strip() for module in system.split(".")]
			all_content["system"] += system
		if "costs" in content:
			for module, cost in content["costs"].iteritems():
				all_content["costs"][module] = cost
		if "input-meta-rules" in content:
			for module, cost in content["input-meta-rules"].iteritems():
				all_content["input-meta-rules"][module] = cost
	# process cost overrides
	try:
		if override_costs:
			for item in override_costs.split(","):
				module, cost_str = item.split(":")
				all_content["costs"][module] = int(cost_str)
	except ValueError as e:
		print "Invalid --costs argument, correct form is --costs=mod1:cost1,mod2:cost,...\n"
		raise(e)
	return parser.parse(all_content)

def print_problem(problem):
	print "Rules:"
	for r in problem["source"]["rules"]:
		parts = r.split("=")
		print "    - %-24s = %s" % (parts[0], ". ".join(parts[1:]))
	print "\nCosts:"
	for module, cost in problem["source"]["costs"].iteritems():
		print "    - %-24s = %d" % (module, cost)
	for module in problem["source"]["cost_undef_mods"]:
		print "    - %-24s = 1   (default cost)" % module
	print "\nSystem:"
	for module in problem["system"]:
		print "    - %-24s" % module
	print ""

def print_problem_stats(problem):
	stats = [
		("System Modules", len(problem["system"])),
		("Defined Costs", len(problem["source"]["costs"])),
		("Defined Rules", len(problem["source"]["rules"])),
		("Expanded Costs", len(problem["costs"])),
		("Expanded Rules", len(problem["rules"]))
	]
	print "Problem Statistics:"
	for tup in stats:
		print "    - %-24s : %d" % tup
	print ""

def main():
	args = docopt.docopt(usage, version="Composability Optimizer (Copter) 0.1")
	try:
		problem = load_problem(args["<problem.json>"], args["--costs"])
	except Exception as e:
		print "Encountered an error while loading problem\n"
		tb = traceback.format_exc()
		print tb
		sys.exit(1)
	if problem:
		mode = args["--mode"]
		if mode not in ["unique", "count", "inclusive"]:
			raise Exception("Invalid mode: %s" % mode)
		if args["--print"]:
			print_problem(problem)
		solution = optimize(problem, mode)
		if args["--output"]:
			write_solution(args["--output"], solution)
		if not args["--quiet"]:
			print_problem_stats(problem)
			print_solution(solution)

if __name__ == "__main__":
	main()
