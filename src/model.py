#!/usr/bin/env python
# encoding: utf-8
"""
model.py

Created by Pierre Chaussalet on 2011-07-25.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import json

import model

class Model(object):
	pass

class Instance(model.Model):
	def __init__(self, server_id, name, bookmark, details=None):
		self.id = server_id
		self.name = name
		self.bookmark = bookmark
		if details != None:
			self._load_details(details)
			
	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False
		if self.id != other.id:
			return False
		return True
	
	def _load_details(self, details):
		for key in ('hostId', 'status', 'addresses', 'image', 'flavor'):
			if key in details:
				setattr(self, key, details[key])
	
	def to_json(self):
		"""docstring for to_json"""
		info = {}
		info['name'] = self.name
		info['imageRef'] = self.image.bookmark
		info['flavorRef'] = self.flavor.bookmark
		return json.dumps({'server': info}, sort_keys=True)
	

class Flavor(model.Model):
	"""docstring for Flavor"""
	def __init__(self, flavor_id, name, bookmark, details=None):
		super(Flavor, self).__init__()
		self.id = flavor_id
		self.name = name
		self.bookmark = bookmark
		if details != None:
			self.details = details
	
	def __repr__(self):
		return "Flavor : id=%s\tname=%s\tbookmark=%s" % (self.id, self.name, self.bookmark)

class Image(model.Model):
	"""docstring for Image"""
	def __init__(self, image_id, name, bookmark, details=None):
		super(Image, self).__init__()
		self.id = image_id
		self.name = name
		self.bookmark = bookmark
		if details != None:
			self._load_details(details)
	
	def _load_details(self, details):
		"""docstring for _load_details"""
		self.status = details["status"]
		self.created = details["created"]
		self.updated = details["updated"]
	
