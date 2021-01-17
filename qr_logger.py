import logging
import os


#'%(name)s - %(levelname)s : %(message)s'
def create_or_get_logger(filename):
	if os.path.exists(filename):
		logging.basicConfig(filename=filename, filemode='a', format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',)
	else:
		logging.basicConfig(filename=filename, filemode='w', format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',)

	logging.getLogger(__name__)
	logging.debug(f'This will get logged to a {filename} file')
	return logging









