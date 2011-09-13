#!/usr/bin/env python
# encoding: utf-8
"""
test_scalingservice.py

Created by Pierre Chaussalet on 2011-08-23.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""
import time

import unittest

import test_utils

import model
import service.alertservice
from oscexceptions import *

class test_alertservice(unittest.TestCase):
	def setUp(self):
		self.alertservice = service.alertservice.AlertService()
	
	def fake_method(self):
		self.called += 1
	
	def test_alert_creation_with_load_balancer(self):
		"""should return new Alert referencing passed LoadBalancer"""
		lb = model.LoadBalancer(123, "FooLb", "192.168.1.1	")
		alert = self.alertservice.create(lb, (None, None), (None, None, None))
		self.assertIsNotNone(alert)
		self.assertIsInstance(alert, model.Alert)
		self.assertIsNotNone(alert.lb)
		self.assertIsInstance(alert.lb, model.LoadBalancer)
		self.assertEqual(123, alert.lb.id)
	
	def test_alert_creation_with_scaling_add_instance(self):
		"""should return new Alert referencing passed function and args"""
		action = service.scalingservice.ScalingService.add_instances
		args = (model.Scaling(None, None, None, None, None), 1)
		alert = self.alertservice.create(None, (action, args), (None, None, None))
		self.assertIsNotNone(alert)
		self.assertIsInstance(alert, model.Alert)
		self.assertIsNotNone(alert.method)
		self.assertTrue(callable(alert.method))
		self.assertIsInstance(alert.args, tuple)
		self.assertEqual(2, len(alert.args))
	
	def test_alert_creation_with_reference_value(self):
		"""should return new Alert referencing passed reference value"""
		alert = self.alertservice.create(None, (None, None), (model.LoadBalancer.RESP_TIME, model.Alert.GT, 2))
		self.assertIsNotNone(alert)
		self.assertIsInstance(alert, model.Alert)
		self.assertIsNotNone(alert.ref_metric)
		self.assertEqual(model.LoadBalancer.RESP_TIME, alert.ref_metric)
		self.assertIsNotNone(alert.comparison)
		self.assertEqual(model.Alert.GT, alert.comparison)
		self.assertIsNotNone(alert.ref_value)
		self.assertEqual(2, alert.ref_value)
	
	def test_alert_triggering(self):
		"""should call defined trigger action"""
		self.called = 0
		alert = self.alertservice.create(None, (self.fake_method, tuple()), (model.LoadBalancer.RESP_TIME, model.Alert.GE, 2))
		self.assertEqual(False, alert.triggered)
		self.alertservice.validate(alert, 1)
		self.assertEqual(0, self.called)
		self.alertservice.validate(alert, 2)
		self.assertEqual(True, alert.triggered)
		self.assertEqual(1, self.called)
	
	def test_alert_trigger_logging(self):
		"""should add an entry in alert's history"""
		self.called = 0
		alert = self.alertservice.create(None, (self.fake_method, tuple()), (model.LoadBalancer.RESP_TIME, model.Alert.LT, 2))
		self.assertEqual(0, len(alert.history))
		self.alertservice.validate(alert, 1)
		self.assertEqual(1, len(alert.history))
	
	def test_alert_triggered_come_back_to_normal(self):
		"""should restore alert to normal mode on correct value reception
		should be logged, too"""
		self.called = 0
		alert = self.alertservice.create(None, (self.fake_method, tuple()), (model.LoadBalancer.RESP_TIME, model.Alert.LE, 2), cool_time=0)
		self.alertservice.validate(alert, 2)
		self.assertEqual(True, alert.triggered)
		hist_len = len(alert.history)
		self.alertservice.validate(alert, 4)
		self.assertEqual(False, alert.triggered)
		self.assertEqual(hist_len+1, len(alert.history))
	
	def test_alert_triggered_has_cool_time(self):
		"""triggered alert should not call method until cool time has elapsed"""
		self.called = 0
		alert = self.alertservice.create(None, (self.fake_method, tuple()), (model.LoadBalancer.RESP_TIME, model.Alert.GE, 2), cool_time=2)
		self.assertEqual(False, alert.triggered)
		self.alertservice.validate(alert, 2)
		self.assertEqual(True, alert.triggered)
		self.assertEqual(1, self.called)
		self.alertservice.validate(alert, 3)
		self.assertEqual(True, alert.triggered)
		self.assertEqual(1, self.called)
		time.sleep(2)
		self.alertservice.validate(alert, 3)
		self.assertEqual(True, alert.triggered)
		self.assertEqual(2, self.called)
		