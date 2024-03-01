import pybiosis.validate as validate
from pybiosis import PRINTING_COLORS, Device, print_function_header
from pybiosis.loader import get_user_path
from pathlib import Path
import os
import glob
import json
import itertools as it

## Tasker is a phone app that may be able to use google assistant to communicate between phone and these commands.
# Okay Google, on pc, play "balloon 6" -> Okay Google, run, balloon 6, in Tasker
# Okay Google, on pc, play "balloon 6" -> Okay Google, run, pc balloon 6, in Tasker
# So, I need to make it so that if I ping the server with a particular command, it will dispatch to these functions.
# run -> "start," "do," "set," or "send,"
# So, on Tasker, if I say "run", it needs to ...

def multi_phrase(*words):
	""" This function accepts a sequence of lists, where each list corresponds to multiple versions of a word.
	    The returned value is a list of all the possible ways to say that sentence.
	    This is useful since the Google assistant may mis-hear a particular phrasing,
	    and this makes it easier to construct multiple variants.

	    Examples:
	    	voice = multi_phrase(['open', 'play', 'place'], ['spire', 'fire', 'buyer'])
	    	voice = multi_phrase(['play'], ['spire']) == (['play'], ['spire'])

	    Because of this, multi_phrase can be used everywhere and is therefore automatically applied.
	"""
	return list(map(' '.join, it.product(*words)))

class Assistant(Device):
	""" A decorator that allows a function to be called from google assistant. """
	HEADERS = ['phrase']

	@classmethod
	@property
	def DATA_FILE(self):
		DATA_DIRECTORY = get_user_path() / '.compilers/assistant'
		DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
		return os.path.abspath(DATA_DIRECTORY / 'pybiosis.json')

	def __init__(self, phrase):
		"""
		 phrase can be a list of lists of words: [["wordA", "synonymA", "synonymB"], ["wordB"]]
		 or they can be a list of words or a single phrase: ["wordA", "wordB", "wordC"] == "wordA wordB wordC"

		 this format is not accepted: ["wordA", ["wordB", "synonymB"]]
		    instead it should be wrapped as in the first example.
		"""
		if isinstance(phrase, str):
			self.phrase = [phrase]
		else:
			phrase_type = type(phrase[0])
			assert all(type(p) == phrase_type for p in phrase)
			if phrase_type == str:
				self.phrase = phrase
			else:  # container
				self.phrase = multi_phrase(*phrase)

	def __call__(self, func):
		func = super().__call__(func)
		self.phrase = self.phrase
		return self.__end_call__(Assistant, self, func)

	@classmethod
	def compile(cls, functions):
		general_execution_string = lambda f, args: f'python -c "import {f.module.__name__}; {f.module.__name__}.{f.name}({args})"'
		execution_string = lambda f: general_execution_string(f, "'$'" if any(p[-1] == '$' for p in f.phrase) else '')

		print(PRINTING_COLORS.device + f'\t{Assistant.__name__}: {len(functions)} Function(s). "Hey Google:"')
		function_json = []
		for i, f in enumerate(functions):
			# Print
			print_function_header(f, i)
			print(PRINTING_COLORS.key + '\t\t\tCommand:', execution_string(f))
			if len(f.phrase) == 1:
				print(PRINTING_COLORS.key + '\t\t\tPhrases:', f.phrase[0])
			else:
				print(PRINTING_COLORS.key + '\t\t\tPhrases:', 'v'+'='*max(len(c) for c in f.phrase)+'v')
				for command in f.phrase:
					print('\t\t\t\t', command)
			print()

			for p in f.phrase:
				function_json.append({
					"title": f.title,
					"phrase": p,
					"command": execution_string(f),
					"start": str(get_user_path()),
				})

		with open(cls.DATA_FILE, "w") as file:
			json.dump(function_json, file, indent=4)


# This is the old version that worked with Push2Run and IFFFT, which is now useless.
# class Assistant2(Device):
# 	""" A decorator that allows a function to be called from google assistant. """

# 	P2R_DIRECTORY = get_user_path() / '.compilers/assistant'
# 	P2R_DIRECTORY.mkdir(parents=True, exist_ok=True)
# 	PUSH2RUN_PROFILE_PATH = os.path.abspath(P2R_DIRECTORY / 'pybiosis.p2r')
# 	HEADERS = ['phrase']

# 	def __init__(self, phrase):
# 		"""
# 		 phrase can be a list of lists of words: [["wordA", "synonymA", "synonymB"], ["wordB"]]
# 		 or they can be a list of words or a single phrase: ["wordA", "wordB", "wordC"] == "wordA wordB wordC"

