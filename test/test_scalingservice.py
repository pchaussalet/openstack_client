#!/usr/bin/env python
# encoding: utf-8
"""
test_scalingservice.py

Created by Pierre Chaussalet on 2011-08-23.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import unittest

import test_utils
import fakes.f_modelservice

import service.scalingservice
import model
from oscexceptions import *


class test_scalingservice(unittest.TestCase):
	def setUp(self):
		self.scaling_service = service.scalingservice.ScalingService(fakes.f_modelservice.FakeInstanceService())
	
	def test_scaling_creation_with_image(self):
		"""should return new Scaling referencing passed image"""
		scaling = self.scaling_service.create(image=model.Image(1, "image1", "http://foo:123/bar/images/1"),
												flavor=None)
		self.assertIsNotNone(scaling)
		self.assertIsInstance(scaling, model.Scaling)
		self.assertIsNotNone(scaling.image)
		self.assertIsInstance(scaling.image, model.Image)
		self.assertEqual(1, scaling.image.id)
	
	def test_scaling_creation_without_image(self):
		"""should raise TypeError"""
		with self.assertRaises(TypeError):
			scaling = self.scaling_service.create(flavor=None)
	
	def test_scaling_creation_with_flavor(self):
		"""should return new Scaling referencing passed flavor"""
		scaling = self.scaling_service.create(flavor=model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"),
												image=None)
		self.assertIsNotNone(scaling.flavor)
		self.assertIsInstance(scaling.flavor, model.Flavor)
		self.assertEqual(2, scaling.flavor.id)
	
	def test_scaling_creation_without_flavor(self):
		"""should raise TypeError"""
		with self.assertRaises(TypeError):
			scaling = self.scaling_service.create(image=None)
	
	def test_scaling_creation_with_no_instance(self):
		"""should return new Scaling containing no instance"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"))
		self.assertIsInstance(scaling.instances, list)
		self.assertEqual(0, len(scaling.instances))
	
	def test_scaling_creation_with_instance_count(self):
		"""should return new Scaling containing 2 instances"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"),
												2)
		self.assertEqual(2, len(scaling.instances))
		self.assertEqual(2, len(self.scaling_service.instance_service.list()))
		first_instance = scaling.instances[0]
		self.assertEqual(1, first_instance.id)
		self.assertEqual(first_instance, self.scaling_service.instance_service.get(1))
		self.assertIsInstance(first_instance, model.Instance)
		self.assertIsInstance(first_instance.image, model.Image)
		self.assertEqual(1, first_instance.image.id)
		self.assertIsInstance(first_instance.flavor, model.Flavor)
		self.assertEqual(2, first_instance.flavor.id)
	
	def test_scaling_growing_by_1(self):
		"""should modify Scaling by adding a new instance"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"))
		self.scaling_service.add_instances(scaling, 1)
		self.assertEqual(1, len(scaling.instances))
		self.assertEqual(1, len(self.scaling_service.instance_service.list()))
		self.assertEqual(1, scaling.instances[0].id)
		self.scaling_service.add_instances(scaling, 1)
		self.assertEqual(2, len(scaling.instances))
		self.assertEqual(2, len(self.scaling_service.instance_service.list()))
		
		self.assertEqual(2, scaling.instances[1].id)
	
	def test_scaling_growing_by_2(self):
		"""should modify Scaling by adding two new instances"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"))
		self.scaling_service.add_instances(scaling, 2)
		self.assertEqual(2, len(scaling.instances))
		self.assertEqual(1, scaling.instances[0].id)
		self.assertEqual(2, scaling.instances[1].id)
	
	def test_scaling_shrinking_by_1(self):
		"""should modify Scaling by removing last instance"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"),
												2)
		self.scaling_service.remove_instances(scaling, 1)
		self.assertEqual(1, len(scaling.instances))
		self.assertEqual(1, scaling.instances[0].id)
		self.scaling_service.remove_instances(scaling, 1)
		self.assertEqual(0, len(scaling.instances))
	
	def test_scaling_shrinking_by_2(self):
		"""should modify Scaling by removing two last instances"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"),
												3)
		self.scaling_service.remove_instances(scaling, 2)
		self.assertEqual(1, len(scaling.instances))
		self.assertEqual(1, scaling.instances[0].id)
	
	def test_scaling_shrinking_when_empty(self):
		"""should raise IndexError"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"))
		with self.assertRaises(OscValueError):
			self.scaling_service.remove_instances(scaling, 1)
	
	def test_scaling_shrinking_more_instances_than_available(self):
		"""should raise IndexError and leave Scaling untouched"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"),
												2)
		with self.assertRaises(OscValueError):
			self.scaling_service.remove_instances(scaling, 3)
		self.assertEqual(2, len(scaling.instances))
	
	def test_scaling_growing_then_shrinking(self):
		"""should modify Scaling by adding then removing then adding again instances"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"),
												2)
		self.scaling_service.add_instances(scaling, 1)
		self.assertEqual(3, len(scaling.instances))
		self.scaling_service.remove_instances(scaling, 2)
		self.assertEqual(1, len(scaling.instances))
		self.scaling_service.add_instances(scaling, 3)
		self.assertEqual(4, len(scaling.instances))
	
	def test_scaling_creation_without_lb(self):
		"""should return new Scaling with a default LoadBalancer"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"))
		self.assertIsNotNone(scaling.lb)
		self.assertIsInstance(scaling.lb, model.LoadBalancer)
	
	def test_scaling_creation_with_specific_lb(self):
		"""should return new Scaling referencing passed lb"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"),
												lb=model.LoadBalancer(3, "lb3", "10.0.0.1"))
		self.assertIsInstance(scaling.lb, model.LoadBalancer)
		self.assertEqual(3, scaling.lb.id)
		self.assertEqual("192.168.100.254", scaling.lb.private_addr)
		self.assertEqual("10.0.0.1", scaling.lb.public_addr)
	
	def test_scaling_creation_with_lb_and_instances_count(self):
		"""should return new Scaling referencing passed lb and containing 2 instances registered in lb"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"),
												lb=model.LoadBalancer(3, "lb3", "10.0.0.1"),
												instances_count=2)
		self.assertIsNotNone(scaling.lb)
		self.assertEqual(2, len(scaling.instances))
		self.assertEqual(2, len(scaling.lb.targets))
		first_target = scaling.lb.targets[0]
		self.assertIsInstance(first_target, model.LoadBalancer.Target)
		self.assertEqual(1, first_target.id)
		self.assertEqual("192.168.100.1", first_target.address)
		self.assertEqual("ADDING", first_target.status)
	
	def test_scaling_creation_with_min_size(self):
		"""should return new Scaling with passed min_size (2) and 2 instances count"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"),
												min_size=2)
		self.assertEqual(2, scaling.min_size)
		self.assertEqual(2, len(scaling.instances))
	
	def test_scaling_creation_with_min_size_and_smaller_instances_count(self):
		"""should return new Scaling with 3 instances"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"),
												min_size=3,
												instances_count=2)
		self.assertEqual(3, len(scaling.instances))
	
	def test_scaling_creation_with_max_size(self):
		"""should return new Scaling with passed max_size"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"),
												max_size=10)
		self.assertEqual(10, scaling.max_size)
	
	def test_scaling_creation_with_max_size_and_bigger_instances_count(self):
		"""should return new Scaling with 10 instances"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"),
												max_size=10,
												instances_count=20)
		self.assertEqual(10, len(scaling.instances))
	
	def test_scaling_growing_above_max_size(self):
		"""should modify Scaling by adding instances up to max_size"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"),
												max_size=2)
		self.scaling_service.add_instances(scaling, 10)
		self.assertEqual(2, len(scaling.instances))
	
	def test_scaling_shrinking_below_min_size(self):
		"""should modify Scaling by removing instances up to min_size"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"),
												min_size=2,
												instances_count=3)
		self.scaling_service.remove_instances(scaling, 3)
		self.assertEqual(2, len(scaling.instances))
	
	def test_scaling_growing_above_default_max_size(self):
		"""should moodify Scaling by adding instances up to default_max_size (253)"""
		scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
												model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"))
		self.scaling_service.add_instances(scaling, 1024)
		self.assertEqual(253, len(scaling.instances))
	
	def test_scaling_creation_with_max_size_greater_than_253(self):
		"""should raise OscValueError"""
		with self.assertRaises(OscValueError):
			scaling = self.scaling_service.create(model.Image(1, "image1", "http://foo:123/bar/images/1"),
													model.Flavor(2, "flavor2", "http://foo:123/bar/flavors/2"),
													max_size=1024)
	
