#!/usr/bin/env python
# encoding: utf-8
"""
test_connectionservice.py

Created by Pierre Chaussalet on 2011-08-04.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""
import unittest
import json

import test_utils

import service.connectionservice
import fakes.f_httplib

class test_connectionservice(unittest.TestCase):
	def setUp(self):
		self.service = service.connectionservice.ConnectionService("http://server_hostname:12345/vX.X/", "fake_username", "fake_userkey")
		self.service.conn = fakes.f_httplib.FakeHTTPConnection()
		self.service.auth_token = {"X-Auth-Token": "fake_token"}

	def test_extract_endpoint_with_explicit_port(self):
		"""should return correct host and port tuple"""
		host, port = self.service._extract_endpoint("http://server:67890/foo/bar")
		self.assertEqual("server", host)
		self.assertEqual(67890, port)
	
	def test_extract_endpoint_with_implicit_http_port(self):
		"""should return correct host and default port"""
		host, port = self.service._extract_endpoint("http://server/foo/bar")
		self.assertEqual("server", host)
		self.assertEqual(80, port)
	
	def test_extract_endpoint_with_implicit_https_port(self):
		"""should return correct host and default port"""
		host, port = self.service._extract_endpoint("https://server/foo/bar")
		self.assertEqual("server", host)
		self.assertEqual(443, port)
	
	def test_extract_endpoint_with_invalid_url(self):
		"""should raise Exception"""
		with self.assertRaises(Exception) as has_raised:
			host, port = self.service._extract_endpoint("http:///")
	
	def test_authenticate(self):
		"""should set X-Auth-Token"""
		self.service.conn = fakes.f_httplib.FakeHTTPConnection()
		del self.service.auth_token
		self.service.authenticate()
		auth_token = self.service.auth_token
		self.assertIsInstance(auth_token, dict)
		self.assertIn("X-Auth-Token", auth_token.keys())
		self.assertEqual("fake_token", auth_token["X-Auth-Token"])
	
	def test_send_request_with_only_slash(self):
		"""should correctly set default values"""
		conn = self.service.conn
		resp = self.service._send_request("/")
		self.assertEqual(200, resp.status)
		self.assertEqual("GET", conn.method)
		self.assertEqual("http://server_hostname:12345/vX.X/", conn.url)
		self.assertEqual(None, conn.body)
		self.assertIn("X-Auth-Token", conn.headers.keys())
		self.assertEqual("fake_token", conn.headers["X-Auth-Token"])
		self.assertIn("Content-type", conn.headers.keys())
		self.assertEqual("application/json", conn.headers["Content-type"])
		self.assertIn("Accept", conn.headers.keys())
		self.assertEqual("application/json", conn.headers["Accept"])
	
	def test_send_request_with_correct_path(self):
		"""should correctly set default values"""
		resp = self.service._send_request("/foo/bar")
		self.assertEqual("http://server_hostname:12345/vX.X/foo/bar", self.service.conn.url)

	def test_send_request_with_absolute_path(self):
		"""should ignore self.host and self.port"""
		resp = self.service._send_request("http://bar/vY.Y/foo")
		self.assertEqual("http://bar/vY.Y/foo", self.service.conn.url)


if __name__ == '__main__':
	unittest.main()