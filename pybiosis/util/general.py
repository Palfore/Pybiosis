""" This module provides general utilities. """

import os
import importlib.util
from pathlib import Path

class ChangeDir:
	""" Provide a context manager to temporarily change directories. """

	def __init__(self, new_dir):
		self.new_dir = new_dir
		self.saved_dir = os.getcwd()

	def __enter__(self):
		os.chdir(self.new_dir)

	def __exit__(self, exc_type, exc_value, traceback):
		os.chdir(self.saved_dir)


def import_module(module_path):
	""" Imports a module given the file path. """
	module_path = Path(module_path)
	module_name = module_path.stem
	spec = importlib.util.spec_from_file_location(module_name, module_path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module
