if __name__ == '__main__':
	import sys
	import os
	user_path = os.environ.get('PYBIOSIS_USER_PATH')
	if user_path is not None:
		sys.path.insert(1, user_path)
	else:
		raise ValueError("Please set the environment variable 'PYBIOSIS_USER_PATH'.")

	from driver import main
	main()