# -*- coding: utf-8 -*-
#!/bin/env python

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

class IrisHTML(object):
	def __init__(self, raw_dict, ip_list):
		self.raw_dict = raw_dict
		self.ip_list = ip_list

	def get_iris_html(self):
		status_nok_count = 0
		strNoklist=list()
		mergelist=list()
		
		iris_flag = True
		for ip in self.ip_list:
			#__LOG__.Trace("%s %s "% (ip, self.raw_dict[ip].keys()))

			#처음 table label을 한번만 출력하기 위해 iris_flag 사용
		
			irisStatus = self.raw_dict[ip]['IRIS_LISTENER']

			if iris_flag:
				iris_flag=False
				mergelist.append("<h1 align='center'>IRIS</h1>")
				mergelist.append("<h2 align='center'>IRIS LISTENER STATUS : " + irisStatus + "</h2>")
				mergelist.append("<table align='center' width='95%' cellpadding='5' cellspacing='0' border='1'>")
				mergelist.append("<tr bgcolor='#66FF00'><td>IP</td><td>HOSTNAME</td><td>NODE_ID</td><td>SYS_STATUS(VALID, BUSY, WARN)</td><td>ADM_STATUS</td><td>UPDATE_TIME</td><td>CPU(%)</td><td>LOADAVG</td><td>MEM:P(%)</td><td    >MEM:F(%)</td><td>DISK(%)</td></tr>")
				if irisStatus == 'NOK' :
					status_nok_count+=1
					strNoklist.append("Iris Connect Listener Error <br>")
			
			try:
				hostname=''
				#__LOG__.Trace(self.raw_dict[ip]['HOSTNAME']['VALUE'])
				hostname = self.raw_dict[ip]['HOSTNAME']['VALUE']
				hostname = ','.join(hostname)
			except:
				__LOG__.Exception()
			
			type_list = [key for key in self.raw_dict[ip].keys()]

			for types in type_list:
				if not types=='IRIS':
					continue
				try:
					#type이 IRIS인 것만 받아서 table을 만든다.
					mergelist.append("<tr>")
					if self.raw_dict[ip][types]['STATUS'] =='NOK':
						status_nok_count+=1
						strNoklist.append("[IrisStatus] %s[%s] <br>" % (str(ip),self.raw_dict[ip][types]['VALUE']))
						mergelist.append("<td><font color = 'red'>%s</font></td>" % ip)
						mergelist.append("<td><font color = 'red'>%s</font></td>" % hostname)				
						
						for elem in self.raw_dict[ip][types]['VALUE']:
							mergelist.append("<td><font color='red'>%s</font></td>" % elem)
						
						__LOG__.Trace(self.raw_dict[ip][types]['VALUE'])
					else:
						mergelist.append("<td>%s</td>" % ip)
						mergelist.append("<td>%s</td>" % hostname)		
						for elem in self.raw_dict[ip][types]['VALUE']:
							mergelist.append("<td>%s</td>"%elem)
				except:
					pass
			mergelist.append("</tr>")
		mergelist.append("</table><br><br>")

		for index in range(len(mergelist)): 
			if type(mergelist[index]) == unicode : 
				mergelist[index] = mergelist[index].encode('cp949')
		
		for index in range(len(strNoklist)) : 
			if type(strNoklist[index]) == unicode : 
				strNoklist[index] = strNoklist[index].encode('cp949')
		
		return status_nok_count, strNoklist, mergelist
