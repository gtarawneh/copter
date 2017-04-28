#!/usr/bin/env python

from pprint import pprint
from itertools import product
from bitarray import bitarray

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

def dnf_to_cnf(dnf_core, dnf_opt):
	# dnf_core = [
	# 	["x", "y", "t"],
	# 	["x", "w"]
	# ]
	# dnf_opt = [
	# 	["a", "b"],
	# 	["c", "d"],
	# 	["a"]
	# ]
	cnf_core = [list(set(item)) for item in product(*dnf_core)]
	cnf_opt = [list(set(item)) for item in product(*dnf_opt)]
	# cnf = product(cnf_core, cnf_opt)
	pprint(dnf_opt)
	pprint(list(product(*dnf_opt)))
	# for item in dnf_opt:
		# print item

def get_rsvec(sg, nvars):
	"""
	Calculate vector of reachable states.
	"""
	rstates = [trans[0] for trans_list in sg.values() \
		for trans in trans_list] # reachable states
	rsvec = bitarray(2**nvars) # reachable state vector
	rsvec.setall(0)
	for item in rstates:
		ind = int(item, 2)
		rsvec[ind] = 1
	return rsvec

def get_tran_svec(sg, nvars, transition):
	svec = bitarray(2**nvars) # reachable state vector
	svec.setall(0)
	for state, _ in sg[transition]:
		ind = int(state, 2)
		svec[ind] = 1
	return svec

def get_literal_svec(nvars, ind):
	svec = bitarray([(i>>ind)&1 for i in range(2**nvars)])
	return svec

def is_implication(antec, preced):
	return antec & preced == preced

def main():
	file = "examples/david_cell.sg"
	sg = load_sg(file)
	encoding = get_encoding(sg)
	nvars = len(encoding)
	rsvec = get_rsvec(sg, nvars)
	usvec = bitarray(rsvec)
	usvec.invert()
	# printing
	pprint(sg)
	print ""
	print "Encoding :", encoding
	print ""
	target_trans = "e-"
	plus_transitions = ["%s+" % signal for signal in encoding]
	minus_transitions = ["%s-" % signal for signal in encoding]
	all_transitions = plus_transitions + minus_transitions
	for target_trans in all_transitions:
		target = get_tran_svec(sg, nvars, target_trans)
		for literal_ind in range(nvars):
			literal = encoding[nvars-literal_ind-1]
			literal_svec = get_literal_svec(5, literal_ind)
			if is_implication(literal_svec, target):
				print "cause %5s+ %5s" % (literal, target_trans)
			if is_implication(~literal_svec, target):
				print "cause %5s- %5s" % (literal, target_trans)
	return
	# ustates = list(set(states) - set(rstates)) # unreachable states
	# ustates.remove("0" * nvars)
	# print ustates
	get_expr = lambda code : \
		[encoding[ind] for ind in range(nvars) if code[ind] == "1"]
	dnf_opt = map(get_expr, ustates)
	dnf_core = [
		["r1"]
	]
	# dnf_to_cnf(dnf_core, dnf_opt)


if __name__ == "__main__":
	main()
