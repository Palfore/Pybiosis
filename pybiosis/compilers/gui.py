## Each compiler should implement a streamlit interface.
from pathlib import Path
import pybiosis.commands as commands
import pybiosis.loader as loader
import pybiosis.core as pybiosis
import pybiosis.util.general as general
import streamlit as st
import ast
import os


def create_grid(num_rows: int, num_cols: int, button_info):
	# Create a NxM grid of buttons with tooltips
	for i in range(num_rows):
		cols = st.columns(num_cols)
		for j in range(num_cols):
			button_info_idx = i * num_cols + j
			with cols[j]:
				button_label = button_info[button_info_idx]["label"]
				tooltip = button_info[button_info_idx]["tooltip"]
				function = button_info[button_info_idx]["function"]
				button_clicked = st.button(button_label, help=tooltip, disabled=not bool(function))
				if button_clicked:
					identifier = f"{function['dot']}.{function['name']}"
					st.write(function, identifier)

					module = general.import_module(function['file'])  # We are in the user_path.
					function = getattr(module, function['name'])
					function()
					# commands.RunHelper.call_function_by_dot_syntax(identifier)


def main():
	st.set_page_config(layout="wide")
	st.write("# Pybiosis GUI")
	st.write("Here you can access all of your functionality.")

	tabs = st.tabs(["StreamDeck", "Assistant", "Scheduler", "CLI", ])
	with tabs[0]:
		with st.spinner("Loading Commands..."):
			layout = {}
			user_path = loader.get_user_path()
			with general.ChangeDir(user_path):
				pybiosis.load()
				for decorator, end_call in pybiosis.Device.FUNCTIONS:
					if hasattr(end_call, 'location'):
						dot = str(Path(end_call.module.__file__).relative_to(user_path)).replace(os.sep, '.').replace('.py', '')
						location = str(end_call.location).replace('\n', '_')
						layout[location] = {'dot': dot, 'name': str(end_call.name), 'file': str(Path(end_call.module.__file__))}


			grouped_data = {}
			for string_key in layout:
				try:
					key = ast.literal_eval(string_key)
				except:
					key = string_key

				if isinstance(key, str):
					prefix, coords = key.rsplit('/', 1)
					prefix = prefix.strip('/')
					if prefix not in grouped_data:
						grouped_data[prefix] = []
					grouped_data[prefix].append( {**layout[string_key], 'coords': coords})
				else:
					for subkey in key:
						if '/' in subkey:
							prefix, coords = subkey.rsplit('/', 1)
							prefix = prefix.strip('/')
						else:
							prefix, coords = '', subkey

						if prefix not in grouped_data:
							grouped_data[prefix] = []
						grouped_data[prefix].append( {**layout[string_key], 'coords': coords})

		st.write("### StreamDeck")
		NUM_ROWS = 4
		NUM_COLS = 5
		location = st.selectbox(f"Select a location: ", sorted(list(grouped_data)))
		st.write('---')

		mapping = {}
		for function in grouped_data[location]:
			mapping[function['coords']] = function

		button_info = [  # Define labels and tool tips for buttons
		    {
		    	"label": mapping.get(f"{i},{j}", {'name': f'{i},{j}'})['name'],
		    	# "tooltip": mapping.get(f"{i},{j}", {'description': f'{i},{j}'})['description'],
		    	"tooltip": f"{i},{j}",  # Description not yet supported
		    	"function": mapping.get(f"{i},{j}"),
		    } for i in range(NUM_ROWS) for j in range(NUM_COLS)
		]
		create_grid(NUM_ROWS, NUM_COLS, button_info)


	for tab in tabs[1:]:
		with tab:
			st.write("This device does not yet support a GUI interface.")


if __name__ == '__main__':
	main()