#!/usr/bin/env python
# encoding: utf-8
"""
test_nova.py

Created by Pierre Chaussalet on 2011-08-05.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import unittest

import test_utils

import nova
import fakes.f_httplib
import fakes.f_modelservice


class test_nova(unittest.TestCase):
	def setUp(self):
		self.client = nova.NovaClient("http://server:12345/version/foo/bar", "foo_user", "bar_key")
		self.client.connection.conn = fakes.f_httplib.FakeHTTPConnection()
		self.client.connection.auth_token = {"X-Auth-Token": "fake_token"}
		self.client.service_mapping = {"foo": fakes.f_modelservice.FooService()}
	
	def test_new_nova_client(self):
		"""should return new NovaClient"""
		client = nova.NovaClient("http://server:12345/version/foo/bar", "foo_user", "bar_key")
		self.assertIsNotNone(client)
		self.assertIsNotNone(client.connection)		
		self.assertEqual("http://server:12345/version/foo/bar", client.connection.url)
		self.assertEqual("foo_user", client.connection.user)
		self.assertEqual("bar_key", client.connection.key)
		self.assertEqual(3, len(client.service_mapping))
		self.assertIn("instance", client.service_mapping.keys())
		self.assertIsNotNone(client.service_mapping["instance"])
		self.assertIn("image", client.service_mapping.keys())
		self.assertIsNotNone(client.service_mapping["image"])
		self.assertIn("flavor", client.service_mapping.keys())
		self.assertIsNotNone(client.service_mapping["flavor"])
		self.assertEqual({}, client.pools)
	
	def test_handle_request_with_correct_data(self):
		"""should call action in service"""
		response = self.client.handle_request("foo", "list")
		self.assertEqual(1, self.client.service_mapping["foo"].called_methods["list"])
		self.assertIsNotNone(response)

	def test_handle_request_with_incorrect_service(self):
		"""should raise Exception"""
		with self.assertRaises(Exception) as has_raised:
			response = self.client.handle_request("bar", "list")

	def test_handle_request_with_incorrect_action(self):
		"""should raise Exception"""
		with self.assertRaises(Exception) as has_raised:
			response = self.client.handle_request("foo", "bar")

if __name__ == '__main__':
	unittest.main()