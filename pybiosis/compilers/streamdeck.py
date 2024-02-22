import pybiosis.validate as validate
from pybiosis import PRINTING_COLORS, Device, print_function_header
from pybiosis.utility import save_function
from pybiosis.loader import get_user_path
from pathlib import Path
import os
import time
import json
import shutil
import glob

class StreamDeck(Device):
	""" A decorator that allows a function to be called from a StreamDeck button. """

	HEADERS = ['location', 'image', 'setter']
	TEMP_PATH = get_user_path() / '.compilers/streamdeck'
	NUM_ROWS = 3
	NUM_COLUMNS = 5
	
	def __init__(self, location, image=None, setter=None): 
		self.location = location
		self.image = image
		self.setter = setter

	def __call__(self, func):
		func = super().__call__(func)
		if any(l.endswith('0,0') and l.startswith('/') for l in self.location):
			raise ValueError(f"Cannot override the return button with {func.title}.")
		return self.__end_call__(StreamDeck, self, func)

	@staticmethod
	def compile(functions):
		validate.require_windows()
		execution_string = lambda f: f'cd /d {get_user_path()} && python -c "import {f.module.__name__}; {f.module.__name__}.{f.name}();"'
		try:
			DECK_EXE = R'"C:\Program Files\Elgato\StreamDeck\StreamDeck.exe"'
			DECK_PROFILES = fR"{os.getenv('APPDATA')}\Elgato\StreamDeck\ProfilesV2"
			DECK_PROFILE_IDENTIFIER = os.getenv('PYBIOSIS_PROFILE_ID', os.listdir(DECK_PROFILES)[0].replace('.sdProfile', ''))
		except FileNotFoundError as e:
			raise validate.InvalidEnvironment(f"StreamDeck.exe could not be found in Program Files. ({DECK_EXE})")
		DECK_PROFILE_PATH = fR"{DECK_PROFILES}\{DECK_PROFILE_IDENTIFIER}.sdProfile"
		IMAGE_DIRECTORY = 'Images'

		if os.system('powershell.exe -command "taskkill /IM Streamdeck.exe /T /F | out-null"') == 0:  # Requires terminal with admin priv.
			time.sleep(1)
		folders = get_folders(DECK_PROFILE_PATH)
		print(PRINTING_COLORS.device+f'\t{StreamDeck.__name__}: {len(functions)} Function(s)')
		for f in glob.glob(str(StreamDeck.TEMP_PATH / '*')):
			os.remove(f)
		for i, f in enumerate(functions):

			if f.setter:
				f.title = f.setter

			# Print
			print_function_header(f, i)
			print(PRINTING_COLORS.key+f'\t\t\tCommand:', execution_string(f))
			print(PRINTING_COLORS.key+f'\t\t\tLocation:', str(f.location).replace('\n', ' '))
			print(PRINTING_COLORS.key+f'\t\t\tImage:', f.image)
			print(PRINTING_COLORS.key+f'\t\t\tName:', '|'.join([f.__name__, f.name, f.title]))

			# Process
			file = save_function(StreamDeck.TEMP_PATH, f.__name__+'_'+str(id(f)), execution_string(f), f=f)
			locations = [f.location] if isinstance(f.location, str) else f.location  # single location or list of them.
			for location in locations:
				if '/' in location:
					folder, coords = location.rsplit('/', 1)
					# folder = folder.rstrip('/')  # Ignore duplicate /'s that may pass through, eg: location//1,3
					if folder not in folders:
						raise ValueError(f'Could not find the folder "{folder}" for function "{f.name}" in {location}, {f.module}.')
					folder_ID = folders[folder]
					folder_path = DECK_PROFILE_PATH + f'/Profiles/{folder_ID}.sdProfile/'
				else:
					coords = location
					folder_path = DECK_PROFILE_PATH

				
				try:
					folder_manifest = json.load(open(folder_path + '/manifest.json'))
				except FileNotFoundError:
					continue
				folder_manifest['Actions'][coords] = {
					'Name': 'Open',
					'Settings': {
						'openInBrowser': True,
						'path': str(file),
					},
					'State': 0,
					'States': [{'FFamily': '',
						'FSize': '9',
						'FStyle': '',
						'FUnderline': 'off',
						'Image': 'state0.png',
						'Title': f.title,
						'TitleAlignment': 'top',
						'TitleColor': '#ffffff',
						'TitleShow': ''
					}],
					'UUID': 'com.elgato.streamdeck.system.open'
				}

				# Image Support
				if f.image:
					image_path = get_user_path() / IMAGE_DIRECTORY / f.image
					state_path = f'{folder_path}/{coords}/CustomImages'
					if f.image == 'default':
						Path(f'{state_path}/state0.png').unlink(missing_ok=True)
						shutil.rmtree(state_path, ignore_errors=True)
					else:
						Path(state_path).mkdir(parents=True, exist_ok=True)
						shutil.copyfile(image_path, f'{state_path}/state0.png')
				json.dump(folder_manifest, open(f'{folder_path}/manifest.json', 'w'), indent=4)
		if functions:
			os.system(Rf'start "" /max {DECK_EXE} --runinbk')


def get_folders(profile_path):
	def ID_to_manifest(ID):
		manifest_path = profile_path + '/Profiles/' + ID + '.sdProfile/manifest.json'
		try:
			return json.load(open(manifest_path))
		except json.decoder.JSONDecodeError:
			raise ValueError(f"Something went wrong loading file://{manifest_path}")

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
		try:
			sf = get_subfolders(IDseq[-1][1])
		except FileNotFoundError:
			raise ValueError("There are functions that use this non-existent path: " + ', '.join(map(str, IDseq)))

		new_IDseqs = []
		for name, ID in sf.items():
			new_IDseqs.append( IDseq + [(name, ID)] )
		for seq in new_IDseqs[:]:
			new_IDseqs.extend(recur(seq))
		return new_IDseqs

	# Construct nested folders. Each folder is a different profile.
	top_level_manifest_dir = profile_path
	top_level_manifest_file = top_level_manifest_dir + '/manifest.json'
	manifest = json.load(open(top_level_manifest_file))
	main_folders = get_manifest_folders(manifest)
	nested_folders = {}
	for title, ID in main_folders.items():
		for sequence in recur([ (title, ID) ]):
			path = '/'.join([folder for folder, ID in sequence])
			final_ID = sequence[-1][1]
			nested_folders[path.strip('\n')] = final_ID  # Ignore newlines in path - which are accidentally typed into GUI
	folders = {**main_folders, **nested_folders}
	# import pprint as p
	# p.pprint(folders)
	return folders