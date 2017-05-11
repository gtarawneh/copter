#!/usr/bin/env python

from itertools import combinations
from itertools import product
from bitarray  import bitarray
from functools import partial
from operator  import or_
from graphs    import *

def get_example2():
	graph = {
		# "E": ["A", "B"],
		"F": ["A", "C"],
		"G": ["C", "D"],
		"H": ["B", "G"],
		"I": ["F", "G"],
	}
	costs = {
		"A": 10,
		"B": 10,
		"C": 10,
		"D": 10,
		"E": 5,
		"F": 5,
		"G": 5,
		"H": 1,
		"I": 1,
		"X": 1
	}
	spec = set(["B", "C"])
	return graph, costs, spec

def encode(node_list, spec):
	"""
	Convert a node list to bit array format.
	"""
	present = lambda node : 1 if node in spec else 0
	arr = map(present, node_list)
	return bitarray(arr)

def decode(node_list, barr):
	"""
	Convert a node list from bitarray to list format.
	"""
	spec = [item[0] for item in zip(node_list, barr) if item[1]]
	spec.sort()
	return spec

def get_sorted_nodelist(graph, costs):
	"""
	Return a list of nodes, sorted by cost.
	"""
	nodes = list(get_nodes(graph))
	costFun = lambda node : costs.get(node, 0)
	nodes.sort(key=costFun)
	return nodes

def main():
	graph, costs, spec = get_example2()
	solve(graph, costs, spec)

def solve(graph, costs, spec):
	rgraph = get_reversed(graph)
	sources = get_sources(graph)
	closure = get_closure(graph)
	# TODO: spec must be a list of primitives (i.e. sinks)
	# -- Refactor code below
	spec =  list(set().union(*map(set, [closure.get(item, [item]) for item in spec])))
	sinks = get_sinks(graph)
	dspecs = {} # decomposed node spec
	node_list = get_sorted_nodelist(graph, costs)
	encode_p = partial(encode, node_list)
	decode_p = partial(decode, node_list)
	build_dspecs_p = partial(build_dspecs, sinks, dspecs, spec, graph, encode_p)
	for key, val in graph.items():
		# print "%-16s %s" % (key, map(str, val))
		pass
	traverse_dp(graph, build_dspecs_p)
	# print_dspecs(dspecs, node_list)
	valid_dspec = reduce(or_, [dspecs[node] for node in spec])
	valid_dspec_hash = get_barr_hash(valid_dspec)
	n = len(node_list)
	ncombs = 0
	best_cost = sum(costs.values())
	best_cost = 999
	for k in range(1, 2):
		print "k =", k
		for comb in combinations(node_list, k):
			ncombs += 1
			# print map(str, comb)
			cost = sum([costs[item] for item in comb])
			# if cost < best_cost:
			if True:
				dspec_barr_list = [dspecs[node] for node in comb]
				dspec_barr = reduce(or_, dspec_barr_list)
				if get_barr_hash(dspec_barr) == valid_dspec_hash:
					print map(str, comb), "=", cost
					best_cost = cost
	print "Examined solutions : %d" % ncombs

def get_barr_hash(barr):
	"""
	Compute hash of bitarray.
	"""
	return hash(barr.tobytes())

def build_dspecs(sinks, dspecs, spec, graph, encode_p, node):
	"""
	Build decomposed (flattened spec) using dynamic programming.
	"""
	if node in sinks:
		dspecs[node] = encode_p([node] if node in spec else [])
	else:
		child_flats = [dspecs[child] for child in graph.get(node, [])]
		dspecs[node] = reduce(or_, child_flats)

def print_dspecs(dspecs, node_list):
	print "Decomposed Spec:\n"
	for node, flat in dspecs.iteritems():
		print node, "=", map(str, decode(node_list, flat))
	print ""

if __name__ == "__main__":
	main()

def get_example1():
	graph = {
		"D1": ["A1", "B1", "C1"],
		"D2": ["A2", "B2", "C2"],
		"E": ["D1", "D2"]
	}
	costs = {
		"A1": 10,
		"B1": 10,
		"C1": 10,
		"D1": 10,
		"A2": 10,
		"B2": 10,
		"C2": 10,
		"D2": 10,
		"E": 10,
	}
	spec = set(["A1", "B1", "C1", "A2", "B2", "C2"])
	return graph, costs, spec