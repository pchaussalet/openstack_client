#!/usr/bin/env python
# encoding: utf-8
"""
public.py

Created by Pierre Chaussalet on 2011-08-01.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

def action(function):
	function.is_action = True
	return function

class PublicActions(object):
	"""docstring for PublicActions"""
	def __init__(self):
		super(PublicActions, self).__init__()
	
	def get_actions(self):
		print self
		if not hasattr(self, 'actions'):
			self.actions = []
			for action in [function for function in dir(self) if hasattr(getattr(self, function), 'is_action')]:
				self.actions.append(action)
		self.actions.sort()
		return self.actions
	
