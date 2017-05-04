#!/usr/bin/env python

from collections import namedtuple

class Literal(namedtuple("Literal", "signal polarity")):

	def __str__(self):
		return self.signal + self.polarity

class Cause(namedtuple("Cause", "cond transition")):

	def __str__(self):
		return "cause %s %s" % (self.cond, self.transition)

class OrCause(namedtuple("OrCause", "cond1 cond2 transition")):

	def __str__(self):
		return "or_cause %s %s %s" % (self.cond1, self.cond2, self.transition)

	def __eq__(self, x):
		tran_match = self.transition == x.transition
		cond_match_1 = (self.cond1 == x.cond1) and (self.cond2 == x.cond2)
		cond_match_2 = (self.cond1 == x.cond2) and (self.cond2 == x.cond1)
		return tran_match and (cond_match_1 or cond_match_2)

def is_negated(x, y):
	return (x.signal == y.signal) and (x.polarity != y.polarity)
