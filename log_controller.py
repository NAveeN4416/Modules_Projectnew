class Initiate_logging:

	def __init__(self,file_name,level):

		import logging
		from django.conf  import settings

		self.filename = f"{file_name}.log"

		self.logger = logging.getLogger(self.filename)
		self.logger.setLevel(level)

		#Create formatter object
		formatter = logging.Formatter('%(asctime)s : %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')

		#File Handler
		filehandler = logging.FileHandler(self.filename)
		filehandler.setFormatter(formatter)

		# mailhandler = logging.handlers.SMTPHandler(mailhost=settings.EMAIL_HOST,
		# 										   fromaddr='DjangoModules@gmail.com',
		# 										   toaddrs= [settings.ADMIN_MAIL],
		# 										   subject="INFO from DJANGO Modules",
		# 										   credentials = (settings.EMAIL_HOST_USER,settings.EMAIL_HOST_PASSWORD),
		# 										   secure=None
		# 										   )


		self.logger.addHandler(filehandler)
		#self.logger.addHandler(mailhandler)


	def Track(self):
		return self.logger


# def Initiate_logging(file_name,level=10):

# 	import logging

# 	filename = f"{file_name}.log"

# 	logger = logging.getLogger(filename)
# 	logger.setLevel(level)

# 	#Create formatter object
# 	formatter = logging.Formatter('%(asctime)s : %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')

# 	#File Handler
# 	filehandler = logging.FileHandler(filename)
# 	filehandler.setFormatter(formatter)


# 	logger.addHandler(filehandler)

# 	#logging.basicConfig(filename=filename,level=logging.INFO,format='%(asctime)s : %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')

# 	return logger