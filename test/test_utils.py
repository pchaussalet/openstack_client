import os
import sys

abs_path = os.path.abspath(__file__)
dir_name = os.path.dirname(abs_path)
while "src" not in os.listdir(dir_name):
	dir_name = os.path.dirname(dir_name)
cmd_folder = os.path.join(dir_name, "src")
if cmd_folder not in sys.path:
	sys.path.insert(0, cmd_folder)

cmd_folder = os.path.join(dir_name, "test")
if cmd_folder not in sys.path:
	sys.path.insert(0, cmd_folder)

