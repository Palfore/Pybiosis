""" This module serves as a python wrapper for https://github.com/MScholtes/VirtualDesktop, with a modified api.
	
	This assumes no desktops contain the string "(visible)".
	The previous implementation has a state (keeps an internal reference to desktops via a pipeline), this however removes this.
"""

from typing import Union
from pathlib import Path
import subprocess

EXE = Rf"{Path(__file__).parent}\VirtualDesktop\VirtualDesktop.exe"

def command(commands: list, **kwargs):
	commands = [str(c) for c in commands]
	if 'capture_output' not in kwargs:
		kwargs['capture_output'] = True
	
	# print(commands)  # For debugging
	output = subprocess.run(commands, **kwargs)
	o, e = output.stdout.decode('utf-8', errors='ignore'), output.stderr.decode('utf-8', errors='ignore')
	if e != '':
		raise ValueError(e)
	return o

def list():
	""" Returns a list of virtual desktops by name, in order of increasing index. """
	o = command([EXE, '/list'])
	names = o.split('\n')[2:-3]  # First two elements are headers, last three are ['', count, ''].
	return [name.rstrip("\r").replace(" (visible)", '') for name in names]  # Might fail if (visible in title).
	
def count():
	""" Returns the number of virtual desktops. """
	o = command([EXE, '/count'])
	return int(o.split('\n')[0].replace('Count of desktops: ', ''))

def exists(selector):
	for desktop in list():
		if selector in [desktop, get_index(desktop)]:
			return True
	return False

def get_active_desktop():
	""" Returns the (index, name) of the active desktop. """
	o = command([EXE, '/GetCurrentDesktop'])
	(name, index) = o.lstrip("Current desktop: ").split(' (desktop number ')
	return int(index.strip(")\r\n")), name.strip("'")

def get_name(index: int):
	return list()[index]

def get_index(name: str):
	return {n: i for i, n in enumerate(list())}[name]

def rename(name, selector=None):
	""" set name of desktop with number in pipeline (short: /na)."""
	if selector is None:
		selector, _ = get_active_desktop()
	if name in list():  # name might already exist, leading to a possible duplicate
		if not (selector == name or selector == get_index(name)):  # unless renaming same desktop
			print(f"Warning: Duplicate name detected ({name}).")
	command([EXE, f'-GetDesktop:{selector}', f'-Name:{name}'])

def switch(selector=None):
	""" switch to desktop with number <n>, desktop with text <s> in name or with number in pipeline (short: /s).
		ValueErorr raised if selector is invalid.
	"""
	if selector is None:
		selector, _ = get_active_desktop()
	if not exists(selector):
		raise ValueError(f"The selector {selector} does not exist.")
	
	command([EXE, f'-Switch:{selector}'])

def new(name):
	""" create new desktop (short: /n). Number is stored in pipeline."""
	command([EXE, f'-New'])
	rename(name, count()-1)

def remove(selector=None):
	"""remove desktop number <n>, desktop with text <s> in name or desktop with number in pipeline (short: /r)."""
	if selector is None:
		selector, _ = get_active_desktop()
	command([EXE, f'-Remove:{selector}'])

def move_window(identifier, desktop):
	"""move process with name <s> or id <n> to desktop with number in pipeline (short: /mw)."""
	command([EXE, f'-GetDesktop:{desktop}', f'-MoveWindow:{identifier}'])

def move_window_handle(identifier, desktop):
	"""move window with text <s> in title or handle <n> to desktop with number in pipeline (short: /mwh)."""
	command([EXE, f'-GetDesktop:{desktop}', f'-MoveWindowHandle:{identifier}'])

def move_window_handle(identifier, desktop):
	"""move window with text <s> in title or handle <n> to desktop with number in pipeline (short: /mwh)."""
	command([EXE, f'-GetDesktop:{desktop}', f'-MoveWindowHandle:{identifier}'])

def move_active_window(desktop):
	"""move active window to desktop with number in pipeline (short: /maw)."""
	command([EXE, f'-GetDesktop:{desktop}', f'-MoveActiveWindow'])

def pin_window(identifier):
	"""pin window with text <s> in title or handle <n> to all desktops (short: /pwh)."""
	command([EXE, f'-PinWindow:{identifier}'])

def pin_window_handle(identifier):
	"""pin window with text <s> in title or handle <n> to all desktops (short: /pwh)."""
	command([EXE, f'-PinWindowHandle:{identifier}'])

