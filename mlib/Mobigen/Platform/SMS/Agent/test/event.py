#!/usr/bin/python
# coding: euc-kr

import socket
import time
import os
import sys
import string
import re
from threading import Thread
#from socket import *

#IP = "150.23.19.100"
IP = "127.0.0.1"

#C_PORT = 10002
R_PORT = 10001

class ClientSample(Thread):
#{
	def __init__(self):
		Thread.__init__(self)
		self.inbuf = ''

	def readline(self):
		""" readine for socket - buffers data """
		# Much slower than built-in method!
		lf = 0
		while True:
			lf = string.find(self.inbuf, '\n')
			if lf >= 0:
				break
			r = self.sock.recv(4096)
			if not r: 
				# connection broken
				break
			self.inbuf = self.inbuf + r
		lf = lf + 1
		data = self.inbuf[:lf]
		self.inbuf = self.inbuf[lf:]
		return data

	def run(self):
	#{

		global C_PORT, R_PORT, IP

		if True:
		#try:
			r_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			r_s.connect((IP, R_PORT))

			self.sock = r_s

			r_fd = r_s.makefile()

			print r_fd.readline()

			r_s.send("USER admin\n");
			print r_fd.readline()

			r_s.send("PASS admin.\n");
			print r_fd.readline()


			isWrite = False;
			F = None	


			while True:
				#data =  self.readline();
				data = r_fd.readline()
				if not data:
					break
				data = data.replace("\0", "");
				print data.strip()

				#if data.find("COMPLETED") == 0:
				#	break;

			r_s.send("exit;");


			r_fd.close()

			r_s.close()
	#}
#}


if __name__ == "__main__":

	client = ClientSample()
	client.start()
	client.join()


