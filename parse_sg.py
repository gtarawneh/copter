#!/usr/bin/env python

from collections import namedtuple
from collections import defaultdict
from itertools   import product
from itertools   import combinations
from itertools   import permutations
from itertools   import starmap
from bitarray    import bitarray
from pprint      import pprint
from json        import dumps as jsons
from concepts    import *

class SG(namedtuple("SG", "transitions encoding")):

	def __str__(self):
		header = ["Transitions:", ""]
		items = ["%4s : %s" % (key, val) for key, val \
			in self.transitions.iteritems()]
		footer = ["", "Encoding: %s" % self.encoding, ""]
		return "\n".join(header + items + footer)

def load_sg(file):
	"""
	Load an SG file.
	"""
	# load transitions
	tran_info = defaultdict(list) # trans -> [(from_state, to_state)]
	with open(file, "r") as fid:
		lines = fid.read().splitlines()
	for line in lines:
		if line[0] not in ".#":
			prev_state, transition, next_state = line.split()
			prev_bits = prev_state.split("_")[1]
			next_bits = next_state.split("_")[1]
			tran_info[transition].append((prev_bits, next_bits))
	# determine encoding
	encoding_dic = {}
	for tran_item, state_list in tran_info.iteritems():
		signal, polarity = tran_item[:-1], tran_item[-1]
		for state_tup in state_list:
			prev_bits, next_bits = state_tup
			bit_diff = [a!=b for (a,b) in zip(prev_bits, next_bits)]
			diff_inds = [ind for ind, bdiff in enumerate(bit_diff) if bdiff]
			bit = diff_inds[0]
			if len(diff_inds) > 1:
				raise Exception("multiple bit changes after %s" % tran_item)
			if bit != encoding_dic.get(signal, bit):
				raise Exception("inconsistent encoding of signal %s" % signal)
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
	for state in sg.transitions[str(transition)]:
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
	sg, cause_concepts, or_cause_concepts = mine_concepts(file, False)
	concepts = cause_concepts + or_cause_concepts
	print sg
	print jsons(map(str, concepts), indent=4)

def mine_concepts(file, add_labels):
	sg = load_sg(file)
	signals = sg.encoding
	reachable_barr = get_reachable_barr(sg)
	literals = list(starmap(Literal, product(signals, "+-")))
	label = lambda x, lbl : "%s (%s)" % (x, lbl) if add_labels else x
	tran_barrs = {x:get_tran_barr(sg, x) & reachable_barr for x in literals}
	cond_barrs = {x:get_cond_barr(sg, x) & reachable_barr for x in literals}
	# mine atom causalities
	cause_concepts = []
	for transition, cond in permutations(literals, 2):
		if is_negated(transition, cond):
			continue
		tran_barr = tran_barrs[transition]
		cond_barr = cond_barrs[cond]
		if is_implication(tran_barr, cond_barr):
			tags = []
			if is_negated(cond, transition):
				tags.append("consistency axiom")
			concept = Cause(cond, transition)
			cause_concepts.append(concept)
	# mine OR causality
	cause_set = set(cause_concepts)
	or_cause_concepts = []
	for transition, cond1, cond2 in permutations(literals, 3):
		tran_barr = tran_barrs[transition]
		cond1_barr = cond_barrs[cond1]
		cond2_barr = cond_barrs[cond2]
		or_barr = cond1_barr | cond2_barr
		if is_implication(tran_barr, or_barr):
			concept = "or_cause %4s %4s %4s" % (cond1, cond2, transition)
			tags = []
			if not or_barr.any():
				tags.append("unreachable")
			if is_negated(cond1, transition) or is_negated(cond2, transition):
				tags.append("consistency axiom")
			if is_negated(cond1, cond2):
				tags.append("tautology")
			if Cause(cond1, transition) in cause_set or \
				Cause(cond2, transition) in cause_set:
				tags.append("corollary")
			concept = OrCause(cond1, cond2, transition)
			or_cause_concepts.append(concept)
	# produce outputs
	return sg, cause_concepts, or_cause_concepts

if __name__ == "__main__":
	main()