# 		 this format is not accepted: ["wordA", ["wordB", "synonymB"]]
# 		    instead it should be wrapped as in the first example.
# 		"""
# 		if isinstance(phrase, str):
# 			self.phrase = [phrase]
# 		else:
# 			phrase_type = type(phrase[0])
# 			assert all(type(p) == phrase_type for p in phrase)
# 			if phrase_type == str:
# 				self.phrase = phrase
# 			else:  # container
# 				self.phrase = self.multi_phrase(*phrase)

# 	def __call__(self, func):
# 		func = super().__call__(func)
# 		self.phrase = self.phrase
# 		return self.__end_call__(Assistant, self, func)

# 	@staticmethod
# 	def multi_phrase(*words):
# 		""" This function accepts a sequence of lists, where each list corresponds to multiple versions of a word.
# 		    The returned value is a list of all the possible ways to say that sentence.
# 		    This is useful since the Google assistant may mis-hear a particular phrasing,
# 		    and this makes it easier to construct multiple variants.

# 		    Examples:
# 		    	voice = multi_phrase(['open', 'play', 'place'], ['spire', 'fire', 'buyer'])
# 		    	voice = multi_phrase(['play'], ['spire']) == (['play'], ['spire'])

# 		    Because of this, multi_phrase can be used everywhere and is therefore automatically applied.
# 		"""
# 		return list(map(' '.join, it.product(*words)))

# 	@staticmethod
# 	def compile(functions):
# 		general_execution_string = lambda f, args: f'-c "import {f.module.__name__}; {f.module.__name__}.{f.name}({args})"'
# 		execution_string = lambda f: general_execution_string(f, "'$'" if any(p[-1] == '$' for p in f.phrase) else '')
# 		try:
# 			assert os.path.exists(R"C:\Program Files\Push2Run"), "Push2Run must be installed in Program Files to function properly."
# 			PUSH2RUN_LOCAL_DATA = fR"{os.getenv('LOCALAPPDATA')}\Rob_Latour"
# 			PUSH2RUN_DATABASES = fR"{os.getenv('APPDATA')}\Push2Run\Push2Run*.db3"
# 		except (FileNotFoundError, AssertionError) as e:
# 			raise validate.InvalidEnvironment(e)

# 		print(PRINTING_COLORS.device + f'\t{Assistant.__name__}: {len(functions)} Function(s). "Hey Google:"')
# 		function_json = []
# 		for i, f in enumerate(functions):
# 			# Print
# 			print_function_header(f, i)
# 			print(PRINTING_COLORS.key + '\t\t\tCommand:', 'python', execution_string(f))
# 			if len(f.phrase) == 1:
# 				print(PRINTING_COLORS.key + '\t\t\tPhrases:', f.phrase[0])
# 			else:
# 				print(PRINTING_COLORS.key + '\t\t\tPhrases:', 'v'+'='*max(len(c) for c in f.phrase)+'v')
# 				for command in f.phrase:
# 					print('\t\t\t\t', command)
# 			print()

# 			# Process
# 			function_json.append({
# 				"Descrption": f.title,  # "Descrption" is a typo in Push2Run so it is kept as is.
# 				"ListenFor": '\r'.join(f.phrase),
# 				"Open": "python",
# 				"Parameters": execution_string(f),
# 				"StartIn": str(get_user_path()),
# 				"Admin": True,
# 				"StartingWindowState": 1,
# 				"KeysToSend": ""
# 			})

# 		# Close Push2Run. Requires terminal with admin priv.
# 		if os.system('powershell.exe -command "taskkill /IM Push2Run.exe /T /F  --quiet --no-verbose *>$null"') == 0:
# 			time.sleep(2)

# 		# Reset all push2run functions. Note that this leaves the 'calculator' command, but this isn't a big deal.
# 		for file in glob.glob(PUSH2RUN_DATABASES):
# 			try:
# 				Path(file).unlink(missing_ok=True)
# 			except PermissionError as e:
# 				pass  # The process cannot access the file because it is being used by another process: '...\\Push2Run.db3'
			
# 		# Programmatic uploading was added to push2run: https://www.push2run.com/phpbb/viewforum.php?f=6
# 		os.makedirs(os.path.dirname(Assistant.PUSH2RUN_PROFILE_PATH), exist_ok=True)
# 		with open(Assistant.PUSH2RUN_PROFILE_PATH, "w") as file:
# 			json.dump(function_json, file, indent=4)

# 		# We don't want the p2r screen showing. There are settings to stop popup, and you can set the .exe to start minimized.
# 		os.startfile(Assistant.PUSH2RUN_PROFILE_PATH)
