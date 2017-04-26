#!/usr/bin/env python

def traverse_dp(graph, visit_fun):
	"""
	Same as traverse_bf but visits a node only once all its destinations have been
	visited.
	"""
	initials = get_sources(graph)
	nodes = get_nodes(graph)
	visited = set(initials)
	remaining = set(nodes)
	while remaining:
		just_visited = set()
		for node in remaining:
			if set(graph.get(node, [])).issubset(visited):
				visit_fun(node)
				just_visited.add(node)
		remaining -= just_visited
		visited |= just_visited

def traverse_bf(graph, initials, visit_fun):
	"""
	Perform a breadth-first traversal of `graph`, starting from a list of
	nodes `initial` and applying a function `visit_fun` to each visited node.
	"""
	visited = set()
	current = set(initials)
	while current:
		visited |= current
		to_visit = set()
		for node in current:
			visit_fun(node)
			to_visit |= set(graph.get(node, []))
		to_visit -= visited
		current = to_visit

def get_sources(graph):
	"""
	Return list of nodes with no incoming edges.
	"""
	nodes = get_nodes(graph)
	vals = map(set, graph.values())
	destinations = set().union(*vals)
	sources = [n for n in nodes if n not in destinations]
	return sources

def get_sinks(graph):
	"""
	Return list of nodes with no outgoing edges
	"""
	nodes = get_nodes(graph)
	sinks = [n for n in nodes if n not in graph.keys()]
	return sinks

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
