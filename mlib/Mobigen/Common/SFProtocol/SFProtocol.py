#!/usr/bin/python
# -*- coding: UTF-8 -*-

#---------------------------------------------------------------
# version | date : writer : description
#---------------------------------------------------------------
# V1.0    | 061127 : tesse : begin
# V1.1    | 061201 : tesse : add debug and flush mode
# V2.0    | 070414 : tesse : remove buffer concept
# V2.1    | 070620 : jjinylee: read((), check return value 
# V2.2    | 070620 : eek: add my_readline and add readBuf
#---------------------------------------------------------------

import Mobigen.Common.Log as Log; Log.Init()
import sys
from socket import *

SFP_CH_S = 'SFP_CH_S'
SFP_CH_U = 'SFP_CH_U'
SFP_CH_I = 'SFP_CH_I'
SFP_CH_T = 'SFP_CH_T'

SFP_SOCKOPT_SNDBUF = -1 # -1 : system default
SFP_SOCKOPT_RCVBUF = -1 # -1 : system default
SFP_SOCKOPT_MAKEFILEBUF = -1 # -1 : system default

class SFPDiscon(Exception) : pass
class SFPBadFormat(Exception) : pass
class SFPBadPType(Exception) : pass
class SFPBadChType(Exception) : pass

def getOptStr() :
	return 'p:ld'

def prnOpt() :
	print '        -p[pType]     : start protocol type, default=1'
	print '        -l            : flush mode'
	print '        -d            : debug mode'
	print '        -h            : help'

