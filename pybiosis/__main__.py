""" This file implements the CLI. 

For functionality, see `pybiosis.commands`.
"""
from pybiosis.compilers.cli import CommandFramework
from pybiosis.util.config import ConfigurationManager
from pathlib import Path
from rich import print
import pybiosis.commands as commands
import pybiosis.util.general as general
import pybiosis.loader as loader
import pybiosis.core as pybiosis
import atexit
import sys

START_MSG = f"🟢 Starting the Pybiosis CLI."
STOP_MSG = f"🔴 Stopping the Pybiosis CLI."

class Commands(CommandFramework):
	CONFIG_VARIABLES = ['user_path']

	def add_run(self, setup, args, **kwargs):
		""" Run and search for functions to run. """

		manager = ConfigurationManager()
		if manager.has('user_path'):
			with general.ChangeDir(loader.get_user_path()):
				pybiosis.load()
				_, cmds = commands.RunHelper.load_data()
		else:
			cmds = []

		if setup:
			setup.add_argument('-r', '--run', choices=sorted(list(cmds)), help='Run a command')
			setup.add_argument('-l', '--list', nargs='*', help='List the subhierarchy.')
			setup.add_argument('-d', '--depth', nargs='?', default=None, type=int, help='Limit the depths of the hierarchy, starting at 1.')
			return

		print(f"🏃 Running the [green]RUN[/green] command.")
		commands.call_run(args, kwargs.get('unknown_args'))

	def add_compile(self, setup, args, **kwargs):
		""" This compiles the Pybiosis functions. """
		if setup:
			return
		
		print(f"🛠️ Running the [green]COMPILE[/green] command.")
		commands.call_compile(args, None)  # TODO: for some reason, this hangs...
		
	def add_user(self, setup, args, **kwargs):
		""" This calls the user's driver.py module. """
		# TODO: It seems like `python -m pybiosis user --help` fails. (doesn't get here)
		if setup:
			setup.add_argument('-d', '--detached', action='store_true', help="Run as a detached process [only use in GUI CLI].")
			return

		print("👨 Running the [green]USER[/green] command.")
		commands.call_user(args.detached, args, kwargs.get('unknown_args'))

	def add_config(self, setup, args, **kwargs):
		""" Access the config functionality. """
		if setup:
			setup.add_argument('-l', '--list', action='store_true', help='List the config variables.')
			setup.add_argument('-s', '--set', nargs='*', help='Set key-value pairs.')
			setup.add_argument('-i', '--interactive', action='store_true', help='Interactively set key-value pairs.')
			return

		print("⚙️ Running the [green]CONFIG[/green] command.")
		commands.call_config(args, None, config_variables=self.CONFIG_VARIABLES)

	def add_gui(self, setup, args, **kwargs):
		""" Access functionality through the GUI. """
		if setup:
			return

		print("🖥️ Running the [green]GUI[/green] command.")
		commands.call_gui(args, None)




def main():
	# On windows, we need to ensure that the executable is accessible.
	# It turns out `bb` command needs to call `bb.exe`, so we need to manually append if missing.
	# Using the existence of files makes this more robust than querying hardware.
	if not Path(sys.argv[0]).exists():
		if Path(sys.argv[0] + '.exe').exists():
			sys.argv[0] += '.exe'
	assert Path(sys.argv[0]).exists(), f"Somehow, the executable path couldn't be found: {sys.argv[0]}"

	# Run the CLI
	print(START_MSG)
	atexit.register(lambda: print(STOP_MSG))
	Commands.run_cli(sys.argv)

if __name__ == '__main__':
	main()
