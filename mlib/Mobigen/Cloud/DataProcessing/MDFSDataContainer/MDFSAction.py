# -*- coding: utf-8 -*-

import sys
import time
from mdfslib.mdfs import MDFSClient
from mdfslib.mdfs_protocol_pb2 import Response

class MDFSAction :

	client = None

	def __init__(self, ip, port, id, pw) :
		self.ip   = ip
		self.port = port
		self.id   = id
		self.pw   = pw

		self.connect()

	def connect(self) :
		while (True) :
			try :
				client = MDFSClient(self.ip, int(self.port))
				client.login(self.id, self.pw)
			except Exception, ex :
				sys.stderr.write("mdfs connect fail.. cause(%s)" % str(ex))
				sys.stderr.flush()
				time.sleep(1)

	def disconnect(self) :
		try : client.close()
		except : pass
		client = None

	def peek(self, path) :
		return client.peek(path)

	def mkdir(self, path) :
		client.mkdir(path)

	def getsize(self, path) :
		return client.getsize(path)

	def ls(self, path) :
		return client.ls(path)

	def rm(self, path) :
		client.rm(path)

	def mv(self, org, new) :
		client.mv(org, new)

	def open(self, file, mode) :
		return client.open(file, mode)


