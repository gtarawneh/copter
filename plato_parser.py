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

def parse_concept_clause(str):
	pass

def split_list(L, separators):
	sublists = []
	head = 0
	for ind, item in enumerate(L):
		if item in separators:
			sublists.append(L[head:ind])
			head = ind + 1
	remaining = L[head:]
	if remaining:
		sublists.append(remaining)
	return sublists

def main():
	definitions = [
		"cElement a b c = buffer a c . buffer b c",
		"handshake b c = buffer b c . inverter c b"
	]
	concept_defs = parse_definitions(definitions)
	import json
	print json.dumps(concept_defs, indent=4)

if __name__ == "__main__":
	main()
