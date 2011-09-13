#!/usr/bin/env python
# encoding: utf-8
"""
modelservice.py

Created by Pierre Chaussalet on 2011-08-05.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

def action(function):
	function.is_action = True
	return function

class FooService(object):
	called_methods = {}
	def get_actions(self):
		return ("get", "list")
	
	@action
	def list(self, debug=False):
		self.called_methods["list"] = "list" in self.called_methods.keys() and self.called_methods["list"]+1 or 1
		return []
	
class FakeInstanceService(object):
	def __init__(self):
		self.instances = []
	
	def create(self, instance):
		self.instances.append(instance)

	def list(self):
		return self.instances
		
	def get(self, _id):
		return self.instances[_id-1]