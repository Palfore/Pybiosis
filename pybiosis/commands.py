""" This file implements the functionality of the CLI. """
from pathlib import Path
from pybiosis.util.config import ConfigurationManager
import pybiosis.util.general as general
import pybiosis.loader as loader
import pybiosis.core as pybiosis
import subprocess
import argparse
import sys
import os


class RunHelper:
	""" Methods to help with the `run()` function. """

	@classmethod
	def load_data(cls):
		data = {}
		for i, command in enumerate(pybiosis.Device.FUNCTIONS):
			decorator, end_call = command
			module_path = f"{Path() / end_call.__module__.replace('.', os.sep)}.py"

			# Create a nested json structure
			directories = module_path.split(os.sep)
			nested_dict = data
			for directory in directories[:-1]:  # Exclude the file name
				nested_dict = nested_dict.setdefault(directory, {})

			# Add the file name to the nested dictionary
			if directories[-1] not in nested_dict:
				nested_dict[directories[-1]] = []

			# Add the function to the list of functions.
			nested_dict[directories[-1]].append(
				cls.Info(name=end_call.__name__, title=end_call.title, description=end_call.description),
			)

		all_commands = {}
		RunHelper.populate_all_commands(all_commands, data)
		return data, all_commands

	@classmethod
	def populate_all_commands(cls, all_commands, info, current_path=""):
		# all_commands is modified in-place.
	    for key, value in info.items():
	        key = key.replace(".py", "")
	        if isinstance(value, list):
	            for item in value:
	                full_identifier = current_path + "." + key + "." + item.name
	                # Remove leading dot
	                full_identifier = full_identifier[1:]
	                # print(full_identifier)
	                all_commands[full_identifier] = item
	        elif isinstance(value, dict):
	            cls.populate_all_commands(all_commands, value, current_path + "." + key)

	@staticmethod
	def truncate(name, depth=None):
		chunks = name.split('.')
		if depth is None:
			depth = len(chunks)
		return '.'.join(chunks[:min(len(chunks), depth)])

	@classmethod
	def call_function_by_dot_syntax(cls, identifier: str):
		if not identifier:
			raise ValueError("You did not supply an function to call.")
		module, function_name = identifier.rsplit('.', 1)
		module = general.import_module(module.replace('.', os.sep) + '.py')  # We are in the user_path.
		function = getattr(module, function_name)
		function()

	class Info:
		def __init__(self, name, title, description):
			self.name = name
			self.title = title
			self.description = description


def call_run(args, unknown_args):
	data, cmds = RunHelper.load_data()
	
	with general.ChangeDir(loader.get_user_path()):
		match args:
			# For `list`:
			case argparse.Namespace(list=[]):  # list everything
				print("Listing Everything")
				for command in sorted(list(set([RunHelper.truncate(name, args.depth) for name, c in cmds.items()]))):
					print(command)

			case argparse.Namespace(list=[identifier]):  # list given dot-syntax identifier
				print("Listing by Dot-Syntax:", identifier)
				levels = identifier.split('.')

				matches = []
				for command in sorted(list(set([RunHelper.truncate(name, args.depth) for name, c in cmds.items()]))):
					if identifier in ('""', "''"):
						matches.append(command)
					else:
						# Exact matching for everything except for the last one, which uses .startswith().
						comps = list(zip(levels, command.split('.')))
						*top, (ending_level, ending_command) = comps
						if all(x == y for x, y in top) and (ending_command.startswith(ending_level)):  # Starts with the right prefix.
							matches.append(command)
				
				if not matches:
					print(f"There were no matches for: {identifier}")
					return
				
				for match in matches:
					print(match)

			case argparse.Namespace(list=[identifier, *others]):  # Invalid, multiple identifiers
				raise ValueError(f"Multiple values of --list specified, must only be one (use dot-syntax): {args.list}")

			# Handle unused depth parameter after failing to register as a --list command.
			case argparse.Namespace(depth=int()):
				raise ValueError("Can't use depth flag outside of --list (-l).")

			# For `run identifier`:
			case argparse.Namespace(run=identifier) if not unknown_args:
				if identifier:
					print("Calling:", identifier)
					RunHelper.call_function_by_dot_syntax(identifier)
				else:
					print("No identifier was provided, so no command was run. You can use `--help` for more on the `run` command.")

			case _:
				print(f"Command to be executed: {args} {unknown_args}")
				match unknown_args:
					case [identifier]:
						print("Calling:", identifier)
						RunHelper.call_function_by_dot_syntax(identifier)
					case _:
						raise ValueError("Can't use `call` without identifier. Use `python -m pybiosis call identifier.name`.")

def call_compile(args, unknown_args):
	with general.ChangeDir(loader.get_user_path()):
		pybiosis.load()
		pybiosis.Device.compile_all()


def call_user(gui, wait, args, unknown_args):
	command_list = [sys.executable, 'driver.py'] + unknown_args
	if gui:
		subprocess.Popen(command_list, cwd=loader.get_user_path(),
			start_new_session=True,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,			
		)
	else:
		process = subprocess.Popen(command_list, cwd=loader.get_user_path())
	
	if wait:
		process.wait()


def call_config(args, unknown_args, config_variables):
	manager = ConfigurationManager(loader.get_config_path(), config_variables=config_variables)
	manager.dispatch(args)
	
def call_gui(args, unknown_args):
	module = Path(__file__).parent / 'compilers' / 'gui.py'
	os.system(f"{sys.executable} -m streamlit run {module}")
