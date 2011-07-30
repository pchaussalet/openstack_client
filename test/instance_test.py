#!/usr/bin/env python
# encoding: utf-8
"""
server_test.py

Created by Pierre Chaussalet on 2011-07-26.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import unittest
import sys, os.path

cmd_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if cmd_folder not in sys.path:
	sys.path.insert(0, cmd_folder)

import model


class instance_test(unittest.TestCase):
	class FakeImage(object):
		def __init__(self):
			self.bookmark = "http://server/v1.1/imageRef"

	class FakeFlavor(object):
		def __init__(self):
			self.bookmark = "http://server2/v1.2/flavorRef"

	def setUp(self):
		self.image = self.FakeImage()
		self.flavor = self.FakeFlavor()

	def test_instance_to_json(self):
		request = model.Instance(None, "server-name", None, {"hostId": None, "status": None, "addresses": None, "image": self.image, "flavor": self.flavor})
		expected_json = '{"server": {"flavorRef": "http://server2/v1.2/flavorRef", "imageRef": "http://server/v1.1/imageRef", "name": "server-name"}}'
		self.assertEqual(expected_json, request.to_json())
    
if __name__ == '__main__':
	unittest.main()