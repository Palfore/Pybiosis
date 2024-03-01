R""" Provides a decorator and wrapper for the Windows Scheduler.

	A scheduled task is created by creating a batch file which runs a command launching the specified python function.
	The batch file then gets scheduled to run on the Windows Scheduler using schtasks.exe.

	See https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create for more details.
		Important: sc, mo, sd/st, ed/et, /d, /m

		/sc minute /mo 20  # run every 20 minutes
		/sc minute /mo 100 /st 17:00 /et 08:00  # every 100 minutes between 5:00 P.M. and 7:59 A.M. each day, 
		/sc hourly /mo 5 /sd 03/01/2002  # every five hours, beginning on the first day of March 2002
		/sc hourly /st 00:05  # hourly, beginning at five minutes past midnight

		/sc daily /st 08:00 /ed 31/12/2021  # once a day, every day, at 8:00 A.M. until December 31, 2021
		/sc daily /mo 12 /sd 12/31/2002 /st 13:00 # every twelve days at 1:00 P.M. (13:00) beginning on December 31, 2021
		/sc daily /mo 70  #  every 70 days

		/sc weekly /mo 6  #  every six weeks
		/sc weekly /mo 2 /d FRI  # every other Friday
		/sc weekly /d WED  # every week on Wednesday
		/sc weekly /mo 8 /d MON,FRI # Monday and Friday of every eighth week

		/sc monthly
		/sc monthly /mo 3
		/sc monthly /mo 2 /d 21 /st 00:00 /sd 2002/07/01 /ed 2003/06/30  #  every other month 21st day of the month at midnight for a year, from July 2, 2002 to June 30, 2003
		/sc monthly /mo SECOND /d SUN  # second Sunday of every month
		/sc monthly /mo FIRST /d MON /m MAR,SEP  # first Monday in March and September
		/sc monthly /d 15 /m MAY,JUN /st 15:00  # May 15 and June 15 at 3:00 P.M. (15:00)


		/sc monthly /mo lastday /m *  # last day of every month
		/sc monthly /mo lastday /m FEB,MAR /st 18:00  # /sc monthly /mo lastday /m FEB,MAR /st 18:00

		/sc once /sd 01/01/2003 /st 00:00
		/sc onstart /sd 03/15/2001
		/sc onlogon
		/sc onidle /i 10
"""

import pybiosis.validate as validate
from pybiosis import PRINTING_COLORS, Device, print_function_header
from pybiosis.utility import command, save_function
from pybiosis.loader import get_user_path
from pathlib import Path
from io import StringIO
import datetime as dt
import subprocess
import inspect
import glob
import os


