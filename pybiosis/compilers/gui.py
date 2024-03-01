## Each compiler should implement a streamlit interface.
import streamlit as st


def create_grid(num_rows: int, num_cols: int, button_info):
	# Create a NxM grid of buttons with tooltips
	for i in range(num_rows):
	    cols = st.columns(num_cols)
	    for j in range(num_cols):
	        button_info_idx = i * num_cols + j
	        with cols[j]:
	            button_label = button_info[button_info_idx]["label"]
	            tooltip = button_info[button_info_idx]["tooltip"]
	            button_clicked = st.button(button_label, help=tooltip)
	            if button_clicked:
	                button_function(button_label)

def main():
	st.write("# Pybiosis GUI")
	st.write("Here you can access all of your functionality.")

	tabs = st.tabs(["StreamDeck", "Assistant", "Scheduler", "CLI", ])


	with tabs[0]:
		def button_function(button_label):
		    st.write(f"Button '{button_label}' clicked!")


		st.write("### StreamDeck")
		NUM_ROWS = 4
		NUM_COLS = 5
		location = st.selectbox(f"Select a location: ", ["/Monitors/"])
		button_info = [  # Define labels and tooltips for buttons
		    {
		    	"label": f"Button ({i},{j})",
		    	"tooltip": f"Tooltip for Button ({i},{j})"
		    } for i in range(NUM_ROWS) for j in range(NUM_COLS)
		]
		create_grid(NUM_ROWS, NUM_COLS, button_info)


	for tab in tabs[1:]:
		with tab:
			st.write("This device does not support a GUI interface.")


if __name__ == '__main__':
	main()