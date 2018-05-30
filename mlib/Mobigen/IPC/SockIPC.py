#!/usr/bin/python
# -*- coding: cp949 -*-

import time, os, sys, threading, struct, collections, tempfile, cPickle
from socket import *

VERSION = '1.5'

# V1.4 : 051111 : add RecvPort=None option
# V1.5 : 051117 : add PortAlreadyIGN option

MAX_BUF = 1000000
TMP_DIR = '/tmp/mobigen'

class NoDataException(Exception) : pass

class SockIPC :

	def __init__(self, **args) :
		# NAMED_PIPE / UNIX_DOMAIN_SOCKET
		try : self.RecvType = args['RecvType']
		except : self.RecvType = "UNIX_DOMAIN_SOCKET"

		try : self.tmpDir = args['TmpDir']
		except : self.tmpDir = TMP_DIR

		try : os.mkdir(self.tmpDir)
		except : pass

		try :
			if args['RecvPort'] :
				self.recvPort = '%s/%s' % (self.tmpDir, args['RecvPort'])
			else :
				self.recvPort = None

		except :
			tempfile.tempdir = self.tmpDir
			self.recvPort = tempfile.mktemp()

		try :
			if args['SendPort'] :
				self.sendPort = '%s/%s' % (self.tmpDir, args['SendPort'])
			else :
				self.sendPort = None

		except :
			tempfile.tempdir = self.tmpDir
			self.sendPort = tempfile.mktemp()

		try : self.sendFailIGN = args['SendFailIGN']
		except : self.sendFailIGN = False

		# try : self.nonBlock = args['NonBlock']
		# except : self.nonBlock = False

		try : self.maxBuf = args['MaxBuf']
		except : self.maxBuf = MAX_BUF

		try : self.size = args['Size']
		except : self.size = 0

		try : self.delimeter = args['Delimeter']
		except : self.delimeter = '|'

		try : self.portAlreadyIGN = args['PortAlreadyIGN']
		except : self.portAlreadyIGN = False

		self.bPIPE = False
		if self.recvPort :
			if self.portAlreadyIGN :
				try : os.unlink(self.recvPort)
				except : pass
			if(self.RecvType == "UNIX_DOMAIN_SOCKET") :
				self.recvSock = socket(AF_UNIX, SOCK_DGRAM)
				self.recvSock.bind(self.recvPort)
				self.bPIPE = False
			elif(self.RecvType == "NAMED_PIPE") :
				try : os.mkfifo(self.recvPort)
				except : pass
				self.recvSock = open(self.recvPort, "r")
				self.bPIPE = True


		if(self.RecvType == "NAMED_PIPE_WRITE") :
			if self.sendPort : 
				try : os.mkfifo(self.sendPort)
				except : pass
				self.sendSock = os.open(self.sendPort, os.O_WRONLY);
				self.bPIPE = True
		else :
			self.sendSock = socket(AF_UNIX, SOCK_DGRAM)

	def dump(self, obj, fileName) :
		cPickle.dump( obj, open( fileName+'.tmp', 'w' ) )
		os.rename( fileName+'.tmp', fileName )

	def load(self, fileName) :
		return cPickle.load( open(fileName) )

	def sendFast(self, sendPort, cmd, key, val) :
		msg = '%s%s%s%s%s%s%s' % (self.recvPort, self.delimeter, \
			cmd, self.delimeter, key, self.delimeter, val)

		if(self.bPIPE) :
			os.write(self.sendSock, msg + "\n")
		else :
			if self.sendFailIGN :
				try : self.sendSock.sendto(msg, sendPort)
				except : pass
			else :
				self.sendSock.sendto(msg, sendPort)
		
	def send(self, sendPort, *args) :
		msg = struct.pack('!I', len(self.recvPort)) + self.recvPort

		for arg in args :
			arg = str(arg)
			msg += struct.pack('!I', len(arg)) + arg

		if self.sendFailIGN :
			try : self.sendSock.sendto(msg, sendPort)
			except : pass
		else :
			self.sendSock.sendto(msg, sendPort)

	def recvFast(self) :
		if(self.bPIPE) :
			msg = self.recvSock.readline()
			msg = msg[:-1]
			if(len(msg)==0) :
				raise NoDataException
		else :
			msg, addr = self.recvSock.recvfrom(self.maxBuf)
		return msg.split(self.delimeter, 3)
		
	def recv(self) :
		if(self.bPIPE) :
			msg = self.recvSock.readline()
			msg = msg[:-1]
		else :
			msg, addr = self.recvSock.recvfrom(self.maxBuf)

		retList = []
		offset = 0 
		while 1 :
			tmpLen, = struct.unpack('!I', msg[ offset:offset+4 ])
			offset += 4
			retList.append( msg[ offset:offset+tmpLen ] )
			offset += tmpLen
			
			if offset >= len(msg) : break

		return retList

	def close(self) :
		if(self.RecvType == "NAMED_PIPE_WRITE") :
			try : self.recvSock.close()
			except : pass
			try : os.close(self.sendSock)
			except : pass
		else :
			try : os.unlink(self.recvPort)
			except : pass

	def __del__(self) :
		self.close()
