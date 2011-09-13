#!/usr/bin/env python
# encoding: utf-8
"""
fake_connection.py

Created by Pierre Chaussalet on 2011-08-04.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import json
import datetime

class FakeHTTPResponse(object):
	def __init__(self, status, reason, version, headers={}, body=None):
		self.status = status
		self.reason = reason
		self.version = version
		self.headers = headers
		self.body = body

	def getheader(self, name):
		return self.headers[name]
	
	def getheaders(self):
		return self.headers

	def read(self):
		return self.body
	
class FakeHTTPConnection(object):
	response = FakeHTTPResponse(200, "OK", "HTTP/1.1")
	def request(self, method, url, body, headers= None):
		self.method = method
		self.url = url
		self.body = body
		self.headers = headers
		if method == "POST":
			if headers != None and "X-Auth-User" in headers.keys() and "X-Auth-Key" in headers.keys():
				self.response.headers["X-Auth-Token"] = "fake_token"
				return
			if url == "http://foo:123/bar/servers":
				resp = json.loads(self.body)
				resp["server"]["id"] = 1234
				resp["server"]["links"] = [
											{"href": "http://foo:123/bar/servers/1234", "type": "application/xml", "rel": "bookmark"},
											{"href": "http://foo:123/bar/servers/1234", "type": "application/json", "rel": "bookmark"},
											{"href": "http://foo:123/bar/servers/1234", "rel": "self"}
										]
				resp["server"]["adminPass"] = "someSecretPassword"
			if url == "http://foo:123/bar/images":
				resp = json.loads(self.body)["image"]
				del resp["serverId"]
				resp["id"] = 987
				resp["links"] = [
									{"href": "http://foo:123/bar/images/987", "type": "application/xml", "rel": "bookmark"},
									{"href": "http://foo:123/bar/images/987", "type": "application/json", "rel": "bookmark"},
									{"href": "http://foo:123/bar/images/987", "rel": "self"}
								]
				resp["status"] = "ACTIVE"
				resp["created"] = datetime.datetime.now().isoformat()
				resp["updated"] = None
			self.response.body = json.dumps(resp)
		if method == "GET":
			resp = None
			if url == "http://foo:123/bar/foo":
				resp = {"foos": [
							{"name": "foo1", "id": "id1", "links": [
								{"href": "http://foo:123/bar/foo/id1", "type": "application/xml", "rel": "bookmark"},
								{"href": "http://foo:123/bar/foo/id1", "type": "application/json", "rel": "bookmark"},
								{"href": "http://foo:123/bar/foo/id1", "rel": "self"}]
							},
							{"name": "foo2", "id": "id2", "links": [
									{"href": "http://foo:123/bar/foo/id2", "type": "application/xml", "rel": "bookmark"},
									{"href": "http://foo:123/bar/foo/id2", "type": "application/json", "rel": "bookmark"},
									{"href": "http://foo:123/bar/foo/id2", "rel": "self"}]
							}]
						}
			if url == "http://foo:123/bar/foo/2468":
				resp = {"foo": 	{	"name": "foo2468", 
									"id": 2468,
									"status": "ACTIVE", 
									"hostId": "foo_bar_host", 
									"addresses": {
										"public": [	{	"version": 4, "addr": "1.2.3.4"},
													{	"version": 4, "addr": "5.6.7.8"}],
										"private": [{	"version": 4, "addr": "10.0.0.1"},
													{	"version": 4, "addr": "192.168.123.234"}]},
									"links": [
										{"href": "http://foo:123/bar/foo/2468", "type": "application/xml", "rel": "bookmark"},
										{"href": "http://foo:123/bar/foo/2468", "type": "application/json", "rel": "bookmark"},
										{"href": "http://foo:123/bar/foo/2468", "rel": "self"}]
								}
						}
			if url == "http://foo:345/bar/image/123":
				resp = {"image": 	{	"name": "image123", 
										"id": 123,
										"status": "ACTIVE",
										"created": None,
										"updated": None,
										"links": [
											{"href": "http://foo:345/bar/image/123", "type": "application/xml", "rel": "bookmark"},
											{"href": "http://foo:345/bar/image/123", "type": "application/json", "rel": "bookmark"},
											{"href": "http://foo:345/bar/image/123", "rel": "self"}]
									}
						}
			self.response.body = json.dumps(resp)
	
	def getresponse(self):
		return self.response


