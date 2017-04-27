#!/usr/bin/env python

from graphs import *
from itertools import product
from functools import partial

def main():
	graph = {
		"E": ["A", "B"],
		"F": ["A", "C"],
		"G": ["C", "D"],
		"H": ["B", "G"],
		"I": ["F", "G"]
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
		"R": 0,
	}
	spec = set(["B", "C"])
	add_root(graph)
	rgraph = get_reversed(graph)
	sources = get_sources(graph)
	sinks = get_sinks(graph)
	comps = {} # node compositions and costs
	dspecs = {} # decomposed node spec
	build_dspecs_p = partial(build_dspecs, sinks, dspecs, spec, graph)
	build_comp_p = partial(build_comps, comps, sinks, graph, costs, spec)
	traverse_dp(graph, build_dspecs_p)
	traverse_dp(graph, build_comp_p)
	print_dspecs(dspecs)
	print_comps(comps)

def add_root(graph):
	nodes = get_nodes(graph)
	graph["R"] = list(nodes)

def build_comps(comps, sinks, graph, costs, spec, node):
	if node in sinks:
		comps[node] = [(set(node), costs[node])]
		if node not in spec:
			# add epsilon as a valid composition
			comps[node] += [(set(), 0)]
	else:
		# Enumerate compositions as cartesian product of child
		# compositions
		child_imps = [comps[n] for n in graph.get(node, [])]
		prods = product(*child_imps)
		res = map(combine_pairs, prods)
		res += [(set(node), costs[node])]
		comps[node] = res
		if node == "R":
			print child_imps
			import sys
			sys.exit(1)
			print "==", list(res)

def build_dspecs(sinks, dspecs, spec, graph, node):
	if node in sinks:
		dspecs[node] = set([node]) if node in spec else set()
	else:
		child_flats = [dspecs[child] for child in graph.get(node, [])]
		dspecs[node] = set().union(*child_flats)

def print_comps(comps):
	print "Node compositions:\n"
	for node, comps in comps.iteritems():
		print node, ":"
		for comp in comps:
			print "\t", list(comp[0]), "=", comp[1]
	print ""

def print_dspecs(dspecs):
	print "Decomposed Spec:\n"
	for node, flat in dspecs.iteritems():
		print node, "=", list(flat)
	print ""

def combine_pairs(tup):
	combined_children = tup[0][0] | tup[1][0]
	combined_cost = tup[0][1] + tup[1][1]
	return (combined_children, combined_cost)

if __name__ == "__main__":
	main()
