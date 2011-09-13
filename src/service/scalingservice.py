#!/usr/bin/env python
# encoding: utf-8
"""
scalingservice.py

Created by Pierre Chaussalet on 2011-08-01.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

from service.public import *

import model
import service.modelservice
from oscexceptions import *

class ScalingService(PublicActions):
	_defaults = {	"max_size": 253,
					"min_size": 0,
					"instances_count": 0
				}
	def __init__(self, instance_service):
		self.instance_service = instance_service
	
	def create(self, image, flavor, instances_count=_defaults["instances_count"], lb=None, min_size=_defaults["min_size"], max_size=_defaults["max_size"]):
		"""Return new Instance"""
		if max_size > self._defaults["max_size"]:
			raise OscValueError("Max size of a scaling group cannot be greater than %s (%s requested)." %(self._defaults["max_size"], max_size))
		lb = lb or model.LoadBalancer(None, None, None)
		scaling = model.Scaling(image, flavor, lb, min_size, max_size)
		self.add_instances(scaling, min(max_size, max(instances_count, min_size)))
		return scaling
	
	def add_instances(self, scaling, instances_count):
		offset = len(scaling.instances)+1
		filling_count = scaling.max_size-len(scaling.instances)
		real_count = min(filling_count, instances_count)
		for inc in range(offset, offset+real_count):
			instance = model.Instance(inc, "instance%s" % (inc,), None,{"image": scaling.image, "flavor": scaling.flavor, "addresses": {"private": [{"version": 4, "addr": "192.168.100.%s" % (inc,)}]}})
			self.instance_service.create(instance)
			scaling.instances.append(instance)
			scaling.lb.targets.append(model.LoadBalancer.Target(instance))
	
	def remove_instances(self, scaling, instances_count):
		if len(scaling.instances) >= instances_count:
			emptying_count = len(scaling.instances)-scaling.min_size
			real_count = min(emptying_count, instances_count)
			for inc in range(real_count):
				scaling.instances.pop()
				scaling.lb.targets.pop()
		else:
			raise OscValueError("Unable to remove more instances (%s) than available in this scaling (%s)." % (instances_count, len(scaling.instances)))
	
