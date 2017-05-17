#!/usr/bin/env python

from collections import namedtuple

class Literal(namedtuple("Literal", "signal polarity")):

	def __str__(self):
		return self.signal + self.polarity

	def __invert__(self):
		oppo_polarity = "-" if (self.polarity == "+") else "+"
		return Literal(self.signal, oppo_polarity)

class Cause(namedtuple("Cause", "cond transition")):

	def __str__(self):
		return "cause %s %s" % (self.cond, self.transition)

class OrCause(namedtuple("OrCause", "cond1 cond2 transition")):

	def __get_ordered(self):
		return (self.cond1, self.cond2) if (self.cond1 < self.cond2) \
			else (self.cond2, self.cond1)

	def __str__(self):
		return "or_cause %s %s %s" % (self.cond1, self.cond2, self.transition)

	def __eq__(self, x):
		if type(x) is not OrCause:
			return False
		tran_match = self.transition == x.transition
		cond_match = self.__get_ordered() == x.__get_ordered()
		return tran_match and cond_match

	def __hash__(self):
		ordered = self.__get_ordered()
		return hash((ordered, self.transition))

class OrGate(namedtuple("OrGate", "a b y")):

	def __get_ordered(self):
		return (self.a, self.b) if (self.a < self.b) else (self.b, self.a)

	def __str__(self):
		ordered = self.__get_ordered()
		return "orGate %s %s %s" % (ordered[0], ordered[1], self.y)

	def __eq__(self, other):
		output_match = self.y == other.y
		input_match = self.__get_ordered() == other.__get_ordered()
		return output_match and input_match

	def __hash__(self):
		ordered = self.__get_ordered(self)
		return hash((ordered, self.y))

class NorGate(namedtuple("NorGate", "a b y")):

	def __get_ordered(self):
		return (self.a, self.b) if (self.a < self.b) else (self.b, self.a)

	def __str__(self):
		ordered = self.__get_ordered()
		return "norGate %s %s %s" % (ordered[0], ordered[1], self.y)

	def __eq__(self, other):
		if type(other) is not NorGate:
			return False
		output_match = self.y == other.y
		input_match = self.__get_ordered() == other.__get_ordered()
		return output_match and input_match

	def __hash__(self):
		ordered = self.__get_ordered()
		return hash((ordered, self.y))
