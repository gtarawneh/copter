#!/usr/bin/env python

from graphs import *
from bitarray import bitarray
from itertools import product
from itertools import combinations
from functools import partial
import operator

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
	present = lambda node : 1 if node in spec else 0
	arr = [present(n) for n in node_list]
	return bitarray(arr)

def decode(node_list, barr):
	spec = [item[0] for item in zip(node_list, barr) if item[1]]
	spec.sort()
	return spec

def calculate_cost(cost_list, barr):
	item_costs = [cost_list[ind] for ind, val in enumerate(barr) if val]
	return sum(item_costs)

def main():
	graph, costs, spec = get_example2()
	rgraph = get_reversed(graph)
	sources = get_sources(graph)
	sinks = get_sinks(graph)
	# comps = {} # node compositions and costs
	dspecs = {} # decomposed node spec
	node_list = list(get_nodes(graph))
	cost_list = [costs[n] for n in node_list]
	# code = encode(node_list, spec)
	encode_p = partial(encode, node_list)
	decode_p = partial(decode, node_list)
	build_dspecs_p = partial(build_dspecs, sinks, dspecs, spec, graph, encode_p)
	# build_comp_p = partial(build_comps, comps, sinks, graph, costs, spec, encode_p)
	traverse_dp(graph, build_dspecs_p)
	# traverse_dp(graph, build_comp_p)
	# print_dspecs(dspecs, node_list)
	# print_comps(comps, decode_p)
	# test combs
	get_dspec = lambda node : dspecs[node]
	valid_dspec = reduce(operator.or_, map(get_dspec, spec))
	valid_dspec_hash = get_barr_hash(valid_dspec)
	n = len(node_list)
	c1 = 0
	c2 = 0
	for k in range(1, n):
		for comb in combinations(node_list, k):
			c1 += 1
			cost = sum([costs[item] for item in comb])
			dspec_barr_list = map(get_dspec, list(comb))
			dspec_barr = reduce(operator.or_, dspec_barr_list)
			if get_barr_hash(dspec_barr) == valid_dspec_hash:
				print list(comb), "=", cost
				c2 += 1
	print c2, c1

	return
	sols = [(item, calculate_cost(cost_list, item)) for item in comps["root"]]
	sols.sort(key=lambda sol : sol[1])
	for item in sols:
		print decode_p(item[0]), item[1]

def combine_barr_list(arr_list):
	return reduce(operator.or_, arr_list)

def build_comps(comps, sinks, graph, costs, spec, encode_p, node):
	if node in sinks:
		comps[node] = [encode_p([node])] + \
			([encode_p([])] if node not in spec else [])
	else:
		# Enumerate compositions as cartesian product of child compositions
		child_imps = [comps[n] for n in graph.get(node, [])]
		prods = list(product(*child_imps))
		prods.append([encode_p(node)]) # add node itself as a valid composition
		res = map(combine_barr_list, prods)
		comps[node] = get_unique_barr_list(res)

def get_barr_hash(barr):
	return hash(barr.tobytes())

def get_unique_barr_list(barr_list):
	dic = {get_barr_hash(barr):barr for barr in barr_list}
	barr_list_uniq = [val for _, val in dic.iteritems()]
	return barr_list_uniq

def build_dspecs(sinks, dspecs, spec, graph, encode_p, node):
	if node in sinks:
		dspecs[node] = encode_p([node] if node in spec else [])
	else:
		child_flats = [dspecs[child] for child in graph.get(node, [])]
		dspecs[node] = reduce(operator.or_, child_flats)

def print_comps(comps, decode_p):
	print "Node compositions:\n"
	for node, comps in comps.iteritems():
		print node, ":"
		for comp in comps:
			print "\t", decode_p(comp)
	print ""

def print_dspecs(dspecs, node_list):
	print "Decomposed Spec:\n"
	for node, flat in dspecs.iteritems():
		print node, "=", decode(node_list, flat)
	print ""

if __name__ == "__main__":
	main()
