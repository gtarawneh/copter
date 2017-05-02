#!/usr/bin/env python

from collections import namedtuple
from itertools   import product
from itertools   import combinations
from itertools   import permutations
from itertools   import starmap
from bitarray    import bitarray
from pprint      import pprint
from json        import dumps as jsons

Literal = namedtuple("Literal", "signal polarity")
SG      = namedtuple("SG", "transitions encoding")

show_literal = lambda literal : literal.signal + literal.polarity

is_negated = lambda x, y : (x.signal == y.signal) and (x.polarity != y.polarity)

def print_stg(sg):
	print "Transitions:\n"
	for key, val in sg.transitions.iteritems():
		print "%4s : %s" % (key, val)
	print "\nEncoding: %s\n" % sg.encoding

def load_sg(file):
	"""
	Load an SG file.
	"""
	# load transitions
	tran_info = {} # trans -> [(from_state, to_state)]
	with open(file, "r") as fid:
		lines = fid.read().splitlines()
	for line in lines:
		if line[0] not in ".#":
			prev_state, transition, next_state = line.split()
			prev_bits = prev_state.split("_")[1]
			next_bits = next_state.split("_")[1]
			tran_info[transition] = tran_info.get(transition, [])
			tran_info[transition].append((prev_bits, next_bits))
	# determine encoding
	encoding_dic = {}
	for tran_item, state_list in tran_info.iteritems():
		signal, polarity = tran_item[:-1], tran_item[-1]
		for state_tup in state_list:
			prev_bits, next_bits = state_tup
			bit_diff = [a!=b for (a,b) in zip(prev_bits, next_bits)]
			diff_inds = [ind for ind, bdiff in enumerate(bit_diff) if bdiff]
			if len(diff_inds) == 1:
				bit = diff_inds[0]
			else:
				raise Exception(
					"Transition %s causes multiple bit changes" % tran_item)
			if signal in encoding_dic:
				if bit != encoding_dic[signal]:
					raise Exception(
						"Inconsistent encoding of signal %s" % signal)
			else:
				encoding_dic[signal] = bit
	encoding_list = [None] * len(encoding_dic)
	for key, value in encoding_dic.iteritems():
		encoding_list[value] = key
	fst = lambda (x, y) : x
	transitions = {key: map(fst, val) for key, val in tran_info.iteritems()}
	return SG(transitions, encoding_list)

def get_reachable_barr(sg):
	"""
	Calculate bit array of reachable states.
	"""
	nvars = len(sg.encoding)
	rstates = sum(sg.transitions.values(), []) # reachable states
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
	for state in sg.transitions[show_literal(transition)]:
		ind = int(state, 2)
		svec[ind] = 1
	return svec

def get_cond_barr(sg, cond):
	nvars = len(sg.encoding)
	ind = nvars - 1 - sg.encoding.index(cond.signal)
	svec = bitarray([(i>>ind)&1 for i in range(2**nvars)])
	return ~svec if cond.polarity=="-" else svec

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
	literals = list(starmap(Literal, product(signals, "+-")))
	print_stg(sg)
	# mine atom causalities
	cause_concepts = []
	for transition in literals:
		tran_barr = get_tran_barr(sg, transition) & reachable_barr
		for cond in literals:
			cond_barr = get_cond_barr(sg, cond) & reachable_barr
			axiom = (transition.signal == cond.signal)
			if is_implication(tran_barr, cond_barr):
				prim = "cause %4s %4s" % \
					(show_literal(cond), show_literal(transition))
				cause_concepts.append(prim)
	# mine OR causality
	label = lambda str, lbl : "%s (%s)" % (str, lbl)
	or_cause_concepts = []
	tran_barrs = {x:get_tran_barr(sg, x) for x in literals}
	cond_barrs = {x:get_cond_barr(sg, x) for x in literals}
	for cond1, cond2, transition in combinations(literals, 3):
		tran_barr = tran_barrs[transition] & reachable_barr
		cond1_barr = cond_barrs[cond1]
		cond2_barr = cond_barrs[cond2]
		or_barr = (cond1_barr | cond2_barr) & reachable_barr
		if is_implication(tran_barr, or_barr):
			concept = "or_cause %4s %4s %4s" % (
				show_literal(cond1),
				show_literal(cond2),
				show_literal(transition)
			)
			if not or_barr.any():
				concept = label(concept, "unreachable")
			if is_negated(cond1, transition) or \
				is_negated(cond2, transition):
				concept = label(concept, "consistency axiom")
			if is_negated(cond1, cond2):
				concept = label(concept, "tautology")
			or_cause_concepts.append(concept)
	concepts = cause_concepts + or_cause_concepts
	print jsons(concepts, indent=4)

if __name__ == "__main__":
	main()
