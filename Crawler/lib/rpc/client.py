import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from lib.rpc.common import Common
from spyne.client.zeromq import ZeroMQClient
import threading
import time

import zmq

from spyne import RemoteService, ClientBase, RemoteProcedureBase

import logging

logger = logging.getLogger(__name__)

context = zmq.Context()


class _RemoteProcedure(RemoteProcedureBase):
	def __call__(self, *args, **kwargs):
		self.ctx = self.contexts[0]

		self.get_out_object(self.ctx, args, kwargs)
		self.get_out_string(self.ctx)
		out_string = b''.join(self.ctx.out_string)

		socket = context.socket(zmq.REQ)
		socket.setsockopt(zmq.LINGER, 0)
		socket.connect(self.url)
		socket.send(out_string)

		poller = zmq.Poller()
		poller.register(socket, zmq.POLLIN)

		if poller.poll(3 * 1000):  # 10s timeout in milliseconds
			self.ctx.in_string = [socket.recv()]
			self.get_in_object(self.ctx)
		else:
			logger.error("Timeout processing auth request - %s" % self.url)
		if not (self.ctx.in_error is None):
			logger.error("RPC Client  Exception : %s", str(self.ctx.in_error))
		else:
			return self.ctx.in_object


class mZeroMQClient(ClientBase):
	def __init__(self, url, app):
		super(mZeroMQClient, self).__init__(url, app)
		self.service = RemoteService(_RemoteProcedure, url, app)


class Client:
	def __init__(self, parent: object = None, ip: str = '0.0.0.0', port: str = '0'):
		try:
			self.parent = parent
			self.url = str("tcp://%s:%s" % (ip, port))
			self.client = mZeroMQClient(self.url, Common)

			self.service = self.client.service
			self.parent.parent.writeLog(self, str("---- %s Handler RPC Connect to (%s) ----" % (self.parent.type, self.url)))
			self.is_connected = False

			handler = ClientHandler(parent=self)
			handler.start()

		except Exception as ex:
			logger.error("RPC Client  Exception : %s", str(ex))
			self.parent.parent.writeLog(self, str("---- %s Handler RPC Client (%s) Exception ----" % (self.parent.type, self.url)))
			pass


class ClientHandler(threading.Thread):
	def __init__(self, parent: object = None):
		threading.Thread.__init__(self)
		self.parent = parent

	def run(self):
		self.isruning = True
		while self.isruning:
			if self.parent.service.check_alive():
				self.parent.is_connected = True
			else:
				self.parent.is_connected = False
			time.sleep(1)
