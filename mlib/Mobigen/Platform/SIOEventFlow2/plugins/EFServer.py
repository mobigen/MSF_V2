#!/usr/bin/env python

import sys
import select
import socket
import traceback

class EFServer() :
	
	def __init__(self, host, port, **opt) :
		self.host = host
		self.port = port

		self.sock_list = []
		self.client_hash = {}

		self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.listen_sock.bind((self.host, self.port))
		self.listen_sock.listen(1000)

		self.sock_list.append(self.listen_sock)


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


	def stdio(self, itr=None) :

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
							self.client_hash[sock].write('+OK\r\n')
							self.client_hash[sock].flush()
							yield line
			except:
				traceback.print_exc()
				break

		for sock in self.sock_list :
			self.close(sock)



if __name__ == "__main__" :
	if len(sys.argv) != 3 :
		print "usage : %s ip port" % (sys.argv[0])
		sys.exit()
	
	ip = sys.argv[1]
	port = int(sys.argv[2])
	sockQ = EFServer( ip, port )

	for line in sockQ.stdio():
		sys.stdout.write(line)
		sys.stdout.flush()
