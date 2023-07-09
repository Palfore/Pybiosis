import ctypes
import sys
import os

WINDOWS_OS_NAME = 'nt'

class InvalidEnvironment(Exception):
	pass

def require_windows():
	if not os.name == WINDOWS_OS_NAME:
		raise InvalidEnvironment("Must compile on Windows.")

def require_admin():
	if not _user_is_admin():
		raise InvalidEnvironment("Must compile with admin privileges.")

def require_user_path():
	if os.environ.get('PYBIOSIS_USER_PATH') is None:
		raise InvalidEnvironment("Please set the environment variable 'PYBIOSIS_USER_PATH'.")

def _user_is_admin():  # https://stackoverflow.com/questions/1026431/cross-platform-way-to-check-admin-rights-in-a-python-script-under-windows
    try:
        return os.getuid() == 0
    except AttributeError:
        pass
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() == 1
    except AttributeError:
        return False  # If it can't be determined, don't try.
