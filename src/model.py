#!/usr/bin/env python
# encoding: utf-8
"""
model.py

Created by Pierre Chaussalet on 2011-07-25.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import json

class Model(object):
	def __repr__(self):
		return "%s : id=%s\tname=%s\tbookmark=%s" % (self.__class__.__name__, self.id, self.name, self.bookmark)
	
	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False
		if self.id != other.id:
			return False
		return True
		
	def __ne__(self, other):
		return not (self == other)
	
	def __cmp__(self, other):
		if self == other:
			return 0
		return cmp(self.id, other.id)
	


class Instance(Model):
	path = "servers"
	def __init__(self, server_id, name, bookmark=None, details=None):
		self.id = server_id
		self.name = name
		self.bookmark = bookmark
		if details != None:
			self._load_details(details)
	
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
	

class Flavor(Model):
	path = "flavors"
	def __init__(self, flavor_id, name, bookmark, details=None):
		super(Flavor, self).__init__()
		self.id = flavor_id
		self.name = name
		self.bookmark = bookmark
		if details != None:
			self.details = details
	

class Image(Model):
	path = "flavors"
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
	

class Scaling(Model):	
	def __init__(self, image, flavor, lb, min_size, max_size):
		super(Scaling, self).__init__()
		self.image = image
		self.flavor = flavor
		self.instances = []
		self.lb = lb
		self.min_size = min_size
		self.max_size = max_size
	

class LoadBalancer(Instance):
	RESP_TIME = "lb_rt"
	def __init__(self, _id, name, public):
		super(LoadBalancer, self).__init__(_id, name, details={"addresses": {"private": [{"version": 4, "addr": "192.168.100.254"}], "public": [{"version": 4, "addr": public}]}})
		self.public_addr = self.addresses["public"][0]["addr"]
		self.private_addr = self.addresses["private"][0]["addr"]
		self.targets = []
	
	class Target(object):
		def __init__(self, instance):
			super(LoadBalancer.Target, self).__init__()
			self.id = instance.id
			self.address = instance.addresses["private"][0]["addr"]
			self.status = "ADDING"
	

class Alert(Model):
	def __init__(self, lb, action, trigger, cool_time):
		super(Alert, self).__init__()
		self.lb = lb
		self.method, self.args = action
		self.ref_metric, self.comparison, self.ref_value = trigger
		self.history = []
		self.triggered = False
		self.cool_time = cool_time
	
	@staticmethod
	def GT(value, ref):
		return value > ref
	
	@staticmethod
	def GE(value, ref):
		return value >= ref
	
	@staticmethod
	def LT(value, ref):
		return value < ref
	
	@staticmethod
	def LE(value, ref):
		return value <= ref