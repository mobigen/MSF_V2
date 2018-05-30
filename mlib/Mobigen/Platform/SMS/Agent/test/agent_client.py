#!/bin/env python
# coding: iso-8859-1

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

			cmd = []

			#cmd.append("COL:CODE=CPUPerf;\r\n");
			#c_s.send("COL:CODE=PatchConf;\n");
			#c_s.send("COL:CODE=SWConf;\r\n");
			#c_s.send("COL:CODE=CPUConf;\r\n");


			#cmd.append( "COL:CODE=MemoryConf;\r\n");

			#cmd.append("COL:CODE=HostConf;\r\n");

			#cmd.append("COL:CODE=InterfaceConf;\r\n");

			#c_s.send("COL:CODE=CPULoad;\r\n");
		#	c_s.send("COL:CODE=MemoryPerf;\r\n");
			#c_s.send("COL:CODE=DiskPerf;\r\n");
			#cmd.append("COL:CODE=DiskIOPerf;\r\n");

			#cmd.append("COL:CODE=NetworkPerf;\r\n");

			#c_s.send("COL:CODE=ProcessPerf;\r\n");
			#cmd.append("COL:CODE=TopMemProcess,INST=memory|10;\r\n");
			#cmd.append("COL:CODE=TopCPUProcess,INST=cpu|10;\r\n");

			#c_s.send("COL:CODE=LogCheck;\r\n");

			#c_s.send("COL:CODE=ShellCommand,INST=dir c:;\r\n");
			#c_s.send("COL:CODE=ShellCommand,INST=ipconfig;\r\n");
			#c_s.send("COL:CODE=ShellCommand,INST=ipconfig;\r\n");

			#c_s.send("COL:CODE=SessionPerf;\r\n");
			#cmd.append("COL:CODE=OraSessionCount;\r\n");
			cmd.append("COL:CODE=OraTopSql;\r\n");
			cmd.append("COL:CODE=OraHitRatio;\r\n");
			cmd.append("COL:CODE=OraDBLink;\r\n");
			cmd.append("COL:CODE=OraTableSpace;\r\n");
			cmd.append("COL:CODE=OraRollback;\r\n");
			#cmd.append("COL:CODE=ProcessPerf,INST=apache;\r\n");
			#cmd.append("COL:CODE=ProcessPerf,INST=scagent.exe;\r\n");

			#cmd.append("GETCOND:CODE=CPUPerf;\r\n");
			#cmd.append("GETCOND:CODE=MemoryPerf;\r\n");
			#cmd.append("GETCOND:CODE=DiskPerf;\r\n");
			#cmd.append("GETCOND:CODE=ProcessPerf;\r\n");
			#cmd.append("GETCOND:CODE=OraTableSpace;\r\n");
			#cmd.append("GETCOND:CODE=OraHitRatio;\r\n");
			#cmd.append("GETCOND:CODE=ProcessHealth;\r\n");


			c_s.send( cmd.pop())
			while True:
				#data =  self.readline();
				data = r_fd.readline()
				if not data:
					break
				data = data.replace("\0", "");
				print data.strip()

				if data.find("COMPLETED") == 0:
					if len(cmd) <= 0:
						break
					c_s.send( cmd.pop())
				#	break;

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


