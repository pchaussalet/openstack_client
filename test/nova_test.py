#!/usr/bin/env python
# encoding: utf-8
"""
nova_test.py

Created by Pierre Chaussalet on 2011-07-26.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import unittest
import httplib
import urlparse
import sys
import os.path
import json

cmd_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if cmd_folder not in sys.path:
	sys.path.insert(0, cmd_folder)

import nova
import utils.http.response as response
import model

import service.connectionservice

class FakeHTTPResponse(object):
	def __init__(self, status, message, headers, body=None, protocol=11):
		self.status = status
		self.message = message
		self.headers = headers
		self.body = body
		self.protocol = protocol
		

class nova_test(unittest.TestCase):
	def setUp(self):
		self.connection = service.connectionservice.ConnectionService("http://localhost:54321/v1.1", "user", "password")
		self.connection._send_request = self._fake_send_request
		self.client = nova.NovaClient("http://localhost:54321/v1.1", "user", "password")
		self.client.connection = self.connection
		for name, clientservice in self.client.service_mapping.items():
			clientservice.connection = self.connection
		model_service = self.client.service_mapping.items()[0][1]
		self.response_to_model = lambda response: model_service._response_to_model(response)
		self.extract_bookmark = lambda bookmarks: model_service._extract_bookmark(bookmarks)

	def _fake_send_request(self, path, method="GET", data=None):
		path_elements = urlparse.urlsplit(path)
		if path_elements.scheme != '':
			path = path_elements.path
		elif "v1.1" not in path:
			path = "/v1.1" + path
		req_infos = [tmp for tmp in path.split("/") if tmp != '']
		choose_datasource = lambda x: "resources/"+"_".join(("get", x[1], ("base", "detailed")[len(x) % 2]))+".json"
		datasource = choose_datasource(req_infos)
		return FakeHTTPResponse(200, "Success", (), open(datasource, "r").read())

	def test_handle_request(self):
		servers = self.client.handle_request('instance', 'list')
		expected_dict = json.loads(self.connection._send_request("/servers").body)['servers'][0]
		expected = [model.Instance(expected_dict['id'], expected_dict['name'], self.extract_bookmark(expected_dict['links']), expected_dict)]
		self.assertEqual(expected, servers)
    
if __name__ == '__main__':
	unittest.main()