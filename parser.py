import itertools
import re

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
		head, body = parse_definition(line)
		head_name = head[0]
		result = {}
		result["quantifiers"] = len(head) - 1
		result["children"] = []
		head_quantifiers = head[1:]
		for module in body:
			name, signals = module[0], module[1:]
			inds = [head_quantifiers.index(signal) for signal in signals]
			result["children"].append([name] + inds)
			# add child to module_defs
			if name not in module_defs:
				module_defs[name] = {
					"children": [],
					"quantifiers": len(signals)
				}
		module_defs[head_name] = result
	return module_defs

def get_signals(system):
	signals = set()
	for item in system:
		words = item.split()
		for signal in words[1:]:
			signals.add(signal)
	return list(signals)

def parse(problem):
	preprocess_problem(problem)
	definitions = problem["rules"]
	cost_template = problem.get("costs", {})
	system = problem["system"]
	signals = get_signals(system)
	module_defs = parse_definitions(definitions)
	rules, costs = {}, {}
	cost_undef_mods = set() # modules with undefined costs
	for parent in module_defs.keys():
		cd = module_defs[parent]
		child_count = cd["quantifiers"]
		for comb in itertools.permutations(signals, child_count):
			key = " ".join([parent] + list(comb))
			costs[key] = cost_template.get(parent, 1)
			if parent not in cost_template:
				cost_undef_mods.add(parent)
			if cd["children"]:
				rules[key] = []
				for c in cd["children"]:
					name, inds = c[0], c[1:]
					args = [comb[ind] for ind in inds]
					val = " ".join([name] + args)
					rules[key].append(val)
	problem = {
		"rules": rules,
		"costs": costs,
		"system": system,
		"source": {
			"rules": definitions,
			"costs": cost_template,
			"cost_undef_mods": list(cost_undef_mods)
		}
	}
	return problem

def parse_definition(line):
	words = line.split()
	try:
		k = words.index("=")
	except ValueError:
		raise Exception("Incorrect definition: %s" % line)
	parts = split_list(words, [".", "="])
	head, body = parts[0], parts[1:]
	return head, body

def preprocess_problem(problem=None):
	meta_rules = problem["input-meta-rules"]
	gen1 = rule_transformer(meta_rules)
	gen1.next()
	# preprocess system
	problem["system"] = [gen1.send(mod) for mod in problem["system"]]
	# preprocess rules
	new_rules = []
	for line in problem["rules"]:
		head, body = parse_definition(line)
		head_str = " ".join(head)
		new_head_str = gen1.send(head_str)
		mod_strs = [" ".join(mod) for mod in body]
		new_mod_strs = [gen1.send(mod_str) for mod_str in mod_strs]
		new_body_str = " . ".join(new_mod_strs)
		new_rule = "%s = %s" % (new_head_str, new_body_str)
		new_rules.append(new_rule)
	problem["rules"] = new_rules

def rule_transformer(meta_rules):
	compiled_rules = {re.compile(k):v for k, v in meta_rules.iteritems()}
	result = None
	while True:
		module_str = yield result
		for key, value in meta_rules.iteritems():
			re_result = re.match(key, module_str)
			if re_result:
				result = value % re_result.groups()
				break
		else:
			result = module_str