import service.connectionservice
import service.modelservice

class NovaClient(object):
	"""docstring for NovaClient"""
	def __init__(self, url, user, key):
		super(NovaClient, self).__init__()
		self.url = url
		self.user = user
		self.key = key
		self.connection = service.connectionservice.ConnectionService(url, user, key)
		self.service_mapping = {}
		self.service_mapping['instance'] = service.modelservice.InstanceService(self)
		self.service_mapping['image'] =  service.modelservice.ImageService(self)
		self.service_mapping['flavor'] = service.modelservice.FlavorService(self)
	
	def handle_request(self, item, action, data=(), debug=False):
		try:
			service = self.service_mapping[item]
			method = getattr(service, action)
		except KeyError:
			raise Exception("""Unknown item type '%s'\nPossible types :\n %s""" % (item, "\n ".join(self.service_mapping.keys())))
		except AttributeError:
			raise Exception("""Unknown action '%s' for type '%s'\nPossible actions :\n %s""" % (action, item, "\n ".join(service.get_actions())))
		response = None
		if len(data) > 0:
			response = method(data, debug)
		else:
			response = method(debug)
		return response
	
