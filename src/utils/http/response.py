class Response(object):
	def __init__(self, http_response):
		self.headers = http_response.getheaders()
		self.status = http_response.status
		self.message = http_response.reason
		self.protocol = http_response.version
		self.body = http_response.read()

	def __repr__(self):
		"""docstring for __repr__"""
		return "STATUS (reason) : %s (%s)\nHEADERS : %s\nBODY : %s" % (self.status, self.message, self.headers, self.body)