# -*- coding: utf-8 -*-
#!/bin/env python

import re
import signal
import sys
import getopt

import Mobigen.Common.Log as Log

SHUTDOWN = True

def shutdown(sigNum, frame):
	SHUTDOWN = False
	sys.stderr.write("Catch Signal : %s" % sigNum)
	sys.stderr.flush()
	
signal.signal(signal.SIGTERM,shutdown) # sigNum 15 : Terminate
signal.signal(signal.SIGINT, shutdown)  # sigNum  2 : Interrupt
signal.signal(signal.SIGHUP, shutdown)  # sigNum  1 : HangUp
signal.signal(signal.SIGPIPE,shutdown) # sigNum 13 : Broken Pipe


class IrisData(object) :

	def __init__(self, raw_dict,cfg, ip_list):
		self.raw_dict = raw_dict
		self.config = cfg
		self.ip_list = ip_list

	def get_iris_data(self):
		mergelist=list()
		
		for ip in self.ip_list :
			try:
				hostname=''
				__LOG__.Trace(self.raw_dict[ip]['HOSTNAME']['VALUE'])
				hostname = self.raw_dict[ip]['HOSTNAME']['VALUE']
				hostname = ','.join(hostname)
			except:
				__LOG__.Exception()

			type_list = [key for key in self.raw_dict[ip].keys()]
			for types in type_list:
				if not types=='IRIS':
					continue
				try:
					mergelist.append([ip, hostname] + self.raw_dict[ip][types]['VALUE'])
				except:
					pass
		return mergelist