class SFProtocol :

	HEAD = 1
	BODY = 2
	END = 3

	def __init__(self, cType, **opts) :
		self.opts = opts

		# default protocol type 6 -> 1
		try : self.pType = int( opts['-p'] )
		except : self.pType = 1

		self.cType = cType

		self.flushMode = False
		if opts.has_key('-l') : self.flushMode = True

		self.debugMode = False
		if opts.has_key('-d') : self.debugMode = True

		self.fd = ''
		self.sock = ''
		
		self.inbuf = '' # readline buf

		self.stat = SFProtocol.HEAD
		self.remain = 0
		self.tmpList = []

	def setFD(self, fd) :
		if self.cType == SFP_CH_T :
			if SFP_SOCKOPT_SNDBUF >= 0 : sock.setsockopt( SOL_SOCKET, SO_SNDBUF, SFP_SOCKOPT_SNDBUF)
			if SFP_SOCKOPT_RCVBUF >= 0 : sock.setsockopt( SOL_SOCKET, SO_RCVBUF, SFP_SOCKOPT_RCVBUF)

			self.sock = fd
			self.fd = fd
		else :
			self.fd = fd

	def close(self):

		#if self.cType == SFP_CH_T :
		#	self.sock.close()
		#else :
		#	pass

		self.fd.close()

	def readLen(self, size) :

		if not self.remain:
			self.remain = size
			self.tmpList = []
	
		while 1 :
			tmpData = ''
	
			if self.cType == SFP_CH_S :
				tmpData = self.fd.read(self.remain)

			elif self.cType == SFP_CH_T :
				tmpData = self.sock.recv(self.remain)
	
			else :
				raise SFPBadChType, self.cType

			if len(tmpData) == size :
				self.remain = 0
				return tmpData
	
			if tmpData == '' :
				self.remain = 0
				raise SFPDiscon, "disconnect"

			#__LOG__.Trace("remain[%d]tmpData[%d]" % (remain, len(tmpData)))
	
			self.tmpList.append(tmpData)
			self.remain -= len(tmpData)
	

			if self.remain <= 0 : break
	
		self.remain = 0
		str = ''.join(self.tmpList)
		self.tmpList = []
		return str
	

	def my_read_line(self): # socket readline 

		lf = self.inbuf.find('\n')
		if lf >= 0:
			data = self.inbuf[:lf+1]
			self.inbuf = self.inbuf[lf+1:]
			return data

		r = self.sock.recv(4096)
	 	if not r:
			# connection broken
			return ''

		self.inbuf = self.inbuf + r

		lf = self.inbuf.find('\n')
		if lf >= 0:
			data = self.inbuf[:lf + 1]
			self.inbuf = self.inbuf[lf + 1:]

			return data


		# read 했는데 \n이 없는경우.
		raise SFPBadPType, self.pType

	def readBuf(self, **op):

		if self.pType == 1:
			return self.read(**op);

		lf = self.inbuf.find('\n')
		if lf < 0:
			raise timeout, "timeout.dataBuf"

		msg = self.inbuf[:lf+1]
		self.inbuf = self.inbuf[lf+1:]

		if op.has_key('Fast') and op['Fast'] :
			retVal = msg
		else :
			retVal = msg.split( ',', 3 )

		if self.debugMode : __LOG__.Trace( retVal )

		if op.has_key('Fast') and op['Fast'] :
			return retVal

		else :
			if len( retVal ) != 4 : raise SFPBadFormat, retVal

		return retVal

	def read(self, **op) :
		if self.cType == SFP_CH_S or self.cType == SFP_CH_T :
			if self.pType == 1 :

				if self.stat == SFProtocol.HEAD:
					self.header = ""
					self.body = ""

					self.header = self.readLen(16)
					self.stat = SFProtocol.BODY
				else:
					__LOG__.Trace( "[head:%s]" % self.header )

				try :
					bodySize = int( self.header[6:16] )
				except :
					self.stat = SFProtocol.HEAD
					raise SFPBadFormat, self.header[6:16]


				if self.stat == SFProtocol.BODY:
					self.body = self.readLen(bodySize)
					self.stat = SFProtocol.END
				else:
					__LOG__.Trace( "[body:%s]" % self.body )

				if op.has_key('Fast') and op['Fast'] :
					retVal = self.header + self.body
				else :
					retVal = self.header[0], self.header[1:3], \
						self.header[3:6], self.body

				self.stat = SFProtocol.HEAD

			elif self.pType == 6 :


				if self.cType == SFP_CH_T :
					msg = self.my_read_line()
				else:
					msg = self.fd.readline()

				if msg == '' : raise SFPDiscon, "disconnect"

				if op.has_key('Fast') and op['Fast'] :
					retVal = msg
				else :
					retVal = msg.split( ',', 3 )

			else :
				raise SFPBadPType, self.pType
	
		elif self.cType == SFP_CH_U or self.cType == SFP_CH_I:
			msg = self.fd.recv(64000)
			if msg == '' : raise SFPDiscon, "disconnect"
	
			if op.has_key('Fast') and op['Fast'] :
				retVal = msg

			else :
				if self.pType == 1 :
					retVal = msg[0], msg[1:3], msg[3:6], msg[16:]
	
				elif self.pType == 6 :
					retVal = msg.split( ',', 3 )

				else :
					raise SFPBadPType, self.pType
	
		else :
			raise SFPBadChType, self.cType
	
		if self.debugMode : __LOG__.Trace( retVal )

		if op.has_key('Fast') and op['Fast'] :
			return retVal

		else :
			if len( retVal ) != 4 :
				raise SFPBadFormat, retVal

		return retVal

	
	def flush(self) :
		try :
			if self.cType == SFP_CH_T :
				self.fd.sendall('')
	
			elif self.cType == SFP_CH_S :
				self.fd.flush()
	
		except Exception, err :
			if self.debugMode : __LOG__.Exception()
			raise SFPDiscon, "disconnect"

	def write( self, rsv, cmd, msg, **op ) :
		if op.has_key('Fast') and op['Fast'] :
			data = msg # \n included in msg
	
		elif self.pType == 1 :
			data = '%s% -2s% -3s%010d%s' % (self.pType, rsv, cmd, len(msg), msg)
	
		elif self.pType == 6 :
			data = '%s,% -2s,% -3s,%s' % (self.pType, rsv, cmd, msg) # \n included in msg
	
		else :
			raise SFPBadPType, self.pType
	
		if self.debugMode : __LOG__.Watch(data)

		if self.cType == SFP_CH_T :
			if self.flushMode :
				self.sock.sendall(data)
				self.sock.sendall('')
			else :
				self.sock.send(data)

		elif self.cType == SFP_CH_S :
			self.fd.write(data)
			if self.flushMode :	self.fd.flush()

		elif self.cType == SFP_CH_U or self.cType == SFP_CH_I :
			if self.flushMode :
				self.fd.sendall(data)
			else :
				self.fd.send(data)

		else :
			raise SFPBadChType, self.cType
