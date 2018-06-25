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

class ServerHTML(object):
	def __init__(self, raw_dict,cfg, ip_list):
		self.raw_dict = raw_dict
		self.config = cfg
		self.ip_list = ip_list
	
	def get_threshold_config(self, section):
		try:
			conf_dict=dict()
			conf_list=['LOAD_AVG','MEMORY','DISK','SWAP']
			
			for types in conf_list:
				try:
					conf_dict[types]=self.config.get(section,types)
				except:
					conf_dict[types]=''

			return conf_dict
		except:
			__LOG__.Exception()
	
	def get_server_html(self):
		mergelist=list()
		thresholdlist=list()
		strNoklist=list()
		status_nok_count = 0

		__LOG__.Trace("[Noti]SERVER HTML Start___________________")

		server_flag = True
		for ip in self.ip_list:
			if server_flag :
				server_flag = False
				conf_dict = self.get_threshold_config('RESOURCES')
				thresholdlist.append("<center><font size='5'>Threshold(임계치)</font></center><table align='center' width='95%' cellpadding='5' cellspacing='0' border='1'><tr bgcolor='FFFF00'><td></td><td>SWAP(Use%)</td><td>DISK(Use%)</td><td>LOAD_AVERAGE</td><td>MEMORY(Use%)</td></tr>")
				thresholdlist.append("<tr><td>Default Threshold</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" %(conf_dict['SWAP'],conf_dict['DISK'], conf_dict['LOAD_AVG'],conf_dict['MEMORY']))
				mergelist.append("<h1 align='center'>ServerResource</h1>")

			try:
				hostname = self.raw_dict[ip]['HOSTNAME']['VALUE']
				hostname = ','.join(hostname)
			except:
				__LOG__.Exception()
				hostname = ''
				pass
		
			try:
				conf_dict = self.get_threshold_config(ip)
				__LOG__.Trace("Threshold conf DISK: %s, SWAP: %s, LOAD_AVG: %s, MEMORY: %s" % (conf_dict['DISK'], conf_dict['SWAP'], conf_dict['LOAD_AVG'],conf_dict['MEMORY']))
				if conf_dict['DISK']=='' and conf_dict['SWAP']=='' and conf_dict['LOAD_AVG']=='' and conf_dict['MEMORY'] == '':
					pass
				else:
					thresholdlist.append("<tr><td>%s</td>"%ip)
					for types in conf_dict.keys():
						if conf_dict[types]=='':
							thresholdlist.append("<td></td>")
						else:
							thresholdlist.append("<td>%s</td>" %conf_dict[types])
					thresholdlist.append("</tr>")
			except:
				__LOG__.Exception()
			
			mergelist.append("<center><font size='5'>%s [%s]</font></center><hr>" % (ip, hostname))

			type_list = [key for key in self.raw_dict[ip]]
			for types in type_list:
				try:
					#__LOG__.Trace(types)
					if types =='DISK':
						mergelist.append("<font size='4'>DISK</font><font size='3'>(단위MB)</font>")
						mergelist.append("<table align='center' width='95%' cellpadding='5' cellspacing='0' border='1'>")
						mergelist.append("<tr bgcolor='#FFFF00'><td>Mount On(마운트정보)</td><td>1M-blocks(전체디스크용량)</td><td>Used(사용량)</td><td>Available(사용가능용량)</td><td>Use(사용률%)</td></tr>")
						for in_dict in self.raw_dict[ip][types]:
							__LOG__.Trace(in_dict)
							mergelist.append("<tr>")
							if in_dict['STATUS']=='NOK':
								status_nok_count +=1
								strNoklist.append("[ServerResource] %s[%s] : [%s]%s, %s%%<br>" % (ip,hostname,types,in_dict['VALUE'][0],in_dict['VALUE'][4]))
								for elem in in_dict['VALUE']:
									elem = self.commasplit(elem)
									mergelist.append("<td><b><font color='red'>%s</font></b></td>" % elem)
							else:
								for elem in in_dict['VALUE']:
									elem = self.commasplit(elem)
									mergelist.append("<td>%s</td>" % elem)
							mergelist.append("</tr>")
						mergelist.append("</table><br>")

					elif types == 'LOAD_AVG':
						mergelist.append("<font size='4'>CPU_LOAD_AVERAGE</font>")
						mergelist.append("<table align='center' width='95%' cellpadding='5' cellspacing='0' border='1'>")
						mergelist.append("<tr bgcolor='#FFFF00'><td>1 minutes</td><td>5 minutes</td><td>15 minutes</td>")
						mergelist.append("<tr>")

						if self.raw_dict[ip][types]['STATUS'] == 'NOK':
							status_nok_count +=1
							strNoklist.append("%s[%s] : [%s]%s%%<br>" % (ip,hostname,types,self.raw_dict[ip][types]['VALUE']))
							for elem in self.raw_dict[ip][types]['VALUE']:
								elem = self.commasplit(elem)
								mergelist.append("<td><b><font color='red'>%s</font></b></td>" % elem)
						else:
							for elem in self.raw_dict[ip][types]['VALUE']:
								elem = self.commasplit(elem)
								mergelist.append("<td>%s</td>" % elem)
						mergelist.append("</tr></table><br><br><br>")
					
					elif types == 'SWAP' or types == 'MEMORY':
						mergelist.append("<font size='4'>%s</font><font size='3'>(단위 MB)</font>" % types)
						mergelist.append("<table align='center' width='95%' cellpadding='5' cellspacing='0' border='1'>")
						mergelist.append("<tr bgcolor='#FFFF00'><td>Total</td><td>Used(사용량)</td><td>Available(사용가능용량)</td><td>Use(사용률%)</td></tr>")
						mergelist.append("<tr>")
						try:
							if self.raw_dict[ip][types]['STATUS'] =='NOK':
								status_nok_count +=1
								strNoklist.append("%s[%s] : [%s]%s%%<br>" % (ip,hostname,types,self.raw_dict[ip][types]['VALUE'][3]))
								for elem in self.raw_dict[ip][types]['VALUE']:
									elem = self.commasplit(elem)
									mergelist.append("<td><b><font color='red'>%s</font></b></td>" % elem)
							else:
								for elem in self.raw_dict[ip][types]['VALUE']:
									elem = self.commasplit(elem)
									mergelist.append("<td>%s</td>" % elem)
							mergelist.append("</tr></table><br>")
						except:
							pass
				except:
					__LOG__.Exception()
	
		thresholdlist.append("</table><br>")
		for idx in range(len(strNoklist)) :
			if type(strNoklist[idx]) == unicode :
				strNoklist[idx] = strNoklist[idx].encode('cp949')

		for idx in range(len(thresholdlist)) :
			if type(thresholdlist[idx]) == unicode :
				thresholdlist[idx] = thresholdlist[idx].encode('cp949')
		
		strThr=''.join(thresholdlist)
		for index in range(len(mergelist)) : 
			if type(mergelist[index]) == unicode : 
				mergelist[index] = mergelist[index].encode('cp949')

			if type(strThr) == unicode :
				strThr = strThr.encode('cp949')
		
		mergelist.insert(1,strThr)
		__LOG__.Trace("[Noti]SERVER HTML End___________________")
		return status_nok_count, strNoklist, mergelist
		
	def commasplit(self, number):
		try:
			if not re.match('\d[^\.\%]',number):
				return number
			tmp = number.split('.')
			num = tmp[0]
			decimal = '.' + tmp[1]
		except:
			decimal = ''
		head_num = len(num) % 3
		result = ''
		for pos in range(len(num)):
			if pos == head_num and head_num:
				result = result + ','
			elif (pos - head_num) % 3 == 0 and pos:
				result = result + ','
			result = result + num[pos]
		return result+decimal
