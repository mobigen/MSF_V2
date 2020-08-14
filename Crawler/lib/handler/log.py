import os
import time
from lib.interface.ihandler import ihandler
import json
import logging

logger = logging.getLogger(__name__)

class LogHandler(ihandler):
	def __init__(self, *args, **kwargs):
		super(LogHandler, self).__init__(*args, **kwargs)
		self.setName('LogHandler')

	def run(self):
		self.isruning = True
		self.parent.writeLog(self, "---- LogHandler Start ----")
		while self.isruning:
			try:

				time.sleep(1)
			except Exception as ex:
				logger.error("LogHandler Exception : %s", str(ex))
				self.parent.writeLog(self, str('Exception -> %s' % ex))
				self.stop_handler()

	def stop_handler(self):
		try:
			self.isruning = False
			self.parent.writeLog(self, "---- LogHandler Stop ----")
			self.parent.end()
			
		except Exception as ex:
			return False
		return True
