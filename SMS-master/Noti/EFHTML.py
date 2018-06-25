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

class EFHTML(object):
	def __init__(self, raw_dict, cfg, ip_list):
		self.raw_dict = raw_dict
		self.config = cfg
		self.ip_list = ip_list

	def get_EF_html(self):
		status_nok_count = 0
		strNoklist=list()
		mergelist=list()
		
		EF_flag = True
		__LOG__.Trace("[Noti]EventFlow HTML Start_________________")
		mergelist.append("<h1 align='center'>EventFlow</h1>")
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
				__LOG__.Trace(self.raw_dict[ip]['PORTS'])
				for port in self.raw_dict[ip]['PORTS']:
					mergelist.append("<font size='4'>Port : %s</font>" % port)
					mergelist.append("<table align='center' width='95%' cellpadding='5' cellspacing='0' border='1'>")
					mergelist.append("<tr bgcolor='#99ccff'><td>ABN</td><td>Node Name</td><td>Status</td><td>Queue Count</td></tr>")
					for ps in self.raw_dict[ip][port]:
						abn = ps['ABN']
						status = ps["STATUS"]
						ps_name = ps["NODE"]
						queue_count = ps['QUEUE_COUNT']
						
						if abn == 'OK':
							mergelist.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (abn, ps_name, status, queue_count))
						else:
							status_nok_count += 1
							strNoklist.append("[EventFlow Status] %s[%s] <br>" % (p, status))
							mergelist.append("<tr><td><font color = 'red'>%s</font></td><td><font color = 'red'>%s</font></td><td><font color = 'red'>%s</font></td><td><font color = 'red'>%s</font></td></tr>" % (abn, ps_name, status, queue_count))
					mergelist.append("</table><br><br>")

			except:
				pass
		__LOG__.Trace(mergelist)
		for index in range(len(mergelist)):
				if type(mergelist[index]) == unicode:
					mergelist[index] = mergelist[index].encode('cp949')

		for index in range(len(strNoklist)):
				if type(strNoklist[index]) == unicode:
					strNoklist[index] = strNoklist[index].encode('cp949')

		return status_nok_count, strNoklist, mergelist

