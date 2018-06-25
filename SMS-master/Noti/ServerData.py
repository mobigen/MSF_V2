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

class ServerData(object):
	def __init__(self, raw_dict,cfg,ip_list):
		self.raw_dict = raw_dict
		self.config = cfg
		self.ip_list = ip_list
	
	def get_server_data(self):
		cpu_dict = {}
		mem_dict = {}
		swap_dict = {}
		disk_list = {}
		
		__LOG__.Trace("[Noti]Start SERVER DB___________________")

		for ip in self.ip_list:
			try:
				hostname = self.raw_dict[ip]['HOSTNAME']['VALUE']
				__LOG__.Trace('HOSTNAME %s' % hostname)
				hostname = ','.join(hostname)
			except:
				__LOG__.Exception()
				hostname = ''
				pass
		
			if not disk_list.has_key(ip) :
				disk_list[ip] = []
		
			type_list = [key for key in self.raw_dict[ip]]
			__LOG__.Trace(type_list)
			for types in type_list:
				try:
					#__LOG__.Trace(types)
					if types =='DISK':
						for in_dict in self.raw_dict[ip][types]:
							disk_list[ip].append([ip, hostname] + in_dict['VALUE'])

					elif types == 'LOAD_AVG':
						cpu_dict[ip] = [ip, hostname] + self.raw_dict[ip][types]['VALUE']
					
					elif types == 'MEMORY':
						mem_dict[ip] = [ip, hostname] + self.raw_dict[ip][types]['VALUE']
						
					elif types == 'SWAP':
						swap_dict[ip] = [ip, hostname] + self.raw_dict[ip][types]['VALUE']
				except:
					__LOG__.Exception()
		
		__LOG__.Trace("cpu dict : %s" % cpu_dict)
		__LOG__.Trace("mem dict : %s" % mem_dict)
		__LOG__.Trace("swap dict : %s" % swap_dict)
		__LOG__.Trace("disk dict : %s" % disk_list)
		return cpu_dict, mem_dict, swap_dict, disk_list
