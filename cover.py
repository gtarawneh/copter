#!/usr/bin/env python

from graphs import *
from itertools import product

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
	}
	decomp_spec = set(["B", "C"])
	rgraph = get_reversed(graph)
	sources = get_sources(graph)
	sinks = get_sinks(graph)
	lists = {}
	def visit_fun(node):
		if node in sinks:
			lists[node] = [(set(node), costs[node])]
			if node not in decomp_spec:
				# add epsilon as a valid composition
				lists[node] += [(set(), 0)]
		else:
			# Enumerate compositions as cartesian product of child
			# compositions
			child_imps = [lists[n] for n in graph.get(node, [])]
			prods = product(*child_imps)
			res = map(combine_pairs, prods)
			res += [(set(node), costs[node])]
			lists[node] = res
	traverse_dp(graph, visit_fun)
	from pprint import pprint
	pprint(lists, width=40)

def combine_pairs(tup):
	combined_children = tup[0][0] | tup[1][0]
	combined_cost = tup[0][1] + tup[1][1]
	return (combined_children, combined_cost)

if __name__ == "__main__":
	main()
