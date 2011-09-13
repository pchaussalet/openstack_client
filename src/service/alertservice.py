#!/usr/bin/env python
# encoding: utf-8
"""
scalingservice.py

Created by Pierre Chaussalet on 2011-08-01.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""
import time

from service.public import *

import model
from oscexceptions import *

class AlertService(object):
	"""docstring for AlertService"""
	def __init__(self):
		super(AlertService, self).__init__()

	def create(self, lb, action, trigger, cool_time=120):
		alert = model.Alert(lb, action, trigger, cool_time)
		return alert
		
	def validate(self, alert, value):
		if len(alert.history) == 0 or time.time() > alert.history[-1][0]+alert.cool_time:
			if alert.comparison(value, alert.ref_value):
				alert.method(*alert.args)
				alert.history.append((time.time(), "A", alert.ref_metric, alert.comparison.__name__, value))
				alert.triggered = True
			elif alert.triggered:
				alert.triggered = False
				alert.history.append((time.time(), "N", alert.ref_metric, alert.comparison.__name__, value))
	