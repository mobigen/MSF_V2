#!/bin/env python
#coding: utf-8

import sys
import socket
import threading

BUF_SIZE = 1024

class Client(threading.Thread):
	
	def __init__(self, host, port, line):
		threading.Thread.__init__(self)	
		self.host = host
		self.port = port
		self.line = line

	def run(self):	
		try:	
			protocol, file_path = line.strip().split("://")
			if protocol != "file":
				return

			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((self.host, self.port))
			sock_file = sock.makefile()
		
			sock_file.write(self.line)
			sock_file.flush()

			with open(file_path) as in_file:
				
				buf = in_file.read(BUF_SIZE)
				while buf:
					sock_file.write(buf)
					buf = in_file.read(BUF_SIZE)

				sock_file.flush()
				sock.shutdown(socket.SHUT_WR)	

			if sock_file.read() == "FIN":
				sys.stderr.write(self.line)
				sys.stderr.flush()
				
		except:
			print sys.exc_info()[0]
			pass
		finally:	
			try: sock.close()
			except: pass

if __name__ == "__main__" :
	if len(sys.argv) != 3 :
		print "usage : %s host port" % (sys.argv[0])
		sys.exit()
	
	host = sys.argv[1]
	port = int(sys.argv[2])
	
	for line in iter(sys.stdin.readline,""):
		try:	
			client = Client(host, port, line)
			client.start()
		except:
			pass
