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
	module_defs = {}
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
		for module in body:
			name, signals = module[0], module[1:]
			inds = [head_quantifiers.index(signal) for signal in signals]
			result["children"].append([name] + inds)
		module_defs[head_name] = result
	return module_defs

def get_signals(system):
	signals = set()
	for item in system:
		words = item.split()
		for signal in words[1:]:
			signals.add(signal)
	return list(signals)

def parse(plato_problem):
	definitions = plato_problem["rules"]
	cost_template = plato_problem.get("costs", {})
	system = plato_problem["system"]
	signals = get_signals(system)
	module_defs = parse_definitions(definitions)
	rules, costs = {}, {}
	for parent in module_defs.keys():
		cd = module_defs[parent]
		child_count = cd["quantifiers"]
		for comb in itertools.permutations(signals, child_count):
			key = " ".join([parent] + list(comb))
			rules[key] = []
			costs[key] = cost_template.get(parent, 1)
			for c in cd["children"]:
				name, inds = c[0], c[1:]
				args = [comb[ind] for ind in inds]
				val = " ".join([name] + args)
				rules[key].append(val)
	problem = {
		"rules": rules,
		"costs": costs,
		"system": system
	}
	return problem
