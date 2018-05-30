# -*- coding: utf-8 -*-

import socket
import select
import threading
from traceback import *

class ListenServer(threading.Thread) :
	def __init__(self, listen_port, deq) :
		threading.Thread.__init__(self)

		self.listen_port = listen_port
		self.deq		 = deq
		self.sock_list   = []

		self.read_retry  = 10

		self.shutdown	= False

		self.class_name = self.__class__.__name__

	def noti(self) :
		try : return "%16s : connect client count (%d)" % (self.class_name, len(self.sock_list))
		except Exception, err : return "%16s : error cause (%s)" % (self.class_name, str(err))
		
	def init_listen_socket(self) :
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind(("", int(self.listen_port)))
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.listen(10)
		return sock

	def readline(self, sock_fd) :
		retry = 0
		read  = None
		while (not self.shutdown) :
			try :
				read = sock_fd.readline()
				break
			except socket.timeout :
				retry += 1
				if (retry >= self.read_retry) :
					read = None
					break
			except :
				etype, value, tb = sys.exc_info()
				print_exception(etype, value, tb)
				read = None
				break

		return read


	def run(self) :
		listen_sock = self.init_listen_socket()
		self.sock_list.append(listen_sock)

		client_sock_hash = {}   # client socket descriptor

		while (not self.shutdown) :
			try :
				input, output, exception = select.select(self.sock_list, [], [], 1)
			except :
				etype, value, tb = sys.exc_info()
				print_exception(etype, value, tb)	
				break

			if (len(input) == 0) :
				continue

			for sock in input :
				if (sock == listen_sock) :
					client_sock, client_addr = listen_sock.accept()
					client_sock.settimeout(1)
					self.sock_list.append(client_sock)
					client_sock_hash[client_sock] = client_sock.makefile()
				else :
					line = self.readline(client_sock_hash[sock])
					if (line == None or line == "") :
						self.sock_list.remove(sock)
						sock.close()
						del(client_sock_hash[sock])
					else :
						self.deq.appendleft(line.strip())

		for sock in self.sock_list :
			try : sock.close()
			except : pass