def get_window_properties():
	# Command execution time is about 1 second
	properties = ["Id", "Name", "MainWindowHandle", "MainWindowTitle"]
	o = command(["powershell.exe", "Get-Process", "|", "Where-Object", '{$_.MainWindowTitle -ne ""}', "|", "Select-Object", "-Property", ', '.join(properties)])
	
	windows = []
	for x in o.split('\n'):
		x = ' '.join(x.split()).strip(' ')  # compress whitespace
		x = x.split(' ', len(properties) - 1)  # MainWindowTitle is the last line, and is the only multi-word entry, so collect it.
		if x == ['']:  # Empty values due to spacing in table output
			continue
		x = dict(zip(properties, x))
		
		if x['Id'] in ['Id', '--']:  # Remove table headers
			continue

		x['Desktop'] = get_desktop_from_window(x['Id'])

		windows.append(x)
	return windows

def get_desktop_from_window(identifier):
	"""get desktop number where process with name <s> or id <n> is displayed (short: /gdfw)."""
	try:
		o = command([EXE, f'-GetDesktopFromWindow:{identifier}'])
	except ValueError:
		return None

	o = o.replace('Window is on desktop number ', '')
	o = o.replace("')", '')
	index, name = o.split(" (desktop '")
	return name.strip()


# Some higher level functions
# BUG: Sometimes the 'Name' property is truncated and replaces the ending with '...'.
# To acomodate this, if a name ends with '...', it is only checked up to that point.
import pygetwindow
import ctypes
import time

def change_desktop_background(path):
	# path => "C:\\Users\\...\\Pictures\\background.png"
	# print(f'"{path}"')
	ctypes.windll.user32.SystemParametersInfoW(20, 0, path , 0)

def grab_windows(*window_names):
	return grab_windows_by('Name', *window_names)

def grab_windows_by(attribute, *attribute_values):
	window_objects = []
	for attribute_value in attribute_values:
		for window in get_window_properties():
			# Truncated Check
			if attribute == 'Name' and window['Name'].endswith('...'):
				cutoff = window['Name'].find('...')

				if window['Name'][:cutoff] == attribute_value[:cutoff] and window['Desktop'] == get_active_desktop()[1]:
					window_objects.append(next(w for w in pygetwindow.getAllWindows() if int(w._hWnd) == int(window['MainWindowHandle'])))	
					continue
			
			# Normal check
			if window[attribute] == attribute_value and window['Desktop'] == get_active_desktop()[1]:
				window_objects.append(next(w for w in pygetwindow.getAllWindows() if int(w._hWnd) == int(window['MainWindowHandle'])))
	return window_objects

def focus(application, delay=0):
	terminal = grab_windows(application)[0]
	terminal.maximize()
	terminal.activate()
	time.sleep(delay)



if __name__ == '__main__':
	from pprint import pprint
	

	windows = get_window_properties()
	for window in windows:
		 # if window['Name'] == 'WindowsTerminal' and window['Desktop'] == get_active_desktop()[1]:
		 pprint(window)







# def GetDesktopFromWindowHandle(index=None, name=None):
# 	"""get desktop number where window with text <s> in title or handle <n> is displayed (short: /gdfwh)."""
# 	pass

# def IsWindowOnDesktop(index=None, name=None):
# 	"""check if process with name <s> or id <n> is on desktop with number in pipeline (short: /iwod). Returns 0 for yes, 1 for no."""
# 	pass

# def IsWindowHandleOnDesktop(index=None, name=None):
# 	"""check if window with text <s> in title or handle <n> is on desktop with number in pipeline (short: /iwhod). Returns 0 for yes, 1 for no."""
# 	pass

# def PinWindow(index=None, name=None):
# 	"""pin process with name <s> or id <n> to all desktops (short: /pw)."""
# 	pass

# def UnPinWindow(index=None, name=None):
# 	"""unpin process with name <s> or id <n> from all desktops (short: /upw)."""
# 	pass

# def UnPinWindowHandle(index=None, name=None):
# 	"""unpin window with text <s> in title or handle <n> from all desktops (short: /upwh)."""
# 	pass

# def IsWindowPinned(index=None, name=None):
# 	"""check if process with name <s> or id <n> is pinned to all desktops (short: /iwp). Returns 0 for yes, 1 for no."""
# 	pass

# def IsWindowHandlePinned(index=None, name=None):
# 	"""check if window with text <s> in title or handle <n> is pinned to all desktops (short: /iwhp). Returns 0 for yes, 1 for no."""
# 	pass

# def PinApplication(index=None, name=None):
# 	"""pin application with name <s> or id <n> to all desktops (short: /pa)."""
# 	pass

# def UnPinApplication(index=None, name=None):
# 	"""unpin application with name <s> or id <n> from all desktops (short: /upa)."""
# 	pass

# def IsApplicationPinned(index=None, name=None):
# 	"""check if application with name <s> or id <n> is pinned to all desktops (short: /iap). Returns 0 for yes, 1 for no."""
# 	pass
