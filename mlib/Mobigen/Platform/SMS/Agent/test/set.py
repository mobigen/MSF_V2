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

C_PORT = 10005
R_PORT = 10004

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
			c_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			r_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			c_s.connect((IP, C_PORT))
			r_s.connect((IP, R_PORT))

			self.sock = r_s

			fd = c_s.makefile()
			r_fd = r_s.makefile()

			print fd.readline()
			print r_fd.readline()

			print "USER"
			c_s.send("USER admin\n");
			print fd.readline()

			r_s.send("USER admin\n");
			print r_fd.readline()

			print "PASS"
			c_s.send("PASS admin.\n");
			print fd.readline()
			r_s.send("PASS admin.\n");
			print r_fd.readline()


			isWrite = False;
			F = None	

			#c_s.send("ADDCOND:CODE=OraHitRatio,element=0,INST=ALL,COND=>=60,level=MAJOR;\r\n");
			#c_s.send( "ADDCOND:CODE=OraHitRatio,element=1,INST=ALL,COND=>=60,level=MAJOR;\r\n");
			#c_s.send("ADDCOND:CODE=OraHitRatio,element=2,INST=ALL,COND=>=60,level=MAJOR;\r\n");
			#c_s.send("ADDCOND:CODE=OraTableSpace,element=4,INST=ALL,COND=>=80,level=MAJOR;\r\n");

			#c_s.send("ADDCOND:CODE=OraTableSpace,element=4,INST=ALL,COND=>=80,level=MAJOR;\r\n");
			#c_s.send("ADDCOND:CODE=ProcessPerf,element=2,INST=ALL,COND=>=6,level=MAJOR;\r\n");
			c_s.send("SETCOND:CODE=ProcessPerf,CONDID=2,element=2,INST=ALL,COND=>=1,level=MAJOR;\r\n");
			#c_s.send("GETCOND:CODE=CPUPerf;\r\n");

			while True:
				#data =  self.readline();
				data = r_fd.readline()
				if not data:
					break
				data = data.replace("\0", "");
				print data.strip()

				if data.find("COMPLETED") == 0:
					break;

			c_s.send("exit;");
			r_s.send("exit;");


			fd.close()
			r_fd.close()

			c_s.close()
			r_s.close()
	#}
#}


if __name__ == "__main__":

	client = ClientSample()
	client.start()
	client.join()


