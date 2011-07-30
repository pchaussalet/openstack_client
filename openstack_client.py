#!/usr/bin/env python
# encoding: utf-8
"""
openstack-client.py

Created by Pierre Chaussalet on 2011-07-22.
"""

def main(argv):
	import nova
	client = nova.NovaClient("http://172.241.0.101:8774/v1.1", "arthur", "bb56bda2-ae7f-42b5-9d89-5c7ddbdc2129")
	items = client.handle_request(argv[1], argv[2])
	print items

if __name__ == '__main__':
	import sys, os.path
	cmd_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
	if cmd_folder not in sys.path:
		sys.path.insert(0, cmd_folder)
	main(sys.argv)

