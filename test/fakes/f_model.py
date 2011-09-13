#!/usr/bin/env python
# encoding: utf-8
"""
f_model.py

Created by Pierre Chaussalet on 2011-08-08.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

class FooModel(object):
	def __init__(self, _id, name, bookmark=None, details = None):
		self.id = _id
		self.name = name
		self.bookmark = bookmark
		self.details = details
		