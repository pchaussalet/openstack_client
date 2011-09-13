import json
import urlparse
import datetime

from pprint import pprint

from service.public import *
import model

class ModelService(PublicActions):
	"""Parent for all services regarding model"""
	def __init__(self, client):
		if self.item_class == None:
			raise Exception("Cannot instanciate ModelService")
		self.service_mapping = client.service_mapping
		self.connection = client.connection
	
	def get_new_item(self, name):
		return self.item_class(None, name)
	
	def _list_items(self, items_name, item_class, debug=False):
		response = json.loads(self.connection._send_request(self.prefix).body)
		if debug:
			pprint(response)
		items = []
		for item in response[items_name]:
			items.append(item_class(item["id"], item["name"], self._extract_bookmark(item["links"])))
		return items
	
	def _get_item_details(self, item_bookmark, item_name, item_class, debug=False):
		"""docstring for get_item_details"""
		if urlparse.urlsplit(item_bookmark).scheme == "":
			item_bookmark = "/".join(("", item_class.path, item_bookmark))
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
	
	@action
	def delete(self, _id, debug=False):
		"""Requests deletion of an instance"""
		self.connection._send_request("%s/%s" % (self.prefix, _id,), "DELETE")
	


class FlavorService(ModelService):
	"""Service for managing flavors"""
	prefix = "/flavors"
	item_class = model.Flavor
	def __init__(self, client):
		super(FlavorService, self).__init__(client)
	
	@action
	def list(self, debug=False):
		"""Returns availables flavors"""
		return self._list_items("flavors", model.Flavor, debug)
	
	@action
	def get(self, flavor_bookmark, debug=False):
		"""Returns details on a flavor"""
		return self._get_item_details(flavor_bookmark, "flavor", model.Flavor, debug)
	


class ImageService(ModelService):
	"""Service for managing images"""
	prefix = "/images"
	item_class = model.Image
	def __init__(self, client):
		super(ImageService, self).__init__(client)
	
	@action
	def list(self, debug=False):
		"""Returns available images"""
		return self._list_items("images", model.Image, debug)
	
	@action
	def get(self, image_bookmark, debug=False):
		"""Return details on an image"""
		return self._get_item_details(image_bookmark, "image", model.Image, debug)
	
	@action
	def create(self, instance_id, name=None, debug=False):
		"""Requests creation of an image corresponding to the instance"""
		if not name:
			name = "%s_%s" % (instance_id, datetime.datetime.now().isoformat())
		request = {"image": 
					{	"name": name, 
						"serverId": instance_id}}
		body = json.dumps(request)
		response = json.loads(self.connection._send_request(self.prefix, "POST", body).body)
		return model.Image(response["id"], response["name"], self._extract_bookmark(response["links"]), response)
	


class InstanceService(ModelService):
	"""Service for managing instances"""
	prefix = "/servers"
	item_class = model.Instance
	def __init__(self, client):
		super(InstanceService, self).__init__(client)
	
	@action
	def list(self, debug=False):
		"""Returns all instances"""
		return self._list_items("servers", model.Instance, debug)
	
	@action
	def get(self, bookmark, debug=False):
		"""Returns details on an instance"""
		return self._get_item_details(bookmark, "server", model.Instance, debug)
	
	@action
	def create(self, instance, debug=False):
		"""Request creation of a new instance
		Returns the new instance"""
		if isinstance(instance, model.Instance):
			instance_json = instance.to_json()
		else:
			instance_dict = json.loads(instance)
			keys = instance_dict["server"].keys()
			if "name" not in keys or "imageRef" not in keys or "flavorRef" not in keys:
				raise AttributeError()
			instance_json = json.dumps(instance_dict)
		response = json.loads(self.connection._send_request(self.prefix, "POST", instance_json).body)
		created_instance = response["server"]
		return (model.Instance(created_instance["id"], 
									created_instance["name"], 
									self._extract_bookmark(created_instance["links"]), 
									created_instance), 
				created_instance["adminPass"])
	

