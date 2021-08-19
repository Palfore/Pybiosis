# python wrapper for https://www.nirsoft.net/utils/control_my_monitor.html
from collections import namedtuple
from pathlib import Path
# import subprocess
import time
import ast
import os

EXE = Rf"{Path(__file__).parent}\ControlMyMonitor\ControlMyMonitor.exe"
SOURCE_INPUT_CODES = {"dp": 15, "mdp": 16, "hdmi": 17}
COMMAND_CODES = {
	'source_input': 60,
	'brightness': 10,
	'contrast': 12,
}
MODES = {
	'abs': '/SetValue',
	'rel': '/ChangeValue',
}
FILE_CREATION_TIMEOUT = 5
SLEEP_INTERVAL = 0.1

def _cmd(lst):
	return os.system(' '.join(list(map(str, lst))))

def get_monitors():
	temp_monitor_file = '_monitors.txt'  # The "" filename isn't working, this is a workaround
	try:
		os.remove(temp_monitor_file)
	except FileNotFoundError:
		pass
	_cmd(['powershell.exe', EXE, '/smonitors', temp_monitor_file])

	file_creation_start_time = time.time()
	while not os.path.exists(temp_monitor_file):
	    time.sleep(SLEEP_INTERVAL)
	    if time.time() - file_creation_start_time > FILE_CREATION_TIMEOUT:
	    	raise ValueError(f"The file was not created before the timeout of {FILE_CREATION_TIMEOUT} seconds.")


	NUM_PROPERTIES = 5
	info = open(temp_monitor_file, 'r', encoding='utf16').readlines()
	info = [i.replace('//', '/') for i in info]

	os.remove(temp_monitor_file)
	info = [i for i in info if i != '\n']  # Remove blank lines
	details = [info[i::NUM_PROPERTIES] for i in range(NUM_PROPERTIES)]  # Group by property
	num_monitors = len(details[0])
	monitors = [{m[i].split(':')[0]: ast.literal_eval(m[i].split(':')[1].strip()) for m in details} for i in range(num_monitors)]
	monitors = {m['Monitor ID']: m for m in monitors}
	return monitors

def clone():
	_cmd(['displayswitch.exe', '/clone'])

def extend():
	_cmd(['displayswitch.exe', '/extend'])  # Not too sure which monitor is extended, I think there is a way to set primary/secondary or something?

def set_input_source(display, source):
	_cmd(['powershell.exe', EXE, '/SetValue', display, COMMAND_CODES['source_input'], SOURCE_INPUT_CODES[source]])

def brightness(display, brightness, mode='abs'):
	_cmd(['powershell.exe', EXE, MODES[mode], display, COMMAND_CODES['brightness'], brightness])

def contrast(display, contrast, mode='abs'):
	_cmd(['powershell.exe', EXE, MODES[mode], display, COMMAND_CODES['contrast'], contrast])

def appearance(display, brightness, contrast, mode='abs'):
	set_brightness(display, brightness)
	set_contrast(display, contrast)

def sleep(hibernate=False):
	_cmd(['powershell.exe', 'powercfg', '-h', {True: 'on', False: 'off'}[hibernate]])
	_cmd(['powershell.exe', 'rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'])
	


if __name__ == '__main__':
	from config import MONITORS
	import sys
	command = sys.argv[1]
	monitor = sys.argv[2]
	if command == 'brightness':
		brightness(MONITORS[monitor], 5, mode='rel')
