from pathlib import Path
from pprint import pprint
import itertools as it
import pyautogui
import inspect
import shutil
import glob
import json
import time
import os

def general(title, description="", popup=False):
	# popup currently does nothing. This may be useful later: 'powershell.exe', 'powershell.exe -windowstyle hidden

	def decorator(func):
		func.title = title  # Readable name
		func.name = func.__name__  # Callable name
		func.description = description

		if not hasattr(func, 'is_google'):
			func.is_google = False
		if not hasattr(func, 'is_deck'):
			func.is_deck = False

		module_name = inspect.getmodule(func).__name__
		if func.is_google:
			func.push2run_dict = {
				"Descrption": func.title,  # "Descrption" is a typo in Push2Run so it is kept as is.
				"ListenFor": '\r'.join(func.voice),
				"Open": "python",
				# "Parameters": f'-c "import commands; commands.{func.name}()"',
				"Parameters": f'-c "import {module_name}; {module_name}.{func.name}()"',
				"StartIn": os.environ.get('PYBIOSIS_USER_PATH'),
				"Admin": True,
				"StartingWindowState": 1,
				"KeysToSend": ""
			}

		if func.is_deck:
			func.deck_dict = {
				'Name': 'Open',
				'Settings': {
					'openInBrowser': True,
					# 'path': f'cmd.exe /c "cd /d {os.path.abspath(Path(__file__).parent)} && python -c "import commands; commands.{func.name}();""',
					'path': f'cmd.exe /c "cd /d {os.environ.get("PYBIOSIS_USER_PATH")} && python -c "import {module_name}; {module_name}.{func.name}();""',
					# 'path': f'cmd.exe /c "cd /d {os.path.abspath(Path(__file__).parent)} && python -c "import {module_name}; {module_name}.{func.name}();""',
					# Can I rewrite this using powershell to avoid the prompt?
					# 'path': f'cmd.exe /c "cd /d {os.path.abspath(Path(__file__).parent)} && python -c "import commands; commands.{func.name}();""',
					# 'path': f'powershell.exe -command "cd  {os.path.abspath(Path(__file__).parent)} && python -c "import commands; commands.{func.name}();""',
				},

				# cmd.exe /c START /MIN "cd /d C:\Users\nawar\Documents\GitHub\Pybiosis && python -c "import commands; commands.runelite();""
				# cmd.exe /c START /MIN "cd /d C:\Users\nawar\Documents\GitHub\Pybiosis && python -c "import commands; commands.to_results();""
				'State': 0,
				'States': [{'FFamily': '',
					'FSize': '9',
					'FStyle': '',
					'FUnderline': 'off',
					'Image': 'state0.png',
					'Title': func.title,
					'TitleAlignment': 'top',
					'TitleColor': '#ffffff',
					'TitleShow': ''
				}],
				'UUID': 'com.elgato.streamdeck.system.open'
			}
		return func
	return decorator

def google(voice):
	''' Google Assistant '''
	if not hasattr(google, 'functions'):
		google.functions = []

	def decorator(func):
		func.is_google = True
		
		func.voice = [voice] if isinstance(voice, str) else voice
		
		google.functions.append(func)
		return func
	return decorator

def deck(location, image=None):
	''' Stream Deck '''
	if not hasattr(deck, 'functions'):
		deck.functions = []

	def decorator(func):
		func.is_deck = True

		func.location = location
		func.image = image
		
		deck.functions.append(func)
		return func
	return decorator

def multi_phrase(*words):
	""" This function accepts a sequence of lists, where each list corresponds to multiple versions of a word.
	    The returned value is a list of all the possible ways to say that sentence.
	    This is useful since the Google assistant may mis-hear a particular phrasing,
	    and this makes it easier to construct multiple variants.
	"""
	return list(map(' '.join, it.product(*words)))


