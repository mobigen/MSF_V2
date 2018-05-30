#!/bin/env python
# coding: utf-8

import socket, struct, errno
import Mobigen.Common.Log as Log; Log.Init()


class Socket(object) :
	class SocketDisconnectException(Exception) : pass
	class SocketDataSendException(Exception) : pass
	class SocketTimeoutException(Exception) : pass

	def __init__(self) :
		object.__init__(self)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		linger = struct.pack( "ii", 1, 0 )
		self.sock.setsockopt( socket.SOL_SOCKET, socket.SO_LINGER, linger )

		self.remain = 0
		self.tmpList = []
		self.addr = ""
		self.inbuf = ""
		self.isConnect = False

	def Connect(self, ip, port) :

		if not self.isConnect:
			self.sock.connect((ip, int(port)))
			self.setSock(self.sock)

	def Bind(self, port):
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind( ("", int(port)) )
		self.sock.listen(1000)

		self.setSock(self.sock)

	def Accept(self):
		(cSock, addr) =  self.sock.accept()
		c = Socket()
		c.setSock(cSock)
		c.addr = addr
		return c

	def setSock(self, sock):
		self.sock = sock
		self.isConnect = True

	#######################################################
	#
	# 한줄 단위로 Return
	#
	def Readline(self, modeBlock=True, timeOut=0) :
		#__LOG__.Trace("ReadLine S")
		data = ""
		local_sock  = self.sock
		local_inbuf = self.inbuf

		lf = local_inbuf.find('\n')
		if lf >= 0:
			data = local_inbuf[:lf+1]
			local_inbuf = local_inbuf[lf+1:]
			self.inbuf = local_inbuf
			self.sock  = local_sock
			return data

		# 블럭 모드에서도 타임아웃 사용할 수 있도록 수정.
		#if not modeBlock and timeOut > 0:
		if timeOut > 0:
			local_sock.settimeout(timeOut)
		else:
			local_sock.settimeout(None)

		while True:
			#__LOG__.Trace("Recv S")
			try : r = local_sock.recv(1024*2000)
			except socket.timeout:
				self.inbuf = local_inbuf
				self.sock  = local_sock
				raise Socket.SocketTimeoutException
			except socket.error, e:
				if e.args[0] == errno.ECONNRESET:
					self.inbuf = local_inbuf
					self.sock  = local_sock
					raise Socket.SocketDisconnectException
			#__LOG__.Trace("Recv E")
			if not r:
				self.inbuf = local_inbuf
				self.sock  = local_sock
				# connection broken
				# disconnect
				local_sock.settimeout(None)
				raise Socket.SocketDisconnectException
		
			local_inbuf = local_inbuf + r
	
			lf = r.find('\n')
			if lf >= 0:
				lf = local_inbuf.find('\n')
				data = local_inbuf[:lf + 1]
				local_inbuf = local_inbuf[lf + 1:]
				break

			# 함수가 Non-Block Mode 로 동작하는 경우 리턴
			if not modeBlock : break

		local_sock.settimeout(None)
		self.inbuf = local_inbuf
		self.sock  = local_sock

		return data

	def Read(self, size, modeBlock=True, timeOut=0) :
		#__LOG__.Watch((size, len(self.inbuf)))

		self.remain = size

		tmpData = ""
		self.tmpList = []

		if len(self.inbuf) > 0:
			#__LOG__.Watch((self.remain, len(self.inbuf)))
			if self.remain > len(self.inbuf):
				self.remain = self.remain - len(self.inbuf)
				self.tmpList.append( self.inbuf )
				self.inbuf = ""
			else :  #  <=
				tmpData = self.inbuf[:self.remain]
				self.inbuf = self.inbuf[self.remain:]
				return tmpData

		#print dir(self.sock)

		if not modeBlock and timeOut > 0:
			self.sock.settimeout(timeOut)
		else:
			self.sock.settimeout(None)

		while 1 : 
			tmpData = ''
			try: tmpData = self.sock.recv(self.remain)
			except socket.timeout:
				raise Socket.SocketTimeoutException
			except socket.error, e:
				if e.args[0] == errno.ECONNRESET:
					raise Socket.SocketDisconnectException
			#__LOG__.Watch((len(tmpData), self.remain))

			if tmpData == "":
				# connection broken
				# disconnect
				self.sock.settimeout(None)
				raise Socket.SocketDisconnectException

			self.tmpList.append(tmpData)
			self.remain -= len(tmpData)

			# 정상적인 경우
			if self.remain <= 0: break

		self.remain = 0
		str = ''.join(self.tmpList)
		self.tmpList = []

		self.sock.settimeout(None)

		return str

	def ReadMessage(self) :
		line = self.Readline()
		(code, msg) = line.split(" ", 1)

		if   code[0] == "+":
			return (True, msg)
		else:
			return (False, msg)

	def SendMessage(self, cmd, timeOut=0) :

		if timeOut > 0:
			self.sock.settimeout(timeOut)
		else:
			self.sock.settimeout(None)

		while True:
			n =  self.sock.send(cmd)
			if n == len(cmd):
				break;
			elif n <= 0:
				self.sock.settimeout(None)
				raise Socket.SocketDataSendException

			cmd = cmd[n:]

		self.sock.settimeout(None)

	def close(self):
		self.sock.close()
		self.isConnect = False
	"""
	def shutdown(self, num=2):
		self.sock.shutdown(num)
	"""
def server():
	s = Socket()
	s.Bind(9999)

	client_sock = s.Accept()

	client_sock.SendMessage("+OK Hello World!!!!\r\n")

	while True:
		msg = client_sock.Readline()
		client_sock.SendMessage("+OK %s" %msg )
		if msg.strip().upper() == "QUIT":
			break

	client_sock.close()
	s.close()


def client():
	s = Socket()
	s.Connect("localhost", 9999)
	print s.ReadMessage()
	s.SendMessage("GET\r\n")
	print s.ReadMessage()
	s.close()


if __name__ == "__main__":
	#client()
	server()
