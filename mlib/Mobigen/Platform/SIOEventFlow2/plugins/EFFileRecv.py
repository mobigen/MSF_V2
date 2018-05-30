#!/bin/env python
#coding: utf-8

import os
import sys
import getopt
import socket
import threading
import SocketServer

BUF_SIZE = 1024

class RequestHandler(SocketServer.BaseRequestHandler):

	def handle(self):
	
		try:
			sock_file = self.request.makefile()
			line = sock_file.readline()

			protocol, from_path = line.strip().split("://")
			if protocol != "file":
				return
		
			from_dir, basename = os.path.split(from_path)
			to_dir = (self.server.to_dir if self.server.to_dir else from_dir)
			to_path = os.path.join(to_dir, basename)

			out_file = open(to_path, "w")
				
			buf = sock_file.read(BUF_SIZE)	
			while buf:
				out_file.write(buf)
				buf = sock_file.read(BUF_SIZE)
			
			sys.stdout.write("file://%s\n" % to_path)
			sock_file.write("FIN")
			sock_file.flush()
		except:
			pass
		
		finally:
			
			try: sock_file.close()
			except: pass

			try: out_file.close()
			except: pass



class Server(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	pass

if __name__ == "__main__" :

	opts, args = getopt.getopt(sys.argv[1:], 't:')
	to_dir = None
	for o, a in opts:
		if o == "-t":
			to_dir = a
		else:
			assert False, "unhandled option"

	if len(args) != 2 :
		print "usage : %s ip port" % (sys.argv[0])
		sys.exit()

	ip = args[0]
	port = int(args[1])

	server = Server((ip, port), RequestHandler)
	server.to_dir = to_dir 
	try:
		server.serve_forever()
	except KeyboardInterrupt :
		server.shutdown()	
