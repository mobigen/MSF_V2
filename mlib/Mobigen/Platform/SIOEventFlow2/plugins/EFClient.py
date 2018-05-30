#!/usr/bin/env pypy

import sys
import socket
import time
import traceback

class EFClient() :
	
	def __init__(self, host, port, **opt) :
		self.host = host
		self.port = port

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.host, self.port))
		self.sock.settimeout(10)
		self.fd = self.sock.makefile('r', -1)


	def __del__(self) :
		try: self.close()
		except: pass


	def stdin(self, itr) :
		try :
			for line in itr :
				if line == "" :
					break

				self.sock.send(line)

				if self.sock.recv(1024) == '+OK\r\n' :
					sys.stderr.write(line)
					sys.stderr.flush()

				else : 
					sys.stderr.write('Socket Send Fail : %s\n' % repr(line))
					sys.stderr.flush()
					break

				if line[:3].upper() == "BYE" or line[:3].upper() == "KIL" :
					break
					
		except :
			traceback.print_exc()
			pass

		try : self.sock.send("BYE\n")
		except : pass

		try : self.close()
		except : pass



if __name__ == "__main__" :
	if len(sys.argv) != 3 :
		print "usage : %s ip port" % (sys.argv[0])
		sys.exit()
	
	ip = sys.argv[1]
	port = int(sys.argv[2])
	cli = EFClient( ip, port )
	cli.stdin( iter(sys.stdin.readline,"") )
