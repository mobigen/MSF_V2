#!/usr/bin/env python

import sys
import select
import socket
import __main__

class SelectCore :
	
	def __init__(self, host, port, conf) :
		self.some_core = __main__.SomeCore(conf)

		self.host = host
		self.port = int(port)

		self.sock_list = []
		self.client_hash = {}

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


	def loop(self) :
		listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		listen_sock.bind((self.host, self.port))
		listen_sock.listen(100)

		self.sock_list.append(listen_sock)

		while (True) :
	#	{
			try : input, output, exception = select.select(self.sock_list, [], [], 1)
			except : break

			if (len(input) == 0) : continue

			for sock in input :
				if (sock == listen_sock) :
					client, addr = listen_sock.accept()
					self.sock_list.append(client)
					self.client_hash[client] = client.makefile()
				else :
					try :
						line = self.client_hash[sock].readline()
						if (line.strip() == "") : raise Exception
					except :
						self.close(sock)
						continue

					try :
						if (line[:3].upper() == "BYE") :
							self.close(sock)
							continue
					
						answer = self.some_core.sfio(line)

						if (line[:3].upper() == "KIL") :
							for sock in self.sock_list :
								self.close(sock)
							sys.exit()

						if (answer) :
							sock.sendall(answer)
					except :
						continue
	#	}

if __name__ == "__main__" :
	import threading
	import ConfigParser
	class SomeCore(threading.Thread) :
		def __init__(self, conf) :
			threading.Thread.__init__(self)
			
			cfg = ConfigParser.ConfigParser()
			cfg.read(conf)

			self.cmd = {}
			for cmd_name, cmd_class in cfg.items("AsynCore Command") :
				self.cmd[cmd_name.upper()] = cmd_class

		def sfio(self, sfin) :
			try : line = sfin[:3].upper()
			except : return None

			if (self.cmd[line] == "0") :
				sys.stdout.write(sfin)
				sys.stdout.flush()
				return None
			elif (self.cmd[line] == "1") :
				sys.stdout.write(sfin)
				sys.stdout.flush()
				return sys.stdin.readline()
			elif (self.cmd[line] == "2") :
				sys.stdout.write(sfin)
				sys.stdout.flush()
			
				ret_list = []
				while (True) :
					read = sys.stdin.readline()
					if (read == "\n") : break
					ret_list.append(read)
				return "".join(ret_list)
			else :
				return None

	if (len(sys.argv) != 4) :
		print "usage : %s ip port conf" % sys.argv[0]
		sys.exit(0)

	ip, port, conf = sys.argv[1:]

	server = SelectCore(ip, port, conf)
	server.loop()
