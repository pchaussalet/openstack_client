#!/usr/bin/env python
# encoding: utf-8
"""
oscexceptions.py

Created by Pierre Chaussalet on 2011-08-25.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

class OscBaseError(Exception):
	def __init__(self, message):
		super(OscBaseError, self).__init__()
		self.message = message
	
	def __str__(self):
		return message
	
class OscValueError(OscBaseError):
	pass
