import urlparse
import httplib
import json

from pprint import pprint

import utils.http.response
import model
import service.modelservice

class ConnectionService(object):
	def __init__(self, url, user, key):
		self.url = url
		self.user = user
		self.key = key
		self.host, self.port = self._extract_endpoint(url)
	
	def _extract_endpoint(self, url):
		url_data = urlparse.urlsplit(url)
		return (url_data.hostname, url_data.port)
	
	def authenticate(self):
		conn = httplib.HTTPConnection(self.host, self.port)
		conn.request("POST", self.url, None, {"X-Auth-User": self.user, "X-Auth-Key": self.key})
		resp = conn.getresponse()
		self.auth_token = {"X-Auth-Token": resp.getheader("X-Auth-Token")}
		resp.read()
	
	def _send_request(self, path, method="GET", data=None):
		if not hasattr(self, 'auth_token'):
			self.authenticate()
		host = self.host
		port = self.port
		req_path = "/".join((self.url, path))
		if urlparse.urlsplit(path).scheme != "":
			host, port = self._extract_endpoint(path)
			req_path = path
		conn = httplib.HTTPConnection(host, port)
		headers = self.auth_token
		headers["Content-type"] = "application/json"
		headers["Accept"] = "application/json"
		conn.request(method, req_path, data, headers)
		return utils.http.response.Response(conn.getresponse())
	
