import subprocess

def command(commands: list, **kwargs):
	commands = [str(c) for c in commands if c != '']
	if 'capture_output' not in kwargs:
		kwargs['capture_output'] = True

	# print(commands)  # For debugging
	output = subprocess.run(commands, **kwargs)
	o, e = output.stdout.decode('utf-8', errors='ignore'), output.stderr.decode('utf-8', errors='ignore')
	if e != '':
		raise ValueError(e)
	return o

def save_function(path, name, command, f):
	""" Creates a .bat file and .vbs file for each function.
		The .bat displays a window.
		The .vbs does not display a window. """
	assert all(hasattr(f, k) for k in ['show', 'pause'])
	path.mkdir(parents=True, exist_ok=True)
	
	batch_file = path / (name + '.bat')
	with open(batch_file, 'w') as file:
		file.write(command)
	
	vb_file = path / (name + '.vbs')
	with open(vb_file, 'w') as file:
		file.write(f'Set WshShell = CreateObject("WScript.Shell")\n')
		file.write(f'WshShell.Run chr(34) & "{batch_file}" & Chr(34), 0\n')
		file.write(f'Set WshShell = Nothing\n')
	
	if f.show:
		flag = '/k' if f.pause else '/c'
		return f'cmd.exe {flag} ' + str(batch_file)
	else:
		return str(vb_file)