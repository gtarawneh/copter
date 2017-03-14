#!/usr/bin/env python

from z3 import *
from datetime import datetime
import graphs


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

def optimize_circuit(decompositions, circuit):

	print datetime.now()

	print ""

	s = Optimize()

	concepts = graphs.get_nodes(decompositions)

	comp_encoding = list(concepts)
	# comp_encoding = ["F", "E", "G", "C", "D", "B", "A"] # complete encoding

	atoms = get_atoms(decompositions)
	atom_encoding = list(atoms)

	n = len(comp_encoding)
	m = len(atom_encoding)

	atom_decompositions = get_atom_decompositions(decompositions)


	parent_graph = graphs.get_reversed(decompositions)

	ancestor_graph = graphs.get_closure(parent_graph)

	cvec1 = BitVec('cvec1', n) # comp encoding bit vector
	avec1 = BitVec('avec1', m) # atom encoding bit vector

	cvec2 = BitVec('cvec2', n) # comp encoding bit vector

	# adding decomposition constraints

	print "atom_encoding :", atom_encoding
	print "comp_encoding :", comp_encoding

	def count_bits(b):
		# from:
		# http://stackoverflow.com/questions/39299015/sum-of-all-the-bits-in-a-bit-vector-of-z3
		n = b.size() # operand bits
		m = n - 1 # result bits, n-1 for simplicity, could do ceil(log(n, 2))
		bits = [Extract(i, i, b) for i in range(n)]
		bvs = [Concat(BitVecVal(0, m), b) for b in bits]
		nb = reduce(lambda a, b: a + b, bvs)
		return nb

	def add_type1_constraint(cvec, avec, cmask_bv, amask_bv):
		# TODO: more efficient bit extraction, see:
		# http://stackoverflow.com/questions/32594748/z3py-what-is-the-most-efficient-way-of-constraining-a-bit-in-bitvec
		# constraint: if concept exists then its atoms exist
		concept_present = cvec & cmask_bv == cmask_bv
		all_atoms_present = avec & amask_bv == amask_bv
		constraint = Implies(concept_present, all_atoms_present)
		s.add(constraint)

	def add_type2_constraint(cvec, avec, amask_bv, cmask_bv):
		# constraint: if atoms exist then at least one ancestor exists
		atom_present = avec & amask_bv == amask_bv
		one_ancestor_present = (cvec & cmask_bv) != 0
		constraint = Implies(atom_present, one_ancestor_present)
		s.add(constraint)

	print "\nConstraints:\n"

	# add type 1 constraints:
	for ind, concept in enumerate(comp_encoding):
		cmask_bv = BitVecVal(1 << ind, n)
		atoms = atom_decompositions[concept]
		atom_blist = get_blist(atom_encoding, atoms)
		amask_bv = get_bv(atom_blist)
		add_type1_constraint(cvec1, avec1, cmask_bv, amask_bv)
		add_type1_constraint(cvec2, avec1, cmask_bv, amask_bv)
		print "Concept [%s] (cmask = %2s) |-> atoms %s (amask = %2s)" % \
			(concept, cmask_bv, repr(atom_blist), amask_bv)

	# add type 2 constraints:
	for ind, atom in enumerate(atom_encoding):
		amask_bv = BitVecVal(1 << ind, m)
		# determine all concepts that contain atom (containers)
		containers = ancestor_graph[atom]
		containers.add(atom)
		container_blist = get_blist(comp_encoding, containers)
		container_mask_bv = get_bv(container_blist)
		add_type2_constraint(cvec1, avec1, amask_bv, container_mask_bv)
		add_type2_constraint(cvec2, avec1, amask_bv, container_mask_bv)
		print "Atom [%s] (amask = %2s)    |-> container from %s (container_mask = %2s)" % \
			(atom, amask_bv, repr(container_blist), container_mask_bv)

	s.add(avec1 == avec1) # circuit decompositions are equivalent

	circuit_blist = get_blist(comp_encoding, circuit)
	circuit_bv = get_bv(circuit_blist)

	s.add(cvec1 == circuit_bv)

	# s.add(count_bits(cvec2) < count_bits(cvec1)) # require a better circuit

	s.minimize(count_bits(cvec2))

	print ""

	if s.check() == sat:

		m = s.model()

		circuit1 = get_circuit(comp_encoding, m[cvec1].as_long())
		circuit2 = get_circuit(comp_encoding, m[cvec2].as_long())

		cost1 = m.evaluate(count_bits(cvec1))
		cost2 = m.evaluate(count_bits(cvec2))

		print "Input Circuit  (cost = %3s) : %s" % (cost1, circuit1)
		print "Output Circuit (cost = %3s) : %s" % (cost2, circuit2)

		print "\nBit-vector encodings:\n"

		print "cvec1 = %6s, avec1 = %6s" % (m[cvec1], m[avec1])
		print "cvec2 = %6s, avec1 = %6s" % (m[cvec2], m[avec1])
	else:
		print "unsat"

def main():

	decompositions = {
		"E": ["C", "D"],
		"F": ["G", "C"],
		"C": ["A", "B"],
	}

	costs = {
		"A": 4,
		"B": 4,
		"C": 2,
		"D": 2,
		"E": 1,
		"F": 1,
		"G": 2,
	}

	circuit = ["A", "G", "D", "B"]

	optimize_circuit(decompositions, circuit)

if __name__ == "__main__":
	main()
