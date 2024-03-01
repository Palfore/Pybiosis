""" This file implements the CLI. 

For functionality, see `pybiosis.commands`.
"""
from pybiosis.compilers.cli import CommandFramework
from rich import print
import pybiosis.commands as commands
import pybiosis.util.general as general
import pybiosis.loader as loader
import pybiosis
import atexit
import sys

START_MSG = f"🟢 Starting the Pybiosis CLI."
STOP_MSG = f"🔴 Stopping the Pybiosis CLI."

class Commands(CommandFramework):
	CONFIG_VARIABLES = ['user_path']

	def add_run(self, setup, args, unknown_args):
		""" Run and search for functions to run. """

		with general.ChangeDir(loader.get_user_path()):
			pybiosis.load()
			_, cmds = commands.RunHelper.load_data()

		if setup:
			setup.add_argument('-r', '--run', choices=sorted(list(cmds)), help='Run a command')
			setup.add_argument('-l', '--list', nargs='*', help='List the subhierarchy.')
			setup.add_argument('-d', '--depth', nargs='?', default=None, type=int, help='Limit the depths of the hierarchy, starting at 1.')
			return

		print(f"🏃 Running the [green]RUN[/green] command.")
		commands.call_run(args, unknown_args)

	def add_compile(self, setup, args):
		""" This compiles the Pybiosis functions. """
		if setup:
			return
		
		print(f"🛠️ Running the [green]COMPILE[/green] command.")
		commands.call_compile(args, None)
		
	def add_user(self, setup, args, unknown_args):
		""" This calls the user's driver.py module. """
		if setup:
			return

		print("👨 Running the [green]USER[/green] command.")
		commands.call_user(args, unknown_args)

	def add_config(self, setup, args):
		""" Access the config functionality. """
		if setup:
			setup.add_argument('-l', '--list', action='store_true', help='List the config variables.')
			setup.add_argument('-s', '--set', nargs='*', help='Set key-value pairs.')
			setup.add_argument('-i', '--interactive', action='store_true', help='Interactively set key-value pairs.')
			return

		print("⚙️ Running the [green]CONFIG[/green] command.")
		commands.call_config(args, None, config_variables=self.CONFIG_VARIABLES)


def main():
	atexit.register(lambda: print(STOP_MSG))
	print(START_MSG)
	Commands.run_cli(sys.argv)

if __name__ == '__main__':
	main()
