if __name__ == '__main__':
	from pybiosis.loader import get_user_path
	import pybiosis.validate as validate
	import sys
	import os

	validate.require_user_path()
	sys.path.insert(1, str(get_user_path()))
	os.chdir(get_user_path())

	from driver import main
	main()
