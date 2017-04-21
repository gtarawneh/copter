#!/usr/bin/env python

from pprint import pprint

def load_sg(file):
	"""
	Load an SG file.
	Return a dictionary, mapping each transition to a list of (prev, next)
	state tuples, for example: 'a+': [('000', '100'), ('010', '110')].
	"""
	sg = {}
	with open(file, "r") as fid:
		lines = fid.read().splitlines()
	for line in lines:
		if line[0] not in ".#":
			prev_state, transition, next_state = line.split()
			prev_bits = prev_state.split("_")[1]
			next_bits = next_state.split("_")[1]
			sg[transition] = sg.get(transition, [])
			sg[transition].append((prev_bits, next_bits))
	return sg

def get_encoding(sg):
	"""
	Return the encoding of a state graph `sg` as a list of signals, for example
	['a', 'b', 'c'].
	"""
	encoding_dic = {}
	for transition, state_list in sg.iteritems():
		signal, polarity = transition[:-1], transition[-1]
		for state_tup in state_list:
			prev_bits, next_bits = state_tup
			bit_diff = [a!=b for (a,b) in zip(prev_bits, next_bits)]
			diff_inds = [ind for ind, bdiff in enumerate(bit_diff) if bdiff]
			if len(diff_inds) == 1:
				bit = diff_inds[0]
			else:
				raise Exception(
					"Transition %s causes multiple bit changes" % transition)
			if signal in encoding_dic:
				if bit != encoding_dic[signal]:
					raise Exception(
						"Inconsistent encoding of signal %s" % signal)
			else:
				encoding_dic[signal] = bit
	encoding_list = [None] * len(encoding_dic)
	for key, value in encoding_dic.iteritems():
		encoding_list[value] = key
	return encoding_list

def main():
	file = "examples/david_cell.sg"
	sg = load_sg(file)
	encoding = get_encoding(sg)
	pprint(sg)
	pprint(encoding)

if __name__ == "__main__":
	main()
