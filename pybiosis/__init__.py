""" This file stores the decorator, compilers, and helper functions for the user. """

from colorama import init, Fore, Style
import pybiosis.validate as validate
from pybiosis.loader import load_user_modules, get_user_path
from pybiosis.utility import save_function
from pathlib import Path
import importlib
import inspect
import shutil
import glob
import json
import time
import sys
import os

PRINTING_COLORS = type('Colors', (object,), {
	'main': Fore.GREEN,
	'device': Fore.CYAN,
	'function': Fore.YELLOW,
	'key': Fore.RED,
})

def load():
	""" Loads the modules located in PYBIOSIS_USER_PATH. """
	load_user_modules()

def apply_list(decorators):
    """ A decorator that applies a list of decorators to a function. """
    def decorator(f):
        for d in reversed(decorators):
            f = d(f)
        return f
    return decorator

def register(g):
	""" Inner Class Unwrapping Decorator, allows for the Class Syntax.
		Used as: @register(globals())
	"""

	def inner_classes_list(cls):  # https://stackoverflow.com/questions/42326408/python-how-to-get-a-list-of-inner-classes
			return [cls_attribute for cls_attribute in cls.__dict__.values()
			           if inspect.isclass(cls_attribute) and issubclass(cls_attribute, object)]

	def get_all_inner_classes(start):
		def recur(outer):
			if outer:
				thing = [inner_classes_list(cls) for cls in outer][0]
				classes.extend(thing)
				return recur(thing)
			else:
				return classes
		classes = [start]
		return recur(classes)

	def wrapper(cls):
		# Add all inner class functions to the modules globals dict, which is passed in as g.
		for inner_class in get_all_inner_classes(cls):
			for name, func in inspect.getmembers(inner_class, predicate=inspect.isfunction):
				g[name] = func
		return cls
	return wrapper

def print_function_header(f, i):
	title = f.title.replace('\n', ' ')
	module_file = f.module.__file__.replace('\\', '/')
	print(Fore.WHITE+f'\t\t{i}) '+PRINTING_COLORS.function+f'Compiling:', f'{title} {"- " + f.description.strip() if f.description else ""}')
	print(PRINTING_COLORS.function+f'\t\t{" "*len(str(i))}  Executes:', f'{f.module.__name__}.{f.__name__} from {Fore.WHITE}file://{module_file}')
	print(PRINTING_COLORS.function+f'\t\t{" "*len(str(i))}  Settings:', f'{f.show=}, {f.pause=}')
	print(f'\t\t{" "*len(str(i))}'+'  ' + '-'*80)


