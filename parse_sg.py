#!/usr/bin/env python

from collections import namedtuple
from itertools import product
from itertools import combinations
from itertools import permutations
from itertools import starmap
from bitarray import bitarray
from pprint import pprint
from json import dumps as jsons

Transition = namedtuple("Transition", "signal polarity")
Level = namedtuple("Level", "signal level")
SG = namedtuple("SG", "transitions encoding")

get_tran_str = lambda transition : transition.signal + transition.polarity
get_level_str = lambda level : level.signal + level.level
get_sg_tran = lambda sg, transition : sg.transitions[get_tran_str(transition)]

def print_stg(sg):
	print "Transitions:\n"
	for key, val in sg.transitions.iteritems():
		print "%s : %s" % (key, val)
	print "\nEncoding: %s\n" % sg.encoding

def load_sg(file):
	"""
	Load an SG file.
	"""
	# load transitions
	transitions = {}
	with open(file, "r") as fid:
		lines = fid.read().splitlines()
	for line in lines:
		if line[0] not in ".#":
			prev_state, transition, next_state = line.split()
			prev_bits = prev_state.split("_")[1]
			next_bits = next_state.split("_")[1]
			transitions[transition] = transitions.get(transition, [])
			transitions[transition].append((prev_bits, next_bits))
	# determine encoding
	encoding_dic = {}
	for transition, state_list in transitions.iteritems():
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
	return SG(transitions, encoding_list)

def get_reachable_barr(sg):
	"""
	Calculate bit array of reachable states.
	"""
	nvars = len(sg.encoding)
	rstates = [trans[0] for trans_list in sg.transitions.values() \
		for trans in trans_list] # reachable states
	reachable_barr = bitarray(2**nvars) # reachable state bit array
	reachable_barr.setall(0)
	for item in rstates:
		ind = int(item, 2)
		reachable_barr[ind] = 1
	return reachable_barr

def get_tran_barr(sg, transition):
	nvars = len(sg.encoding)
	svec = bitarray(2**nvars)
	svec.setall(0)
	for state, _ in get_sg_tran(sg, transition):
		ind = int(state, 2)
		svec[ind] = 1
	return svec

def get_level_barr(sg, level):
	nvars = len(sg.encoding)
	ind = nvars - sg.encoding.index(level.signal)
	svec = bitarray([(i>>ind)&1 for i in range(2**nvars)])
	return ~svec if level=="-" else svec

def is_implication(cause, effect):
	"""
	Evaluate the statement (`cause` implies `effect`).

	Return True iff cause is subset of effect.
	"""
	return cause & effect == cause

def main():
	file = "examples/david_cell.sg"
	sg = load_sg(file)
	signals = sg.encoding
	reachable_barr = get_reachable_barr(sg)
	print_stg(sg)
	# mine atom causalities
	primitive_concepts = []
	psignals = list(product(signals, "+-"))
	transitions = list(starmap(Transition, psignals))
	levels = list(starmap(Level, psignals))
	for tran in transitions:
		tran_barr = get_tran_barr(sg, tran) & reachable_barr
		for level in levels:
			level_barr = get_level_barr(sg, level) & reachable_barr
			if is_implication(tran_barr, level_barr):
				prim = "cause %4s %4s" % (
					get_level_str(level),
					get_tran_str(tran)
				)
				primitive_concepts.append(prim)
	# mine OR causality
	signal_pairs = combinations(sg.encoding, 2)
	pol_pairs = ["++", "+-", "--"]
	or_combs = list(product(signal_pairs, pol_pairs))
	get_comb_levels = lambda comb : \
		(Level(comb[0][0], comb[1][0]), Level(comb[0][1], comb[1][1]))
	level_tups = map(get_comb_levels, or_combs)
	or_cause_concepts = []
	for transition in transitions:
		tran_barr = get_tran_barr(sg, transition) & reachable_barr
		for cond1, cond2 in level_tups:
			cond1_barr = get_level_barr(sg, cond1)
			cond2_barr = get_level_barr(sg, cond2)
			or_barr = (cond1_barr | cond2_barr) & reachable_barr
			if is_implication(tran_barr, or_barr):
				oc_concept = "or_cause %4s %4s %4s" % (
					get_level_str(cond1),
					get_level_str(cond2),
					get_tran_str(transition)
				)
				bogus = not or_barr.any()
				oc_concept_b = "%s (bogus)" % concept if bogus else oc_concept
				or_cause_concepts.append(oc_concept_b)
	concepts = primitive_concepts + or_cause_concepts
	print jsons(concepts, indent=4)

if __name__ == "__main__":
	main()
