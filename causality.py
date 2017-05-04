#!/usr/bin/env python

from collections import namedtuple

class Cause(namedtuple("Cause", "cond transition")):

	def __str__(self):
		return "cause %s %s" % (self.cond, self.transition)

class OrCause(namedtuple("OrCause", "cond1 cond2 transition")):

	def __str__(self):
		return "or_cause %s %s %s" % (self.cond1, self.cond2, self.transition)