class Device:
	""" Models a generic device or service.
		Can be used to provide function metadata, must be the first (highest) decorator.
	"""

	HEADERS = ['title', 'description', 'name', 'module', 'show', 'pause']  # All self parameters assigned in __call__
	FUNCTIONS = []

	def __init__(self, title=None, description=None, show=None, pause=None):
		""" If no title is provided, the capitalized function name is used with _ and __ replaced by ' ' and '\n'. """
		self.title = title
		self.description = description
		self.show = show
		self.pause = pause

	def __call__(self, func):  # Decorator
		def get(self, attribute, default):
			# Self attributes are not assigned if the Device decorator is omitted.
			if hasattr(self, attribute):
				value = getattr(self, attribute)
				if value is not None:
					return value
			return default  # If the self attributes are not defined, then a default must be provided.

		self.name = func.__name__  # Callable name
		self.module = inspect.getmodule(func)		
		self.title = get(self, 'title', func.__name__.replace('__', '\n').replace('_', ' ').title()) # Readable name
		self.show = get(self, 'show', False)
		self.pause = get(self, 'pause', False)
		
		# Description is chosen in this order: description, docstring, ""
		if func.__doc__ is not None:
			if (not hasattr(self, 'description')) or self.description is None:
				self.description = func.__doc__
		elif not hasattr(self, 'description'):
			self.description = ""

		return self.__end_call__(Device, self, func)

	@staticmethod
	def __end_call__(cls, decorator, func):
		# Create unique function to register...
		def f(*args, **kwargs):
			try:
				func(*args, **kwargs)  # ...that just calls the function being decorated,
			except Exception as e:  # or indicates that there was an error calling it.
				if cls != Device:
					return
				import traceback
				title = f'Pybiosis Function {decorator.title} Failed'
				text = str(e)+'\n'+'='*30+'\n'+traceback.format_exc() + str(args)+str(kwargs)+'|'
				
				# Signal to the user that something has gone wrong.
				try:
					import winsound
					winsound.Beep(1500, 100)
					winsound.Beep(1500, 100)
				except:
					pass

				try:
					import ctypes
					ctypes.windll.user32.MessageBoxW(0, text, title, 0x00000010)
				except:
					import tkinter as tk
					import tkinter.messagebox as m
					root = tk.Tk()
					root.withdraw()
					m.showwarning(title, text)
		
		# Copy metadata to f
		[setattr(f, k, getattr(func, k, '')) for k in ['__name__', '__doc__', '__module__']]
		[setattr(f, k, getattr(decorator, k)) for k in Device.HEADERS]
		[setattr(f, k, getattr(decorator, k)) for k in decorator.HEADERS]

		# Store f
		if cls == Device:  # Device decorator is applied last, so it should be the final thing to put it in the pipeline.
			Device.FUNCTIONS.append((decorator.__class__, f))
		return f

	@staticmethod
	def compile(functions):
		raise NotImplementedError

	@staticmethod
	def compile_all(priority=None):
		# If a function is decorated multiple times, the Device decorator
		# parameters only affects the bottom-most decorator.
		# This means that the Device.HEADERS don't propagate to each function.
		#
		# All of the function call the same function.__name__, so this can be used as a key.
		# Iterating through FUNCTIONS overrides higher up decorators due to the order of construction.
		# So, looping over it like this leaves the one with the true values in 'rename'.
		#
		# I need to preserve the order that the functions are entered.

		functions = Device.FUNCTIONS
		rename = {f.__name__: tuple([getattr(f, h) for h in Device.HEADERS]) for c, f in functions}
		for c, f in functions:
			for attr, value in zip(Device.HEADERS, rename[f.__name__]):
				setattr(f, attr, value)

		# Printing and Compiling
		init(autoreset=True)
		print(PRINTING_COLORS.main + f'Compiling {len(Device.__subclasses__())} Device(s)')
		
		start = time.time()
		if priority is None:
			devices = Device.__subclasses__()
		else:
			devices = []  # Sort by priority
			for i in range(max(priority.values()), -1, -1):
				classes_with_priority_i = [cls for cls, p in priority.items() if p == i]
				devices.extend(classes_with_priority_i)

			for device in Device.__subclasses__():
				if device not in devices:
					devices.append(device)

		for device in devices:
			try:
				device.compile([f for c, f in functions if c == device])
				print()
			except validate.InvalidEnvironment as e:
				print(Fore.RED + f'Could not load {device.__name__} compiler due to:', e)
		end = time.time()

		print(end=PRINTING_COLORS.main+f'Finished Compiling in {end-start:.1f} Seconds. ')
		print(end=PRINTING_COLORS.device+f'There were {len(Device.__subclasses__())} Devices with {len(functions)} Functions: ')
		print(end=PRINTING_COLORS.function+str({sc.__name__: len([f for c, f in functions if c == sc]) for sc in Device.__subclasses__()})[1:-1].replace("'", '')+'.')
		print()

# Emulates: from pybiosis.compilers.streamdeck import StreamDeck, for all Pybiosis compilers
compiler_modules = glob.glob(str(Path(__file__).parent/'compilers') + '/*.py')
compiler_modules = ['pybiosis.compilers.'+Path(c).name.split('.')[0] for c in compiler_modules]
for m in map(importlib.import_module, compiler_modules):
	classes = inspect.getmembers(sys.modules[m.__name__], inspect.isclass)
	for name in [name for name, c in classes if issubclass(c, Device)]:
		locals()[name] = getattr(m, name)