class Compiler:
	def __init__(self, push2run_overwrite=True, deck_overwrite=True):
		self.PUSH2RUN_PROFILE_PATH = os.path.abspath(Path(__file__).parent / 'applications' / 'Push2Run' / 'pybiosis.p2r')
		self.PUSH2RUN_LOCAL_DATA = fR"{os.getenv('LOCALAPPDATA')}\Rob_Latour"
		self.PUSH2RUN_DATABASES = fR"{os.getenv('APPDATA')}\Push2Run\Push2Run*.db3"

		self.DECK_EXE = R'"C:\Program Files\Elgato\StreamDeck\StreamDeck.exe"'
		self.DECK_PROFILE_PATH = fR"{os.getenv('APPDATA')}\Elgato\StreamDeck\ProfilesV2\225568A9-0B81-450D-9AA8-7E87574FB7F2.sdProfile"
		self.PUSH2RUN_OVERWRITE = push2run_overwrite
		self.DECK_OVERWRITE = deck_overwrite

		if hasattr(google, "functions"):
			print(f'Summary of ({len(google.functions)}) Google Functions:')
			print('============================')
			for i, f in enumerate(google.functions, 1):
				title = f.title.replace('\n', ' ')
				print(f'({i}) {title} - {f.description}')
				print('\t', 'Commands:')
				for command in f.voice:
					print('\t\t', command)
				print('----------------------------')
			print('============================')
			print('\n\n')
		else:
			print("There are no google functions.")

		
		if hasattr(deck, "functions"):
			print(f'Summary of ({len(deck.functions)}) Deck Functions:')
			print('============================')
			for i, f in enumerate(deck.functions, 1):
				title = f.title.replace('\n', ' ')
				print(f'({i}) {title} - {f.description}')
				print('\t', 'Location:', f.location)
				print('\t', 'Image:', f.image)
				print('----------------------------')
			print('============================')
		else:
			print("There are no stream deck functions.")



	def compile(self):
		if self.PUSH2RUN_OVERWRITE:
			if os.system('powershell.exe -command "taskkill /IM Push2Run.exe /T /F"') == 0:  # Requires terminal with admin priv.
				time.sleep(2)


			# There is a bug that makes push2run prompt for a password, deleting these files will prevent it from happening.
			# https://push2run.com/passwordpromptfix.html
			# import shutil
			# shutil.rmtree(self.PUSH2RUN_LOCAL_DATA)
			# This doesn't work either... Creates a clean version which prompts user even more.


			# Reset all push2run functions. Note that this leaves the 'calculator' command, but this isn't a big deal.
			# I'm thinking an empty file "may" erase it: [], but I won't deal with this yet.
			for file in glob.glob(str(self.PUSH2RUN_DATABASES)):
				os.remove(file)

			# Programmatic uploading was added to push2run: https://www.push2run.com/phpbb/viewforum.php?f=6
			# Calculator is still added, but I think that is fine.
			json.dump([m.push2run_dict for m in google.functions], open(self.PUSH2RUN_PROFILE_PATH, 'w'), indent=4)			
			os.system(f'powershell.exe -command "Start-Process -window minimized {self.PUSH2RUN_PROFILE_PATH}"')
			# os.system(f'start /min "" "{self.PUSH2RUN_PROFILE_PATH}"')


		if self.DECK_OVERWRITE:
			def ID_to_manifest(ID):
				return json.load(open(self.DECK_PROFILE_PATH + '/Profiles/' + ID + '.sdProfile/manifest.json'))

			def get_manifest_folders(manifest):
				folders = {}
				for location, details in manifest['Actions'].items():
					if details['Name'] == 'Create Folder':
						title = details['States'][0]['Title']  # Assumes only 1 state
						ID = details['Settings']['ProfileUUID']
						folders[title] = ID
				return folders

			def get_subfolders(ID):
				return get_manifest_folders(ID_to_manifest(ID))

			def recur(IDseq):
				sf = get_subfolders(IDseq[-1][1])
				new_IDseqs = []
				for name, ID in sf.items():
					new_IDseqs.append( IDseq + [(name, ID)] )
				
				for seq in new_IDseqs[:]:
					new_IDseqs.extend(recur(seq))

				return new_IDseqs

			if os.system('powershell.exe -command "taskkill /IM Streamdeck.exe /T /F"') == 0:  # Requires terminal with admin priv.
				time.sleep(1)

			# Construct nested folders. Each folder is a different profile.
			manifest = json.load(open(self.DECK_PROFILE_PATH + '/manifest.json'))
			main_folders = get_manifest_folders(manifest)
			nested_folders = {}
			for title, ID in main_folders.items():
				for sequence in recur([ (title, ID) ]):
					path = '/'.join([folder for folder, ID in sequence])
					final_ID = sequence[-1][1]
					nested_folders[path.strip('\n')] = final_ID  # Ignore newlines in path - which are accidentally typed into GUI
			folders = {**main_folders, **nested_folders}
			pprint(folders)


			# Add in Deck Functions
			for deck_function in deck.functions:
				folder, coords = deck_function.location.rsplit('/', 1)
				folder_ID = folders[folder]
				folder_path = self.DECK_PROFILE_PATH + f'/Profiles/{folder_ID}.sdProfile/'
				
				folder_manifest = json.load(open(folder_path + 'manifest.json'))
				folder_manifest['Actions'][coords] = deck_function.deck_dict

				# Image Support
				if deck_function.image:
					image_path = Path(os.environ.get("PYBIOSIS_USER_PATH")) / 'Icons' / deck_function.image
					state_path = f'{folder_path}/{coords}/CustomImages'
					if deck_function.image == 'default':
						try:
						    os.remove(f'{state_path}/state0.png')
						except OSError:
						    pass
						try:
							Path(state_path).rmdir()
						except FileNotFoundError:
						    pass
					else:
						Path(state_path).mkdir(parents=True, exist_ok=True)
						shutil.copyfile(image_path, f'{state_path}/state0.png')

				json.dump(folder_manifest, open(f'{folder_path}/manifest.json', 'w'))
			# os.system(Rf'cmd.exe /c start "" /min {self.DECK_EXE}')
			os.system(Rf'start "" /max {self.DECK_EXE}')
			time.sleep(1.5)
			
			# Minimize by closing. Dangerous to alt-f4, cannot find alternative.
			pyautogui.hotkey('alt', 'f4')


