#!/usr/bin/env python
# encoding: utf-8
"""
test_modelservice.py

Created by Pierre Chaussalet on 2011-08-05.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import unittest
import json
import datetime

import test_utils

import service.modelservice
import nova
import model

import fakes.f_model

class ModelTestCase(unittest.TestCase):
	def setUp(self):
		self.client = nova.NovaClient("http://foo:123/bar", "user", "key")
		self.service = self.class_to_test(self.client)
		self.service.connection.conn = fakes.f_httplib.FakeHTTPConnection()
		self.service.connection.auth_token = {"X-Auth-Token": "fake_token"}
	

class test_modelservice(ModelTestCase):
	class_to_test = service.modelservice.ModelService
	def setUp(self):
		self.class_to_test.item_class = fakes.f_model.FooModel
		ModelTestCase.setUp(self)
		del self.class_to_test.item_class
		self.service.prefix = "/foo"
	
	def test_model_service_init(self):
		"""should raise an exception"""
		with self.assertRaises(Exception):
			service.modelservice.ModelService(self.client)
	
	def test_get_new_item_with_name(self):
		"""should return new Foo object"""
		service.modelservice.ModelService.item_class = fakes.f_model.FooModel
		item = service.modelservice.ModelService(self.client).get_new_item("FooName")
		self.assertIsInstance(item, fakes.f_model.FooModel)
		self.assertEqual("FooName", item.name)
	
	def test_get_new_item_without_name(self):
		"""should raise exception"""
		service.modelservice.ModelService.item_class = fakes.f_model.FooModel
		with self.assertRaises(TypeError):
			service.modelservice.ModelService(self.client).get_new_item()
	
	def test_list_items_with_correct_data(self):
		"""should return items list"""
		items = self.service._list_items("foos", fakes.f_model.FooModel)
		self.assertEqual(2, len(items))
		self.assertIsInstance(items[0], fakes.f_model.FooModel)
		self.assertIsInstance(items[1], fakes.f_model.FooModel)
		self.assertEqual("foo1", items[0].name)
	
	def test_list_items_without_required_data(self):
		"""should raise TypeError"""
		with self.assertRaises(TypeError):
			self.service._list_items()
	
	def test_list_items_without_item_class(self):
		"""should raise TypeError"""
		with self.assertRaises(TypeError):
			self.service._list_items("foos")
	
	def test_list_items_with_incorrect_items_name(self):
		"""should raise KeyError"""
		with self.assertRaises(KeyError):
			self.service._list_items("bar", fakes.f_model.FooModel)
	
	def test_get_item_details_with_correct_data(self):
		"""should return item details"""
		item = self.service._get_item_details("http://foo:123/bar/foo/2468", "foo", fakes.f_model.FooModel)
		self.assertIsInstance(item, fakes.f_model.FooModel)
		self.assertEqual(2468, item.id)
		self.assertEqual("foo2468", item.name)
	
	def test_get_item_details_without_required_data(self):
		"""should raise TypeError"""
		with self.assertRaises(TypeError):
			self.service._get_item_details()
	
	def test_get_item_details_without_item_name_and_item_class(self):
		"""should raise TypeError"""
		with self.assertRaises(TypeError):
			self.service._get_item_details("http://foo:123/bar/foo/2468")
	
	def test_get_item_details_without_item_class(self):
		"""should raise TypeError"""
		with self.assertRaises(TypeError):
			self.service._get_item_details("http://foo:123/bar/foo/2468", "foo")
	
	def test_get_item_details_with_incorrect_item_name(self):
		"""should raise KeyError"""
		with self.assertRaises(KeyError):
			self.service._get_item_details("http://foo:123/bar/foo/2468", "bar", fakes.f_model.FooModel)
	
	def test_response_to_model_with_correct_data(self):
		"""should return item without any reference"""
		item = self.service._response_to_model({"id": 3579, "name": "foo3579", "imageRef": "http://foo:345/bar/image/123"})
		self.assertIn("image", item.keys())
		self.assertIsInstance(item["image"], model.Image)
		self.assertEqual(123, item["image"].id)
	
	def test_delete_with_id(self):
		"""should return None"""
		response = self.service.delete(123)
		self.assertIsNone(response)
	
	def test_delete_without_id(self):
		"""should raise TypeError"""
		with self.assertRaises(TypeError):
			self.service.delete()
	

class test_instanceservice(ModelTestCase):
	class_to_test = service.modelservice.InstanceService
	def test_instance_service_init(self):
		"""should return new InstanceService"""
		instance_service = service.modelservice.InstanceService(self.client)
		self.assertIsNotNone(instance_service)
		self.assertEqual(model.Instance, instance_service.item_class)
	
	def test_instance_create_with_instance_object(self):
		"""should return newly created Instance with associated password"""
		image = model.Image(567, "foo_image", "http://server:987/v0.0/image/567")
		flavor = model.Flavor(890, "foo_flavor", "http://server:890/v0.0/flavor/890")
		input_instance = model.Instance(None, "foo_instance")
		input_instance.image = image
		input_instance.flavor = flavor
		instance, password = self.service.create(input_instance)
		self.assertIsInstance(instance, model.Instance)
		self.assertEqual(1234, instance.id)
		self.assertEqual("http://foo:123/bar/servers/1234", instance.bookmark)
		self.assertEqual("someSecretPassword", password)
	
	def test_instance_create_without_image_object(self):
		"""should raise AttributeError"""
		flavor = model.Flavor(890, "foo_flavor", "http://server:890/v0.0/flavor/890")
		input_instance = model.Instance(None, "foo_instance")
		input_instance.flavor = flavor
		with self.assertRaises(AttributeError):
			instance, password = self.service.create(input_instance)
	
	def test_instance_create_without_flavor_object(self):
		"""should raise AttributeError"""
		image = model.Image(567, "foo_image", "http://server:987/v0.0/image/567")
		input_instance = model.Instance(None, "foo_instance")
		input_instance.image = image
		with self.assertRaises(AttributeError):
			instance, password = self.service.create(input_instance)
	
	def test_instance_create_with_json_data(self):
		"""should return newly created Instance with associated password"""
		data = {"server": 	{	"name": "foo_instance",
								"imageRef": "http://foo/bar/image/567",
								"flavorRef": "http://bar/foo/flavor/890"
							}
				}
		instance, password = self.service.create(json.dumps(data))
		self.assertIsInstance(instance, model.Instance)
		self.assertEqual(1234, instance.id)
		self.assertEqual("http://foo:123/bar/servers/1234", instance.bookmark)
		self.assertEqual("someSecretPassword", password)
	
	def test_instance_create_without_imageRef_json(self):
		"""should raise AttributeError"""
		data = {"server": 	{	"name": "foo_instance",
								"flavorRef": "http://bar/foo/flavor/890"
							}
				}
		with self.assertRaises(AttributeError):
			instance, password = self.service.create(json.dumps(data))
	
	def test_instance_create_without_flavorRef_json(self):
		"""should raise AttributeError"""
		data = {"server": 	{	"name": "foo_instance",
								"imageRef": "http://foo/bar/image/567"
							}
				}
		with self.assertRaises(AttributeError):
			instance, password = self.service.create(json.dumps(data))
	

class test_imageservice(ModelTestCase):
	class_to_test = service.modelservice.ImageService
	def test_image_service_init(self):
		"""should return new ImageService"""
		image_service = service.modelservice.ImageService(self.client)
		self.assertIsNotNone(image_service)
		self.assertEqual(model.Image, image_service.item_class)
	
	def test_image_create_without_name(self):
		"""should return newly created Image"""
		image = self.service.create(123)
		self.assertIsInstance(image, model.Image)
		self.assertEqual(987, image.id)
		self.assertTrue(image.name.startswith("%s_%s" % (123, datetime.datetime.now().isoformat()[:19])))
	
	def test_image_create_with_name(self):
		"""should return newly created Image"""
		image = self.service.create(123, "fooImage")
		self.assertIsInstance(image, model.Image)
		self.assertEqual(987, image.id)
		self.assertEqual("fooImage", image.name)
	

if __name__ == '__main__':
	unittest.main()