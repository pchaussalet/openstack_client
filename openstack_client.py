#!/usr/bin/env python
# encoding: utf-8
"""
openstack-client.py

Created by Pierre Chaussalet on 2011-07-22.
"""
import cmd
import sys, os.path
cmd_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if cmd_folder not in sys.path:
	sys.path.insert(0, cmd_folder)
import nova

def main(argv):
	if len(argv) > 1:
		client = nova.NovaClient("http://172.241.0.101:8774/v1.1", "arthur", "bb56bda2-ae7f-42b5-9d89-5c7ddbdc2129")
		if argv[1] == "TEST":
			items = client.handle_request("scaling", "create_pool", ("test_pool", "http://172.241.0.101:8774/v1.1/images/288248559", "http://172.241.0.101:8774/v1.1/flavors/0"))
		else:
			items = client.handle_request(*argv[1:])
		if isinstance(items, list):
			items.sort()
			for item in items:
				print item
		else:
			print items
	prompt = ClientPrompt(client)
	prompt.cmdloop()

class CmdPrompt(cmd.Cmd):
	def __init__(self, prompt="(Cmd)"):
		cmd.Cmd.__init__(self)
		self.prompt = "%s# " % prompt
		
	def do_quit(self, line):
		"""Exit"""
		return True

class ClientPrompt(CmdPrompt):
	def __init__(self, client=None):
		CmdPrompt.__init__(self, "OsC")
		self.client = client
		if self.client == None:
			self.client = nova.NovaClient("http://172.241.0.101:8774/v1.1", "arthur", "bb56bda2-ae7f-42b5-9d89-5c7ddbdc2129")
	
	def do_instance(self, line):
		prompt = InstancePrompt(self.prompt[:-2], self, line)
		prompt.cmdloop()
	
	def do_image(self, line):
		prompt = ImagePrompt(self.prompt[:-2], self, line)
		prompt.cmdloop()
	
	def do_flavor(self, line):
		prompt = FlavorPrompt(self.prompt[:-2], self, line)
		prompt.cmdloop()
		
	def do_scaling(self, line):
		prompt = ScalingPrompt(self.prompt[:-2], self, line)
		prompt.cmdloop()
	

class ServicePrompt(CmdPrompt):
	def __init__(self, prompt, parent, line):
		CmdPrompt.__init__(self, "%s.%s" % (prompt, self.service))
		self.parent = parent
		self.exit = line != ""
		if self.exit:
			self.onecmd(line)
	
	def cmdloop(self):
		if self.exit:
			return
		CmdPrompt.cmdloop(self)
	

class ModelPrompt(ServicePrompt):
	def do_list(self, line):
		items = self.parent.client.handle_request(self.service, "list")
		items.sort()
		print items
		for item in items:
			print item
	
	def do_get(self, line):
		item = self.parent.client.handle_request(self.service, "get", line)
		print item
	

class InstancePrompt(ModelPrompt):
	service = "instance"
	def do_create(self, line):
		prompt = CreationPrompt(self.parent, "instance", ("name", "imageRef", "flavorRef"))
		print prompt.cmdloop()
	

class ImagePrompt(ModelPrompt):
	service = "image"
	def do_create(self, line):
		prompt = CreationPrompt(self.parent, "image", ("instanceId",), ("name",))
		prompt.cmdloop()
	
class FlavorPrompt(ModelPrompt):
	service = "flavor"

class ScalingPrompt(ModelPrompt):
	service = "scaling"

class CreationPrompt(CmdPrompt):
	"""docstring for CreationPrompt"""
	def __init__(self, parent, item_type, mandatories, optionals=()):
		CmdPrompt.__init__(self, item_type)
		self.parent = parent
		self.item_type = item_type
		if "name" not in mandatories and "name" not in optionals:
			optionals = list(optionals)
			optionals.append("name")
		self.params = (mandatories, optionals)
		self.values = {}
		self.pos = [-1,-1]
		self.param_name = ""
		self.steps = ("mandatory", "optional", "validation", "restart")
		self.step = -1
		self._next_param()

	def cmdloop(self):
		self.items = []
		CmdPrompt.cmdloop(self)
		return self.items

	def _next_param(self):
		old_pos = self.pos
		params_count = map(len, self.params)
		print params_count
		print self.pos
		self.pos[1] += 1
		print self.pos
		if self.pos[0] < 0 or self.pos[1] >= params_count[0]:
			self.step += 1
			self.pos[1] = 0
			print self.pos
			self.pos[0] += 1
			print self.pos
			if self.pos[0] >= 1:
				self.step += 1
				return False
		self.param_name = self.params[self.pos[0]][self.pos[1]]
		self.prompt = "%s %s (%s) ? " % (self.item_type, self.param_name, self.step)
		return True
	
	def do_validate(self, line):
		mandatories, optionals = self.params
		print "Creation parameters :"
		print self.values
		for param in mandatories:
			print "\t%s : %s" % (param, self.values[param])
		for param in optionals:
			if self.values[param]:
				print "\t%s : %s" % (param, self.values[param])
		self.prompt = "Is this valid ? [Y/n] "
	
	def do_y(self, line):
		print self.step
		if self.step == 2:
			print "Creating %s..." % (self.item_type,)
			service = self.parent.client.service_mapping[self.item_type]
			item = service.get_new_item(self.values["name"])
			item, password = service.create(item)
			self.items.append((item, password))
			return True
		elif self.step == 3:
			self.values = {}
			self.pos = [-1,-1]
			self.step = -1
			self._next_param()
		return False

	def do_n(self, line):
		if self.step == 2:
			self.prompt = "Do you want to restart creation process ? [y/N]"
			self.step += 1
		elif self.step == 3:
			return True

	def default(self, line):
		if line:
			self.values[self.param_name] = line
		if not self._next_param():
			self.do_validate(None)
		
	
	def emptyline(self):
		if self.step == 2:
			self.default(None)
			
			


if __name__ == '__main__':
	main(sys.argv)

