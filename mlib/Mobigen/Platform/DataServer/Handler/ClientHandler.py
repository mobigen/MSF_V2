# encoding: utf-8
"""
ClientHandler.py

Copyright (c) 2012 Mobigen. All rights reserved.
"""

import os
import socket
from Dao import *
from Modules.Exception import *
import Mobigen.Common.Log as Log; Log.Init()

class ClientHandler :

	def __init__(self, sock, conf, addr) :
		self.sock = sock
		self.conf = conf
		self.address = addr
		
	def init(self) :
		# self.dao = DummyDao(self.conf)
		self.dao = IRISDao(self.conf)

	def start(self) :
		
		self.init()
		
		self.sockfd = self.sock.makefile()

		lineBuffer = []
		
		while (True) :
	#	{
			line = self.sockfd.readline()
			if (line == None or line == "") :
				break
			
			if (line.startswith("<begin>") or \
				line.startswith("<end>")) :
				lineBuffer.append(line.strip())
			else :
				lineBuffer.append(line)
			
			if (not line.startswith("<end>")) :
				continue

			try:
				beginIndex = lineBuffer.index("<begin>")
				endIndex = lineBuffer.index("<end>")
			except:
				__LOG__.Exception()
				self.writeError("invalid command.")
				lineBuffer = []
				continue
				
			request = "".join(lineBuffer[beginIndex+1:endIndex])
			lineBuffer = []
			
			__LOG__.Trace("%s : request [ %s ]" % (self.address, request))
			
			request = request.split(":", 3)
			
			requestCmd = ""
			requestStart = ""
			requestCount = ""
			requestSql = ""
			
			if (len(request) == 1) :
				requestCmd = request[0]
			elif (len(request) == 2) :
				requestCmd, requestSql = request
			elif (len(request) == 4) :
				requestCmd, requestStart, requestCount, requestSql = request
			else :
				self.writeError("invalid command.")
				continue
			
			requestCmd = requestCmd.strip().upper()
			
			if (requestCmd == "QUERY") :
				self.QUERY(requestStart, requestCount, requestSql)
			elif (requestCmd == "DOWNLOAD") :
				self.DOWNLOAD(requestSql)
			elif (requestCmd == "CLOSE") :
				break
			else :
				self.writeError("invalid command.")
	#	}

		try:
			self.sockfd.close()
			self.sockfd = None
			self.sock.shutdown(socket.SHUT_RDWR)
			self.sock = None
		except:
			pass
			
		try:
			self.dao.close()
		except:
			pass


	def QUERY(self, requestStart, requestCount, query):
		try: requestStart = int(requestStart)
		except: requestStart = 1
			
		try: requestCount  = int(requestCount)
		except: requestCount = None
		
		self.writeLine("<begin>")
		
		try :
			res = self.dao.query(requestStart, requestCount, query)
			for data in res :
				self.writeLine(data)
		except IRISConnectException :
			self.writeLine("-ERR IRIS connect error.")
		except DataNotFoundException :
			self.writeLine("-ERR Data not found.")
		except Exception, ex :
			self.writeLine("-ERR " + str(ex))
			
		self.writeLine("<end>")
		
	def DOWNLOAD(self, query):
		self.writeLine("<begin>")
		
		try : 
			res = self.dao.download(query)
			self.writeLine("+OK " + res)
		except IRISConnectException :
			self.writeLine("-ERR IRIS connect error.")
		except Exception, ex :
			self.writeLine("-ERR " + str(ex))
			
		self.writeLine("<end>")
	
	def writeLine(self, msg) :
		self.sock.sendall(msg + "\r\n")
		
	def writeError(self, msg) :
		self.writeLine("<begin>")
		self.writeLine("-ERR %s" % msg)
		self.writeLine("<end>")