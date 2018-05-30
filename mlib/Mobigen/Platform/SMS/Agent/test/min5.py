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

C_PORT = 10005
R_PORT = 10002

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

		global C_PORT, R_PORT

		if True:
		#try:
			r_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			r_s.connect(("127.0.0.1", R_PORT))

			self.sock = r_s

			print "USER"
			r_s.send("USER admin\r\n");
			print "PASS"
			r_s.send("PASS admin.\r\n");


			isWrite = False;
			F = None	

			#c_s.send("COL:CODE=NetworkPerf;\r\n");
			#c_s.send("COL:CODE=InterfaceConf;\r\n");
			#c_s.send("COL:CODE=ProcessPerf;\r\n");
			#c_s.send("COL:CODE=TopMemProcess;\r\n");
			#c_s.send("COL:CODE=SessionPerf;\r\n");
			#c_s.send("COL:CODE=PatchConf;\r\n");
			#c_s.send("COL:CODE=SWConf;\r\n");

			while True:
				data =  self.readline();
				if not data:
					break
				data = data.replace("\0", "");
				print data.strip()

				if data.find("COMPLETED") == 0:
					continue;

			r_s.send("exit");

			r_s.close()
	#}
#}


if __name__ == "__main__":

	client = ClientSample()
	client.start()
	client.join()


