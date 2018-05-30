# encoding: utf-8
"""
AsyncServer.py

Copyright (c) 2012 Mobigen. All rights reserved.
"""

import time
import socket
import struct
import threading
import Handler
import Mobigen.Common.Log as Log; Log.Init()

class AsyncChannel(threading.Thread) :

	def __init__(self, sock, addr, user_handle) :
		threading.Thread.__init__(self)

		self.address = addr
		self.sock = sock
		self.user_handle = user_handle
		self.handle_type = ""
		
		if (isinstance(self.user_handle, Handler.ClientHandler)) :
			self.handle_type = "service"
		elif (isinstance(self.user_handle, Handler.MasterHandler)) :
			self.handle_type = "master"
			
		__LOG__.Trace("%s : %s channel create." % (self.address, self.handle_type))

	def close(self):
		if (self.sock != None):
			__LOG__.Trace("%s : %s channel close." % (self.address, self.handle_type))
			try: self.sock.shutdown(socket.SHUT_RDWR)
			except: pass
			self.sock = None

	def run(self):

		try: self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
		except: pass

		# self.user_handle.thread_id = self.getName()
		
		self.user_handle.start()

		self.user_handle = None

		self.close()



class AsyncServer(threading.Thread) :

	def __init__(self, server_port, RequestHandlerClass, conf) :
		threading.Thread.__init__(self)

		self.RequestHandlerClass = RequestHandlerClass
		self.conf = conf

		self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.socket.bind(('', server_port))
		self.socket.listen(1000)

	def loop(self) :
		
		while (True) :
			try :
				request, client_addr = self.socket.accept()
			except :
				__LOG__.Exception()
				continue

			try:
				handle = \
					self.RequestHandlerClass(request, self.conf, client_addr)
				channel = AsyncChannel(request, client_addr, handle)
				channel.setDaemon(True)
				channel.start()
			except:
				__LOG__.Exception()
				try: request.close()
				except: pass
				request = None
				time.sleep(1)

	def run(self) :
		self.loop()
