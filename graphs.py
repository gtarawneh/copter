#!/usr/bin/env python

def get_nodes(graph):
	"""
	Return list of nodes in directed graph `graph`

	`graph` is a dict: node -> destination node list.
	"""
	p1 = [item for sublist in graph.values() for item in sublist]
	p2 = graph.keys()
	nodes = set(p1).union(set(p2))
	return nodes

def get_closure(graph):
	"""
	Return transitive closure of directed graph `graph`.

	`graph` is a dict: node -> destination node list.
	"""
	closure = {}
	nodes = get_nodes(graph)
	for n in nodes:
		# bfs
		to_visit = [n]
		visited = set([n])
		while to_visit:
			next_to_visit = set()
			for node in to_visit:
				for child in graph.get(node, []):
					next_to_visit.add(child)
			next_to_visit.difference(visited)
			to_visit = next_to_visit
			visited = visited.union(next_to_visit)
		reachable = visited.difference([n])
		if reachable:
			closure[n] = reachable
	return closure

def get_reversed(graph):
	"""
	Return a directed graph equivalent to `graph` but with edge directions
	reversed.
	"""
	p1 = [item for sublist in graph.values() for item in sublist]
	graph2 = {n:set() for n in p1}
	for parent, children in graph.iteritems():
		for child in children:
			graph2[child].add(parent)
	return graph2

def print_graph(graph):
	print "{"
	for node, children in graph.iteritems():
		print "\t'%s': %s" % (node, list(children))
	print "}"

def main():
	graph1 = {
		"E": ["C", "D"],
		"F": ["G", "C"],
		"C": ["A", "B"],
	}
	print "closure  :", get_closure(graph1)
	print "reversed :", get_reversed(graph1)
	print "closure of reversed :", get_closure(get_reversed(graph1))

if __name__ == "__main__":
	main()
