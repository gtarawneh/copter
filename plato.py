import json
import itertools

def split_list(mylist, separators):
	sublists = []
	head = 0
	for ind, item in enumerate(mylist):
		if item in separators:
			sublists.append(mylist[head:ind])
			head = ind + 1
	remaining = mylist[head:]
	if remaining:
		sublists.append(remaining)
	return sublists

def parse_definitions(definitions):
	concept_defs = {}
	for line in definitions:
		words = line.split()
		try:
			k = words.index("=")
		except ValueError:
			raise Exception("Incorrect definition: %s" % line)
		parts = split_list(words, [".", "="])
		head, body = parts[0], parts[1:]
		head_name = head[0]
		result = {}
		result["quantifiers"] = len(head) - 1
		result["children"] = []
		head_quantifiers = head[1:]
		for concept in body:
			name, signals = concept[0], concept[1:]
			inds = [head_quantifiers.index(signal) for signal in signals]
			result["children"].append([name] + inds)
		concept_defs[head_name] = result
	return concept_defs

def get_circuit_signals(circuit):
	signals = set()
	for item in circuit:
		words = item.split()
		for signal in words[1:]:
			signals.add(signal)
	return list(signals)

def parse(plato_problem):
	definitions = plato_problem["concepts"]
	cost_template = plato_problem.get("costs", {})
	circuit = plato_problem["circuit"]
	signals = get_circuit_signals(circuit)
	concept_defs = parse_definitions(definitions)
	decomps, costs = {}, {}
	for parent in concept_defs.keys():
		cd = concept_defs[parent]
		child_count = cd["quantifiers"]
		for comb in itertools.permutations(signals, child_count):
			key = " ".join([parent] + list(comb))
			decomps[key] = []
			costs[key] = cost_template.get(parent, 1)
			for c in cd["children"]:
				name, inds = c[0], c[1:]
				args = [comb[ind] for ind in inds]
				val = " ".join([name] + args)
				decomps[key].append(val)
	problem = {
		"decompositions": decomps,
		"costs": costs,
		"circuit": circuit
	}
	return problem
