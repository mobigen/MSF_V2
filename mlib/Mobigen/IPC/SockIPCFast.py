#!/usr/bin/python
# -*- coding: cp949 -*-

import time, os, sys, threading, struct, collections, tempfile
from socket import *

VERSION = '1.0'

MAX_BUF = 1000000
TMP_DIR = '/tmp/mobigen'

class SockIPC :

	def __init__(self, **args) :
		try : self.tmpDir = args['TmpDir']
		except : self.tmpDir = TMP_DIR

		try : os.mkdir(self.tmpDir)
		except : pass

		try :
			self.recvPort = '%s/%s' % (self.tmpDir, args['RecvPort'])
		except :
			tempfile.tempdir = self.tmpDir
			self.recvPort = tempfile.mktemp()

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

		self.recvSock = socket(AF_UNIX, SOCK_DGRAM)
		self.recvSock.bind(self.recvPort)

		self.sendSock = socket(AF_UNIX, SOCK_DGRAM)

	def sendFast(self, sendPort, cmd, key, val) :
		msg = '%s%s%s%s%s%s%s' % (self.recvPort, self.delimeter, \
			cmd, self.delimeter, key, self.delimeter, val)

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
		msg, addr = self.recvSock.recvfrom(self.maxBuf)
		return msg.split(self.delimeter, 3)
		
	def recv(self) :
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
		try : os.unlink(self.recvPort)
		except : pass

	def __del__(self) :
		self.close()
