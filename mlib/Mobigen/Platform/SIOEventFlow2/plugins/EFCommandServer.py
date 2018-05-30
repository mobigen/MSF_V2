#!/usr/bin/env pypy

import sys
import select
import socket

class EFCommandServer :
	
	def __init__(self, someCore, host, port, **opt) :
		self.someCore = someCore
		self.host = host
		self.port = port
		try: self.mode = opt["mode"]
		except: self.mode = "stdio"

		self.sock_list = []
		self.client_hash = {}

		self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.listen_sock.bind((self.host, self.port))
		self.listen_sock.listen(100)

		self.sock_list.append(self.listen_sock)
		self.sock_list.append(sys.stdin)
		self.client_hash[sys.stdin] = sys.stdin


	def __del__(self) :
		for sock in self.sock_list :
			self.close(sock)


	def close(self, sock) :
		self.sock_list.remove(sock)

		try : self.client_hash[sock].close()
		except : pass

		try : sock.close()
		except : pass

		try : del(self.client_hash[sock])
		except : pass


	def stdout(self) :

		while (True) :
			try:
				input, output, exception = select.select(self.sock_list, [], [], 1)
	
				if (len(input) == 0) : continue
	
				for sock in input :
					if (sock == self.listen_sock) :
						client, addr = self.listen_sock.accept()
						self.sock_list.append(client)
						self.client_hash[client] = client.makefile()
					else :
						try :
							line = self.client_hash[sock].readline()
							if (line == "") : raise Exception
						except :
							self.close(sock)
							continue
	
						if (line[:3].upper() == "BYE") :
							self.close(sock)
							continue
						
						elif (line[:3].upper() == "KIL") :
							raise Exception
	
						else :
							ans = self.someCore.stdio(line)

							try:
								if sock == sys.stdin:
									if self.mode == "stdio":
										if ans != None:
											yield ans
									elif self.mode == "sync":
										pass
									
								else:
									if ans != None:
										sock.send(ans)
	
									if self.mode == "sync":
										yield line
							except :
								self.close(sock)
								
			except:
				break

		for sock in self.sock_list :
			self.close(sock)

if __name__ == "__main__" :
	if len(sys.argv) < 3 :
		print "usage : %s ip port [sync]" % (sys.argv[0])
		sys.exit()
	
	ip = sys.argv[1]
	port = int(sys.argv[2])
	try: modeVal = sys.argv[3]
	except: modeVal = 'stdio'

	class SomeCore:
		def __init__(self):
			pass

		def stdio(self, msg):
			return "ans : %s" % msg

	sc = SomeCore()
	cs = EFCommandServer( sc, ip, port, mode=modeVal )
	for line in cs.stdout():
		sys.stdout.write(line)
		sys.stdout.flush()
