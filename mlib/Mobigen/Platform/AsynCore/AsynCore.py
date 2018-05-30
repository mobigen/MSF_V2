#!/bin/env python

import asyncore, socket, sys, ConfigParser, threading
import __main__

class AsynCoreHandler(asyncore.dispatcher_with_send):

	def __init__(self, sock, addr, someCore) :
		asyncore.dispatcher_with_send.__init__(self, sock)
		self.someCore = someCore
		self.addr = addr
		self.fd = self.makefile()

	def handle_read(self):
		line = self.fd.readline()
		if line == "" :
			self.close()
			return

		try :
			if line[:3].upper() == "BYE" :
				self.close()
				return

			ansStr = self.someCore.sfio(line)
			if line[:3].upper() == "KIL" :
				sys.exit()

			if ansStr :
				self.send( ansStr )
			else :
				return

		except IndexError :
			return
	
	def __del__(self) :
		sys.stderr.write( 'Connection closed %s\n' % repr(self.addr) )

class AsynCore(asyncore.dispatcher):

	def __init__(self, host, port, confFileName):
		asyncore.dispatcher.__init__(self)
		self.someCore = __main__.SomeCore(confFileName)

		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind((host, port))
		self.listen(5)

	def handle_accept(self):
		pair = self.accept()
		if pair is None:
			pass
		else:
			sock, addr = pair
			sys.stderr.write( 'Incoming connection from %s\n' % repr(addr) )
			handler = AsynCoreHandler(sock, addr, self.someCore)

if __name__ == "__main__" :

	class SomeCore(threading.Thread) :
		def __init__(self, confFileName) :
			threading.Thread.__init__(self)

			confFile = ConfigParser.ConfigParser()
			confFile.read( confFileName )
		
			self.cmdHash = {}
			for cmdName, cmdClass in confFile.items("AsynCore Command") :
				self.cmdHash[cmdName.upper()] = cmdClass

		def sfio(self, sfin) :
			try :
				cmd = sfin[:3].upper()
			except IndexError :
				return None

			try :
				if self.cmdHash[cmd] == "0" :
					sys.stdout.write(sfin)
					sys.stdout.flush()
					return None
	
				elif self.cmdHash[cmd] == "1" :
					sys.stdout.write(sfin)
					sys.stdout.flush()
					return sys.stdin.readline()
	
				elif self.cmdHash[cmd] == "2" :
					sys.stdout.write(sfin)
					sys.stdout.flush()
	
					retStrList = []
					while True :
						line = sys.stdin.readline()
						if line == "\n" :
							break
						retStrList.append(line)
					return "".join( retStrList )
	
				else :
					return None

			except KeyError :
				return None

	if len(sys.argv) != 4 :
		print "usage : %s ip port confFileName" % sys.argv[0]
		sys.exit(0)

	ip = sys.argv[1]
	port = int(sys.argv[2])
	confFileName = sys.argv[3]
	
	server = AsynCore(ip, port, confFileName)
	asyncore.loop()
