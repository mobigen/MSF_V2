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

class ExceptionHTML(object):
	def __init__(self, raw_dict, cfg, ip_list):
		self.raw_dict = raw_dict
		self.config = cfg
		self.ip_list = ip_list

	def get_exception_html(self):
		status_nok_count = 0
		strNoklist=list()
		mergelist=list()

		__LOG__.Trace("[Noti]Exception HTML Start_________________")
		mergelist.append("<h1 align='center'>Exception</h1>")
		for ip in self.ip_list:
			try:
				hostname = self.raw_dict[ip]['HOSTNAME']['VALUE']
				hostname = ','.join(hostname)
			except:
				__LOG__.Exception()
				hostname = ''
				pass

			try:
				mergelist.append("<center><font size='5'>%s [%s]</font></center><hr>" % (ip, hostname))
				#__LOG__.Trace(self.raw_dict[ip]['PORTS'])
				for ex in self.raw_dict[ip]['EXCEPTION'] :
					mergelist.append(ex.replace('\n', '<br>'))
					status_nok_count += 1
			except:
				__LOG__.Exception()
				pass
		__LOG__.Trace(mergelist)

		for index in range(len(mergelist)):
				if type(mergelist[index]) == unicode:
					mergelist[index] = mergelist[index].encode('cp949')

		for index in range(len(strNoklist)):
				if type(strNoklist[index]) == unicode:
					strNoklist[index] = strNoklist[index].encode('cp949')

		return status_nok_count, strNoklist, mergelist

