""" This file shows a high-level example of using Pybiosis to generate dynamic buttons for the StreamDeck.

This file is not meant to run, since the modules like tools and config are not available.
This file demonstrates advanced usage.

"""

# Import the decorators
from pybiosis.core import Device, StreamDeck, Scheduler, apply_list, register

# Import the utility libraries
import itertools
import webbrowser

# Import the functional code (monitor brightness control, etc.)
from tools import monitors as controller
from config import MONITORS, MONITORSR
from games import Games


class Buttons:
	""" This class models a button layout on the StreamDeck. 
	
	It returns slices of the buttons, so that it is easy to iterate over. """

	ROWS = [0, 1, 2, 3, 4]
	COLS = [0, 1, 2]
	INVALID = (0, 0)  # We should not allow the ability to overwrite the back button. The compiler also raises if 0,0 is overwritten.

	@classmethod
	def get_all(cls):
		return [(row, col) for row, col in itertools.product(cls.ROWS, cls.COLS) if (row, col) != cls.INVALID]

	@classmethod
	def get_col(cls, row):
		return [(row, col) for row, col in itertools.product([row], cls.COLS) if (row, col) != cls.INVALID]

	@classmethod
	def get_row(cls, col):
		return [(row, col) for row, col in itertools.product(cls.ROWS, [col]) if (row, col) != cls.INVALID]


class MonitorLayout:
	""" Since pybiosis does not support creating folders yet, the user has to create a subfolder (of BASE) for each monitor. The compile errors will guide you. """

	BASE = "Monitors2/"


	def attach_function(self, buttons, base, kind, prefix, function, monitors, name):
		# We define entry points into the function.
		for row, col in buttons:

			# bound_method_name is the function that is attached to the global scope.
			# setter is the StreamDeck button label.
			get_bound_method_name = lambda row, col, name: f'{prefix}_{row}_{col}_{name.replace('/', '').replace('\\', '')}'

			def create_function(row=row, col=col, monitors=monitors, name=name):
				def kernel():
					return function(self.get_value(kind, row, col), monitors)

				location = f'{base.rstrip('/')}/{name}/{row},{col}'
				kernel.__name__ = get_bound_method_name(row, col, name)
				button_name = f'{prefix}:{self.get_value(kind, row, col)}'
				kernel = StreamDeck(location=location, setter=button_name if self.get_value(kind, row, col) else prefix)(kernel)
				return kernel

			globals()[get_bound_method_name(row, col, name)] = create_function()

	@staticmethod
	def get_value(kind, row, col):
		if kind == "screen_controls":
			match (row, col):
				case (row, 0):
					return [None, -10, +10, -10, +10][row]  # None -> (0, 0) origin

				case (row, 1):
					return [0, 30, 50, 70, 100][row]

				case (row, 2):
					return [0, 30, 50, 70, 100][row]
		
		elif kind == 'setting_controls': 
			match (row, col):
				case (row, col):
					return None

	def __init__(self, monitors, name):
		self.monitors = monitors
		self.name = name


	def create_screen_controls(self):
		base = f"{self.BASE.rstrip('/')}/Visuals"
		get_value = lambda row, col: self.get_value('screen_controls', row, col)

		self.attach_function(buttons=Buttons.get_row(1), base=base, kind='screen_controls', prefix='B', monitors=self.monitors, name=self.name, function=lambda value, monitors: [controller.brightness(MONITORS[m], value, mode='abs') for m in monitors])
		self.attach_function(buttons=Buttons.get_row(2), base=base, kind='screen_controls', prefix='C', monitors=self.monitors, name=self.name, function=lambda value, monitors: [controller.contrast(MONITORS[m], value, mode='abs') for m in monitors])
		self.attach_function(buttons=[(1, 0), (2, 0)], base=base, kind='screen_controls', prefix='^B', monitors=self.monitors, name=self.name, function=lambda value, monitors: [controller.brightness(MONITORS[m], value, mode='rel') for m in monitors])
		self.attach_function(buttons=[(3, 0), (4, 0)], base=base, kind='screen_controls', prefix='^C', monitors=self.monitors, name=self.name,function=lambda value, monitors: [controller.contrast(MONITORS[m], value, mode='rel') for m in monitors])

	def create_setting_controls(self):
		base = f"{self.BASE.rstrip('/')}/Settings"
		get_value = lambda row, col: self.get_value('setting_controls', row, col)

		self.attach_function(buttons=[(1, 0)], base=base, kind='setting_controls', prefix='Normal', monitors=self.monitors, name=self.name, function=lambda value, monitors: [controller.rotate(m, 'landscape') for m in monitors])
		self.attach_function(buttons=[(2, 0)], base=base, kind='setting_controls', prefix='Rotated', monitors=self.monitors, name=self.name, function=lambda value, monitors: [controller.rotate(m, 'portrait') for m in monitors])
		self.attach_function(buttons=[(3, 0)], base=base, kind='setting_controls', prefix='Normal_u', monitors=self.monitors, name=self.name, function=lambda value, monitors: [controller.rotate(m, 'landscape_flipped') for m in monitors])
		self.attach_function(buttons=[(4, 0)], base=base, kind='setting_controls', prefix='Rotated_u', monitors=self.monitors, name=self.name, function=lambda value, monitors: [controller.rotate(m, 'portrait_flipped') for m in monitors])
		# self.attach_function(buttons=[(3, 0)], base=base, kind='setting_controls', prefix='Duplicate', monitors=self.monitors, name=self.name, function=lambda value, monitors: [controller.brightness(MONITORS[m], value, mode='abs') for m in monitors])
		# self.attach_function(buttons=[(4, 0)], base=base, kind='setting_controls', prefix='Unplay', monitors=self.monitors, name=self.name, function=lambda value, monitors: [controller.brightness(MONITORS[m], value, mode='abs') for m in monitors])


