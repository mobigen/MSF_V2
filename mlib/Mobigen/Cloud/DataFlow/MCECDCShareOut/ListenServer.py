# -*- coding: utf-8 -*-

import mce
import sys
import socket
import select
import threading
from traceback import *

class ListenServer(threading.Thread) :
	def __init__(self, listen_port, dc_reader, is_local) :
		threading.Thread.__init__(self)
		self.listen_port = listen_port
		self.reader      = dc_reader
		self.shutdown    = False
		self.read_retry  = 10
		self.send_count  = 0
		self.sock_list   = []
		self.is_local    = is_local
		self.class_name  = self.__class__.__name__

	def __del__(self) :
		self.close()

	def init_listen_socket(self) :
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind(("", int(self.listen_port)))
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.listen(10)
		return sock

	def noti(self) :
		try : return "%16s : client connect count(%d) send count(%d)" % (self.class_name, len(self.sock_list), self.send_count)
		except Exception, err : return "%16s : error cause(%s)" % (self.class_name, str(err))

	def readline(self, sockfd) :
		retry = 0
		read  = None
		while (not self.shutdown) :
			try :
				read = sockfd.readline()
				break
			except socket.timeout :
				retry += 1
				if (retry >= self.read_retry) :
					read = None
					break
			except Exception, err :
				etype, value, tb = sys.exc_info()
				print_exception(etype, value, tb)
				read = None
				break
				
		return read

	def action(self, sock, sockfd) :
		line = self.readline(sockfd)
		if (line == None or line == "") : return False

		#cmd_parse = line.strip().split(",")
		#cmd = cmd_parse[2]

		cmd = line.strip()
		mce.info_msg("recv (%s)" % cmd)

		if (cmd == "quit") :
			return False

		if (cmd == "req") :
			ftime, mtime, opt, index, data = self.reader.next()
			send_msg = "OK,%s" % data
		else :
			send_msg = "NOK,invalid command"

		try :
			sock.sendall(send_msg + "\r\n")
			self.send_count += 1
			mce.info_msg("send (%s)" % send_msg)
		except :
			etype, value, tb = sys.exc_info()
			print_exception(etype, value, tb)

		return True

	def run(self) :
		listen_sock = self.init_listen_socket()

		self.sock_list.append(listen_sock)

		client_sockfd_hash = {}

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
					client_sockfd_hash[client_sock] = client_sock.makefile()
				else :
					ret = self.action(sock, client_sockfd_hash[sock])
					if (ret == False) :
						self.sock_list.remove(sock)
						sock.close()
						del(client_sockfd_hash[sock])
		self.close()


	def close(self) :
		for sock in self.sock_list :
			try : sock.close()
			except : pass
		self.sock_list = []

		try : self.reader.close()
		except : pass


if __name__ == "__main__" :
	from mdfs import MDFSClient
	from mdfs_protocol_pb2 import Response
	mdfs_client = MDFSClient("localhost", 8000)
	mdfs_client.login("mdfs", "mdfs")

	import DCReader
	r = DCReader.DCReader(mdfs_client, "/RAW_DATA/CollectDir", "/Index/Share.idx", "1")

	l = ListenServer("50001", r)
	l.daemon = True
	l.start()

	import time
	time.sleep(0.1)

	test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	test_sock.connect(("localhost", 50001))
	test_sock_fd = test_sock.makefile()

	test_sock.sendall(",,req\r\n")
	print test_sock_fd.readline()

	#test_sock.sendall(",,quit\r\n")
	#time.sleep(1)

	l.shutdown = True

	l.join()
