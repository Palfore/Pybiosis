from os.path import join
import importlib
import glob
import os

def import_from_path(module):
	module = module.replace('\\', '.').lstrip('.')
	module = module.rpartition('.py')[0]
	module = importlib.import_module(module)
	return module

def get_user_modules():
	project_modules = glob.glob(join(os.environ.get('PYBIOSIS_USER_PATH'), "**/*.py"), recursive=True)
	project_modules = [m.replace(os.environ.get('PYBIOSIS_USER_PATH'), '') for m in project_modules if __file__ not in m]
	return project_modules

def load_user_modules():
	for module in get_user_modules():
		import_from_path(module)