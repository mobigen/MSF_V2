import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from lib.rpc.common import Common, Management, Schedule
from spyne.server.zeromq import ZeroMQServer
import threading

from wsgiref.simple_server import make_server
from spyne.server.wsgi import WsgiApplication

import logging

logger = logging.getLogger(__name__)

class Server(threading.Thread):
	def __init__(self, parent: object = None, ip: str = '0.0.0.0', port: str = '0'):
		threading.Thread.__init__(self)
		try:
			self.parent = parent
			protocol = 'tcp'
			if self.parent.type.lower() == 'management' or self.parent.type.lower() == 'schedule':
				protocol = 'http'
			self.url = str("%s://%s:%s" % (protocol, ip, port))

			self.service = None
			if self.parent.type.lower() == 'management':
				wsgi_application = WsgiApplication(Management)
				self.server = make_server(ip, int(port), wsgi_application)
				self.service = self.server.application.app.services[0]
				self.service.handler = parent
			elif self.parent.type.lower() == 'schedule':
				wsgi_application = WsgiApplication(Schedule)
				self.server = make_server(ip, int(port), wsgi_application)
				self.service = self.server.application.app.services[0]
				self.service.handler = parent
			else:
				self.server = ZeroMQServer(Common, self.url)
				self.service = self.server.app.services[0]
				self.service.handler = parent
		except Exception as ex:
			logger.error("RPC Server Exception : %s", str(ex))
			self.parent.parent.writeLog(self, str("---- %s Handler RPC Server (%s) Exception ----" % (self.parent.type, self.url)))
			pass

	def run(self):
		try:
			self.parent.parent.writeLog(self, str("---- %s Handler RPC Server Running (%s) ----" % (self.parent.type, self.url)))
			self.server.serve_forever()
		except Exception as ex:
			logger.error("RPC Server Exception : %s", str(ex))
			self.parent.parent.writeLog(self, str("---- %s Handler RPC Server (%s) Exception ----" % (self.parent.type, self.url)))
			pass