class Scheduler(Device):
	""" A decorator that allows a function to be scheduled.
		See: https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create
	"""
	EXE = "schtasks"
	HEADERS = ['values']
	TASKNAME_PREFIX = "PYBIOSIS_"

	@classmethod
	@property
	def TEMP_PATH(self):
		return get_user_path() / '.compilers/scheduler'

	def __init__(self, trigger, modifier=None, start=None, end=None, day=None, month=None, idle=None):
		self.values = locals()
		del self.values['self']

	def __call__(self, func):
		func = super().__call__(func)
		return self.__end_call__(Scheduler, self, func)

	@staticmethod
	def compile(functions):
		validate.require_windows()
		Scheduler.clear()		
		print(PRINTING_COLORS.device + f'\t{Scheduler.__name__}: {len(functions)} Function(s)')
		for i, f in enumerate(functions):
			# Print
			print_function_header(f, i)
			for k, v in f.values.items():
				print(PRINTING_COLORS.key+f'\t\t\t{k.title()}:', v)
			print()

			# Process
			module_name = inspect.getmodule(f).__name__
			function_name = f.name
			file = save_function(Scheduler.TEMP_PATH, f.__name__+'_'+str(id(f)), Rf'''cd /d {get_user_path()} && python -c "import {module_name}; {module_name}.{function_name}();"''', f=f)
			failure = Scheduler.create(function_name, file, **f.values)
			if failure:
				raise ValueError(function_name + " failed with " + failure)

	@staticmethod
	def get_tasks(custom=False):
		""" Returns a list of scheduled tasks. """
		# import pandas
		# o = command([Scheduler.EXE, '/query', '/fo', 'CSV', '/nh'])
		# names = pandas.read_csv(StringIO(o)).iloc[:,0].to_list()
		# if custom:
		# 	return [n for n in names if n.startswith('\\'+Scheduler.TASKNAME_PREFIX)]
		# else:
		# 	return names


		# command_output = subprocess.run(['Scheduler.EXE', '/query', '/fo', 'CSV', '/nh'], capture_output=True, text=True)
		command_output = subprocess.run(['schtasks.exe', '/query', '/fo', 'CSV', '/nh'], capture_output=True, text=True)
		output_lines = command_output.stdout.strip().split('\n')
		names = [line.split(',')[0] for line in output_lines]
		if custom:
			return [n for n in names if n.startswith('\\' + Scheduler.TASKNAME_PREFIX)]
		else:
			return names

	@staticmethod
	def clear():
		""" Deletes all custom tasks. """
		
		# Remove from task scheduler
		try:
			for task in Scheduler.get_tasks(custom=True):
				command([Scheduler.EXE, '/delete', '/f', '/tn', task])		
		except ValueError as e:
			if str(e).startswith('ERROR: Access is denied.'):
				raise PermissionError("Tasks cannot be cleared. Please compile with administrative privileges.")
			raise

		# Remove batch files
		for f in glob.glob(str(Scheduler.TEMP_PATH / '*')):
			os.remove(f)
		
	@staticmethod
	def create(name, action, trigger, modifier, start, end, day, month, idle):
		R""" Schedules a command to execute according to the schedule.
			trigger: minute, hourly, daily, monthly, once/onstart/onlogon/(onidle with \i #)
			modifier: sc amount (#)
				monthly: lastday, (FIRST, SECOND, THIRD, FOURTH along with the /d <day> parameter)
			day: MON etc or #
			month: FEB etc or *
			st/sd and et/ed: yyyy/MM/dd-hh:mm
		
			eg:
				Every other month 21st day of the month at midnight for a year, from July 2, 2002 to June 30, 2003
				/sc monthly /mo 2 /d 21 /st 00:00 /sd 2002/07/01 /ed 2003/06/30
				create("test_task", R'C:\Program Files\Internet Explorer\iexplore.exe'
					'monthly', 2, '2002/07/01-00:00', day=21
				)

			Returns if there was a failure.
		"""
		arguments = [Scheduler.EXE,
			'/create',
			'/tn', 'PYBIOSIS_'+name,
			'/tr', action,
			'/f',
			# '/z'  # Doesn't seem to work
		]
		if start:
			if start == 'now':  # This may need more work...
				delay = 2  # minutes
				start_date, start_time = dt.datetime.today().strftime("%Y/%m/%d-%H:%M").split('-')
				h, m = start_time.split(':')

				# Increment to the next hour if the delay means the there are more than 60 minutes.
				h = h if int(m) + delay < 60 else h + 1
				m = max(int(m) + delay, 59)

				start_time = f'{h}:{m:02}'
			elif '-' in start:
				start_date, start_time = start.split('-')
			else:
				start_date, start_time = start, None
		else:
			start_date, start_time = None, None

		if end:
			if '-' in end:
				end_date, end_time = end.split('-')
			else:
				end_date, end_time = end, None
		else:
			end_date, end_time = None, None

		flags = {
			'/sc': trigger,
			'/mo': modifier,
			'/sd': start_date,
			'/st': start_time,
			'/ed': end_date,
			'/et': end_time,
			'/m': month,
			'/d': day,
			'/i': idle,
		}
		for flag, value in flags.items():
			if value is not None:
				arguments.extend([flag, str(value)])
		try:
			response = command(arguments)
			if response.startswith('SUCCESS'):
				return False
		except Exception as e:
			return str(e).strip()


