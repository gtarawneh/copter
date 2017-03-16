#!/usr/bin/env python

import graphs
import json
import plato
from z3 import *
from docopt import docopt

usage = """Composability Optimizer (Copter)

Usage:
  copter.py [--plato] [--mode=<m>] [--output=<file>] [--quiet] <problem.json>
  copter.py --version

Options:
  -p --plato          Load problem file in Plato format.
  -m --mode=<m>       Choose optimization mode (unique/count) [default: unique].
  -o --output=<file>  Write solution to json file.
  -q --quiet          Suppress output.

"""

def get_circuit_blist(atom_decompositions, bit_encoding, circuit):
	"""
	Return a bit list indicating whether each atom in `bit_encoding` is
	present in the circuit.

	`circuit` is a list of concepts.
	"""
	circuit_atoms = set()
	for c in circuit:
		circuit_atoms = circuit_atoms.union(atom_decompositions.get(c, []))
	return get_blist(bit_encoding, atoms)

def get_blist(bit_encoding, atoms):
	"""
	Return a bit list indicating whether each atom in `bit_encoding` is
	present in `atoms`
	"""
	return [(1 if b in atoms else 0) for b in bit_encoding]

def get_atom_decompositions(decompositions):
	"""
	Return a dict: concept -> list of constituent atoms.
	"""

	atoms = get_atoms(decompositions)

	def get_concept_atoms(root):
		"""
		Return a list of all atoms in the subtree `root`.
		"""
		to_visit = [root]
		visited = set([root])
		while to_visit:
			next_to_visit = set()
			for node in to_visit:
				for child in decompositions.get(node, []):
					next_to_visit.add(child)
			next_to_visit.difference(visited)
			to_visit = next_to_visit
			visited = visited.union(next_to_visit)
		return list(visited.intersection(atoms))

	concepts = graphs.get_nodes(decompositions)
	atom_decompositions = {c:get_concept_atoms(c) for c in concepts}
	return atom_decompositions

def get_atoms(decompositions):
	"""
	Return atom concepts.

	Atoms are concepts that cannot be decomposed.
	"""
	concepts = graphs.get_nodes(decompositions)
	non_atoms = decompositions.keys()
	atoms = set(concepts).difference(non_atoms)
	return list(atoms)

def get_bv(blist):
	"""
	Return a z3 BitVecVal representation of blist.
	"""
	m = len(blist)
	amask = 0 # atom mask
	for ind2, bit in enumerate(blist):
		amask += bit << ind2
	return BitVecVal(amask, m)

def get_circuit(comp_encoding, cvec):
	n = len(comp_encoding)
	circuit = []
	for ind, concept in enumerate(comp_encoding):
		mask = 1 << ind
		if cvec & mask:
			circuit.append(concept)
	return circuit

def optimize(problem, mode="unique"):

	# in "unique" mode : a . a == a
	# in "count" mode  : a . a != a

	decompositions, circuit = problem["decompositions"], problem["circuit"]

	costs = problem.get("costs", {})

	s = Optimize()

	concepts = graphs.get_nodes(decompositions)

	atoms = get_atoms(decompositions)

	atom_decompositions = get_atom_decompositions(decompositions)

	parent_graph = graphs.get_reversed(decompositions)

	ancestor_graph = graphs.get_closure(parent_graph)

	d = {} # dict: concept -> (z3_int, z3_int)

	# constraints

	for concept in concepts:
		a1 = Int(concept + "_1")
		a2 = Int(concept + "_2")
		d[concept] = (a1, a2)
		s.add(a1 >= 0)
		s.add(a2 >= 0)
		if mode == "unique":
			s.add(a1 == (1 if concept in circuit else 0))
		else:
			s.add(a1 == sum([(1 if x == concept else 0) for x in circuit]))

	for a in atoms:
		pedigree = list(ancestor_graph[a]) + [a]
		p1 = [d[ancestor][0] for ancestor in pedigree]
		p2 = [d[ancestor][1] for ancestor in pedigree]
		if mode == "unique":
			s.add(Implies(sum(p1) > 0, sum(p2) > 0))
			s.add(Implies(sum(p2) > 0, sum(p1) > 0))
		else:
			s.add(sum(p1) == sum(p2))

	cost_list = [d[concept][1] * costs.get(concept, 1) for concept in concepts]

	s.minimize(sum(cost_list))

	if s.check() == sat:
		m = s.model()
		counts = {c:m[d[c][1]].as_long() for c in concepts}
		sol_cost_list = [counts[c] * costs.get(c, 1) for c in concepts]
		solution = {
			"cost": sum(sol_cost_list)
		}
		if mode == "unique":
			solution["circuit"] = [c for c in concepts if m[d[c][1]].as_long() > 0]
		else:
			solution["circuit"] = []
			for concept in concepts:
				units = m[d[concept][1]].as_long()
				if units > 0:
					solution["circuit"] += [concept] * units
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
			json.dumps(solution["circuit"]),
			"",
			"Cost : %d" % solution["cost"]
		]
		for line in lines:
			print line

def write_solution(file, solution):
	with open(file, "w") as f:
		json.dump(solution, f, indent=4)

def load_problem_file(file):
	with open(file, "r") as f:
		problem = json.load(f)
	return problem

def print_problem(problem):
	stats = [
		("Circuit Elements", len(problem["circuit"])),
		("Unique Cost Elements", len(problem["costs"])),
		("Unique Decompositions", len(problem["decompositions"]))
	]
	for tup in stats:
		print "%-26s : %d" % tup
	print ""

def main():
	args = docopt(usage, version="Composability Optimizer (Copter) 0.1")
	content = load_problem_file(args["<problem.json>"])
	problem = plato.parse(content) if args["--plato"] else content
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
