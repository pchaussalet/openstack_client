import urlparse
import httplib
import json

from pprint import pprint

import utils.http.response
import model
import service.modelservice

class ConnectionService(object):
	def __init__(self, url, user, key):
		self.url = url[-1] == "/" and url[:-1] or url
		self.user = user
		self.key = key
		self.host, self.port = self._extract_endpoint(url)
	
	def _extract_endpoint(self, url):
		url_data = urlparse.urlsplit(url)
		if not url_data.hostname:
			raise Exception("Unable to parse url : '%s'" % (url,))
		port = url_data.port
		if not port:
			port = url_data.scheme == "https" and 443 or 80
		return (url_data.hostname, port)
	
	def authenticate(self):
		self.conn = self.conn or httplib.HTTPConnection(self.host, self.port)
		self.conn.request("POST", self.url, None, {"X-Auth-User": self.user, "X-Auth-Key": self.key})
		resp = self.conn.getresponse()
		self.auth_token = {"X-Auth-Token": resp.getheader("X-Auth-Token")}
		resp.read()
		self.conn = None
	
	def _send_request(self, path, method="GET", data=None):
		if not hasattr(self, 'auth_token'):
			self.authenticate()
		host = self.host
		port = self.port
		if urlparse.urlsplit(path).scheme != "":
			host, port = self._extract_endpoint(path)
			req_path = path
		else:
			if path[0] == "/":
				path = path[1:]
			req_path = "/".join((self.url, path))
		self.conn = self.conn or httplib.HTTPConnection(host, port)
		headers = self.auth_token
		headers["Content-type"] = "application/json"
		headers["Accept"] = "application/json"
		self.conn.request(method, req_path, data, headers)
		return utils.http.response.Response(self.conn.getresponse())
	
