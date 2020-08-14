import os
import time
from lib.interface.ihandler import ihandler
import json
import logging

logger = logging.getLogger(__name__)


class ManagementHandler(ihandler):
	def __init__(self, *args, **kwargs):
		super(ManagementHandler, self).__init__(*args, **kwargs)
		self.setName('ManagementHandler')

	def run(self):
		self.isruning = True
		self.parent.writeLog(self, "---- ManagementHandler Start ----")
		while self.isruning:
			try:
				self.rpc_server.service.management.handlers = [c.service for c in self.rpc_clients if c.is_connected]
				time.sleep(1)
			except Exception as ex:
				logger.error("ManagementHandler Exception : %s", str(ex))
				self.parent.writeLog(self, str('Exception -> %s' % ex))
				self.stop_handler()

	def stop_handler(self):
		try:
			self.isruning = False
			self.parent.writeLog(self, "---- ManagementHandler Stop ----")
			self.parent.end()

		except Exception as ex:
			return False
		return True
