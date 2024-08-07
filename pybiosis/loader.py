from pybiosis.util.config import ConfigurationManager
from pathlib import Path
import pybiosis.validate as validate
import importlib
import glob
import sys
import os

def get_config_path():
	return Path(__file__).parent / '.config.json'

def get_user_path():
	if '--local' in sys.argv:
		return Path().absolute()
	
	validate.require_user_path()
	return Path(ConfigurationManager(get_config_path()).get('user_path'))

def get_user_modules():
	modules = glob.glob(os.path.join(get_user_path(), "**/*.py"), recursive=True)
	modules = [m.replace(str(get_user_path()), '') for m in modules if __file__ not in m]
	return modules

def load_user_modules():
	for module in get_user_modules():
		try:
			import_from_path(module)
		except ModuleNotFoundError as e:
			# Hmm... new streamlit dashboard in my user dir is causing an error.
			# I'm ignoring it as an exception since I dont need it to import.
			print(f"Error loading user module: {module}, {e}")

def import_from_path(module):
	module = module.replace('\\', '.')
	module = module.replace('/', '.')
	module = module.lstrip('.')
	module = module.rpartition('.py')[0]
	module = importlib.import_module(module)
	return module

def import_user_module(path):
	file_path = get_user_path() / path
	
	# Extract the module name from the file path
	module_name = str(file_path).split('/')[-1].split('.')[0]

	# # Add the directory containing the file to the system path
	# sys.path.append('/'.join(file_path.split('/')[:-1]))

	# Load the module
	spec = importlib.util.spec_from_file_location(module_name, file_path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)

	return module