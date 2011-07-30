import json

from pprint import pprint

import model

def action(function):
	function.is_action = True
	return function

class ModelService(object):
	"""Parent for all services regarding model"""
	def __init__(self, client):
		self.service_mapping = client.service_mapping
		self.connection = client.connection

	def get_actions(self):
		print self
		if not hasattr(self, 'actions'):
			self.actions = []
			for action in [function for function in dir(self) if hasattr(getattr(self, function), 'is_action')]:
				self.actions.append(action)
		self.actions.sort()
		return self.actions

	def _get_item_details(self, item_bookmark, item_name, item_class, debug=False):
		"""docstring for get_item_details"""
		if debug:
			print item_bookmark, item_name, item_class
		body = self.connection._send_request(item_bookmark).body
		if debug:
			print body
		response = json.loads(body)
		if debug:
			pprint(response)
		item = response[item_name]
		if debug:
			pprint(item)
		item = self._response_to_model(item)
		if debug:
			pprint(item)
		return item_class(item["id"], item["name"], self._extract_bookmark(item["links"]), item)
	
	def _response_to_model(self, response):
		model_types = {	"imageRef": 	("image", 	self.service_mapping['image']), 
						"serverRef": 	("server", 	self.service_mapping['instance']), 
						"flavorRef": 	("flavor", 	self.service_mapping['flavor'])}
		for key, values in model_types.items():
			new_key, service = values
			if key in response and not isinstance(response[key], model.Model):
				response[new_key] = service.get(response[key])
		return response
	
	def _extract_bookmark(self, links):
		for link in links:
			if link["rel"] == "bookmark" and link["type"] == "application/json":
				return link["href"]
		return None
	
	def _list_items(self, path, items_name, item_class, debug=False):
		response = json.loads(self.connection._send_request(path).body)
		if debug:
			pprint(response)
		items = []
		for item in response[items_name]:
			items.append(item_class(item["id"], item["name"], self._extract_bookmark(item["links"])))
		return items
	


class FlavorService(ModelService):
	"""Service for managing flavors"""
	def __init__(self, client):
		super(FlavorService, self).__init__(client)
	
	@action
	def list(self, debug=False):
		"""Returns availables flavors"""
		return self._list_items("/flavors", "flavors", model.Flavor, debug)
	
	@action
	def get(self, flavor_bookmark, debug=False):
		"""Returns details on a flavor"""
		return self._get_item_details(flavor_bookmark, "flavor", model.Flavor, debug)
	


class ImageService(ModelService):
	"""Service for managing images"""
	def __init__(self, client):
		super(ImageService, self).__init__(client)
	
	@action
	def list(self, debug=False):
		"""Returns available images"""
		return self._list_items("/images", "images", model.Image, debug)
	
	@action
	def get(self, image_bookmark, debug=False):
		"""Return details on an image"""
		return self._get_item_details(image_bookmark, "image", model.Image, debug)
	


class InstanceService(ModelService):
	"""Service for managing instances"""
	def __init__(self, client):
		super(InstanceService, self).__init__(client)
	
	@action
	def list(self, debug=False):
		"""Returns all instances"""
		return self._list_items("/servers", "servers", model.Instance, debug)
	
	@action
	def get(self, bookmark, debug=False):
		"""Returns details on an instance"""
		return self._get_item_details(bookmark, "server", model.Instance, debug)
	
	@action
	def create(self, instance, debug=False):
		"""Request creation of a new instance
		Returns the new instance"""
		response = json.loads(self.send_request("/servers", "POST", instance.to_json()).body)
		created_instance = response["server"]
		return (model.Instance(created_instance["id"], 
									created_instance["name"], 
									self._extract_bookmark(created_instance["links"]), 
									created_instance), 
				created_instance["adminPass"])
	
	@action
	def delete(self, _id, debug=False):
		"""Requests deletion of an instance"""
		self.send_request("/servers/%i" % (_id,), "DELETE")
	
	def update(self, instance):
		"""Updates instance's informations"""
		pass
	

