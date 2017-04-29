#!/usr/bin/env python

from pprint import pprint
from itertools import product
from itertools import combinations
from bitarray import bitarray
from json import dumps as jsons

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

def is_implication(preced, antec):
	return antec & preced == antec

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
	# mine atom causalities
	primitive_concepts = []
	rise_transitions = ["%s+" % signal for signal in encoding]
	fall_transitions = ["%s-" % signal for signal in encoding]
	all_transitions = rise_transitions + fall_transitions
	for target_trans in all_transitions:
		target = get_tran_svec(sg, nvars, target_trans)
		for literal_ind in range(nvars):
			literal_svec = get_literal_svec(5, literal_ind)
			if is_implication(literal_svec, target):
				literal = encoding[nvars-literal_ind-1]
				prim = "cause %s+ %s" % (literal, target_trans)
				primitive_concepts.append(prim)
			if is_implication(~literal_svec, target):
				literal = encoding[nvars-literal_ind-1]
				prim = "cause %s- %s" % (literal, target_trans)
				primitive_concepts.append(prim)
	# mine OR causality (or_cause_rrr, or_case_fff)
	or_cause_rrr_concepts = []
	or_cause_fff_concepts = []
	for comb in combinations(range(nvars), 2):
		literal1_svec = get_literal_svec(5, comb[0])
		literal2_svec = get_literal_svec(5, comb[1])
		for target_signal in encoding:
			target_rise = get_tran_svec(sg, nvars, "%s+" % target_signal) & rsvec
			target_fall = get_tran_svec(sg, nvars, "%s-" % target_signal) & rsvec
			comb_svec_or_rr = (literal1_svec | literal2_svec) & rsvec
			comb_svec_or_rf = (~literal1_svec | ~literal2_svec) & rsvec
			comb_svec_or_ff = (~literal1_svec | ~literal2_svec) & rsvec
			if is_implication(comb_svec_or_rr, target_rise):
				literal1 = encoding[nvars-comb[0]-1]
				literal2 = encoding[nvars-comb[1]-1]
				bogus = not comb_svec_or_rr.any()
				oc_concept = "or_cause_rrr %s %s %s%s" % \
					(literal1, literal2, target_signal, " (bogus)" if bogus else "")
				or_cause_rrr_concepts.append(oc_concept)
			if is_implication(comb_svec_or_rf, target_fall):
				literal1 = encoding[nvars-comb[0]-1]
				literal2 = encoding[nvars-comb[1]-1]
				bogus = not comb_svec_or_rf.any()
				if bogus:
					print "BOGUS"
				oc_concept = "or_cause_rfr %s %s %s%s" % \
					(literal1, literal2, target_signal, " (bogus)" if bogus else "")
				or_cause_rrr_concepts.append(oc_concept)
			if is_implication(comb_svec_or_ff, target_fall):
				literal1 = encoding[nvars-comb[0]-1]
				literal2 = encoding[nvars-comb[1]-1]
				bogus = not comb_svec_or_ff.any()
				oc_concept = "or_cause_fff %s %s %s%s" % \
					(literal1, literal2, target_signal, " (bogus)" if bogus else "")
				or_cause_fff_concepts.append(oc_concept)
	concepts = primitive_concepts + or_cause_fff_concepts + or_cause_rrr_concepts
	print jsons(concepts, indent=4)

if __name__ == "__main__":
	main()
