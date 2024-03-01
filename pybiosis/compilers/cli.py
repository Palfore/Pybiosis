""" Implements a class to create a GUI and Terminal CLI interface from a subclass. """

from pybiosis.__version__ import __version__
from rich_argparse import RichHelpFormatter
from gooey import Gooey, GooeyParser
from datetime import datetime
from pathlib import Path
from pybiosis.util.config import ConfigurationManager
import argparse
import platform
import logging
import sys


def play_notification_sound():
	try:
		import winsound
		winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
	except:
		pass

class CommandFramework:
	""" Subclass this class, and create 'add_*' named methods to register them as commands. 
	
	The function must take: self, setup, args.
	The function may take: unknown_args.
	Here is an example:

	```python
	def add_my_new_command(self, setup, args, unknown_args):
		if setup:
			setup.add_argument(...)
			return

		pass # Perform function using args, and potentially unknown_args.
	```
	"""

	PROGRAM_NAME: str = "Welcome"
	DESCRIPTION: str = "Here you can access the functionality of the CLI."
	COMMAND_VARIABLE_NAME: str = "cmd"
	METHOD_PREFIX: str = 'add_'

	HEADER: str = 50 * "-"
	CMD_START: callable = lambda self, args: f"⚡ CLI Executing Command: {args.cmd} with args {args}\n{self.HEADER}"
	CMD_END: callable = lambda self, args: f"{self.HEADER}\n👋 Thanks for Running Your Command!"
	GOOEY_DESCRIPTION_WORKAROUND: str = "|--------------------|"
	CONFIG = ConfigurationManager()


	@classmethod
	@property
	def DEFAULT_MENU(cls):
		return [
			{
				'name': 'File',
				'items': [{
			        'type': 'AboutDialog',
			        'menuTitle': 'About',
			        'name': 'Pybiosis Graphical Interface',
			        'description': 'Access to all your pybiosis functions!',
			        'version': f"v{__version__}",
			        'copyright': f"Python {sys.version.split()[0]} - {platform.system()} - ©️{str(datetime.now().year)}",
			        'website': 'https://github.com/Palfore/Pybiosis/tree/main',
			        'developer': 'Palfore.com',
			        'license': 'MIT'
			    }, {
			        'type': 'MessageDialog',
			        'menuTitle': 'Information',
			        'caption': 'Overview',
			        'message': 'Here, you can access Pybiosis functions, and your user functions.'
			    }, {
			        'type': 'Link',
			        'menuTitle': 'Visit Our Site',
			        'url': 'https://github.com/Palfore/Pybiosis/tree/main'
			    }]
			}, {
				'name': 'Open',
				'items': ([{
						    'type': 'Link',
						    'menuTitle': 'Driver',
						    'url': fR"file://{Path(cls.CONFIG.get('user_path')) / 'driver.py'}",
						}] if cls.CONFIG.has('user_path') else []) + [
						{
						    'type': 'Link',
						    'menuTitle': 'Config',
						    'url': fR"file://{Path(__file__).parent.parent / '.config.json'}",
						},
						{
						    'type': 'Link',
						    'menuTitle': 'Library',
						    'url': fR'file://{Path(__file__).parent.parent}',
						},
					]
			}, {
				'name': 'Help',
				'items': [{
				    'type': 'Link',
				    'menuTitle': 'Documentation',
				    'url': 'https://github.com/Palfore/Pybiosis/tree/main'
				}]
			}
		]

	def build(self, gui: bool=False) -> dict:
		""" Attaches all the commands to the CLI.

		Register a command by creating a method starting with "add_".
		It must accept (self, setup, args). 
		The name in add_name is used as the command name in the CLI.
		The description is taken from the Doc string of the function if it exists.

		If setup: Use add_argument as needed.
		Else (or if args): Implement the function to execute.
		"""
		self.subparsers = self.parser.add_subparsers(title="Commands", dest=self.COMMAND_VARIABLE_NAME)
		for method_name in dir(self):
			if method_name.startswith(self.METHOD_PREFIX):
				# Get the command name from the function name,
				# Create the new parser with that.
				command_name = method_name[len(self.METHOD_PREFIX):]
				parser = self.subparsers.add_parser(command_name, formatter_class=self.parser.formatter_class)

				# Get the method, and it's docstring,
				# Add a description arg with it as description.
				# For some reason, the help text doesn't appear normally, so this is a hack.
				method = getattr(self, method_name)
				if gui and hasattr(method, '__doc__') and method.__doc__:
					parser.add_argument('DESCRIPTION', default=self.GOOEY_DESCRIPTION_WORKAROUND, help=method.__doc__)  # Adhoc way of adding command description, while it seems bugged.

				logging.debug(f"Setting up new command: {command_name}")
				method(setup=parser, args=None)

		if gui:
			return self.parser.parse_args()
		return self.parser.parse_known_args()
		
	def dispatch(self, args, unknown_args=None) -> None:
		""" This method dispatches to the correct CLI command based on the args.cmd value.

		It assumes that since it is calling the methods with parser=None, that the method
		will execute their intended logic (not the setup aspect).

		add_ functions must take 'setup', 'args'; and optionally 'unknown_args'.
		"""
		assert args, f"Args should exist as a Namespace, but doesn't? {args}"
		
		# Preprocess unknown_args, which gets 'auxiliary' elements that need filtering.
		if '--' in unknown_args:
			unknown_args.remove('--')
		if self.GOOEY_DESCRIPTION_WORKAROUND in unknown_args:
			unknown_args.remove(self.GOOEY_DESCRIPTION_WORKAROUND)

		# Dispatch
		print("🚚 Dispatching:", args, unknown_args)
		if args.cmd:
			method_name = self.METHOD_PREFIX + args.cmd
			if hasattr(self, method_name):
				print(self.CMD_START(args))
				method = getattr(self, method_name)
				method(setup=None, args=args, unknown_args=unknown_args)
				print(self.CMD_END(args))
				if not self.CONFIG.get('no-notify'):  # No beep with `--set no-notify True`; beep with `--set no-notify`.
					play_notification_sound()
			else:
				print(f"Invalid Method Name: {method_name}")
		else:
			print("Didn't specify a command. This should have launched the GUI CLI?")

	@classmethod
	def run_cli(cls, args, menu=None) -> None:
		""" This function is called as a cli, where args is sys.argv.
		
		It either launches a CLI, or a GUI CLI (made using `gooey`), depending on if a command was specified.
		"""
		if menu is None:
			menu = cls.DEFAULT_MENU

		# Define the GUI CLI
		@Gooey(
			python_executable=sys.executable,
			program_name=cls.PROGRAM_NAME,
			default_size=(1000, 700),
			clear_before_run=True,
			image_dir=Path(__file__).parent.parent / 'images',
			menu=menu,
			fullscreen=False,
			show_success_modal=False,
			sidebar_title="Commands",
			show_stop_warning=False,
			# richtext_controls=True,  # Seems to fail, would be nice.
        )
		class GUI_CLI(cls):
			def __init__(self):
				self.parser = GooeyParser(description=cls.DESCRIPTION, add_help=True)

		# Define the Terminal CLI
		class CLI(cls):
			def __init__(self):
				self.parser = argparse.ArgumentParser(description=f"{cls.PROGRAM_NAME}!\n{cls.DESCRIPTION}", formatter_class=RichHelpFormatter)

		# Dispatch to the right CLI type, and further dispatch the function call.
		if gui := len(args) == 1:  # No actual args, just the default sys.argv[0] == pybioisis_script.
			print("🚀 Launching the CLI as a GUI (🖥️).")
			GUI_CLI().build(gui=gui)  # .build() launches the gooey GUI: self.parser.parse_args()
		else:
			print("🚀 Launching the CLI.")
			cli = CLI()
			args, unknown_args = cli.build(gui=gui)
			cli.dispatch(args, unknown_args)