## Dynamically generate a button layout in the StreamDeck to control the monitors. The associated methods are bound to global namespace.
manager = controller.MonitorManager()

# Individual and ALL Screen Controls
for m in manager.get_friendly_mapping(MONITORSR):
	layout = MonitorLayout([m], name=m)
	layout.create_screen_controls()
layout = MonitorLayout(list(manager.get_friendly_mapping(MONITORSR)), name='ALL')
layout.create_screen_controls()

# Individual and ALL Settings Controls
for m, display_name in manager.get_display_names(MONITORSR).items():
	layout = MonitorLayout([display_name], name=m)
	layout.create_setting_controls()
layout = MonitorLayout(list(manager.get_display_names(MONITORSR).values()), name='ALL')
layout.create_setting_controls()


@StreamDeck(location=[MonitorLayout.BASE + '2,2', MonitorLayout.BASE + 'Settings/2,2'])
def extend():
	controller.set_input_source(Games.shared_monitor, 'mdp')
	controller.extend()

@StreamDeck(location=[MonitorLayout.BASE + '3,2', MonitorLayout.BASE + 'Settings/3,2'])
def duplicate():
	controller.clone()

@register(globals())
class MonitorManagerHelper:
	def _change_all(brightness, contrast, mode='abs'):
		for monitor in MONITORS.values():
			controller.brightness(monitor, brightness, mode=mode)
			controller.contrast(monitor, contrast, mode=mode)

	class Relative:
		x = 10

		@StreamDeck(location=MonitorLayout.BASE + '0,2')
		def less():
			_change_all(-MonitorManagerHelper.Relative.x, -MonitorManagerHelper.Relative.x, mode='rel')

		@StreamDeck(location=MonitorLayout.BASE + '1,2')
		def more():
			_change_all(MonitorManagerHelper.Relative.x, MonitorManagerHelper.Relative.x, mode='rel')
			
	class Absolute:
		@Device(title='0')
		@Scheduler(trigger='daily', start="2022/05/14-23:59")  # Midnight
		@StreamDeck(location=MonitorLayout.BASE + '0,1')
		def to_0():
			_change_all(0, 0)

		@Device(title='30')
		@StreamDeck(location=MonitorLayout.BASE + '1,1')
		def to_30():
			_change_all(30, 30)

		@Device(title='50')
		@Scheduler(trigger='daily', start="2022/05/14-07:30")
		@StreamDeck(location=MonitorLayout.BASE + '2,1')
		def to_50():
			_change_all(50, 50)

		@Device(title='70')
		@StreamDeck(location=MonitorLayout.BASE + '3,1')
		def to_70():
			_change_all(70, 70)

		@Device(title='100')
		@StreamDeck(location=MonitorLayout.BASE + '4,1')
		def to_100():
			_change_all(100, 100)
