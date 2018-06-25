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

class LogMonitorHTML(object):
	def __init__(self, raw_dict, cfg, ip_list):
		self.raw_dict = raw_dict
		self.config = cfg
		self.ip_list=  ip_list

	def get_log_html(self):
		__LOG__.Trace("[Noti]LogMonitorHTML Start________________________________")
		strNoklist = list()
		mergelist = list()
		thresholdlist = list()	
		status_nok_count = 0
		
		log_flag = True
		for ip in self.ip_list:
			
			if log_flag :
				log_flag = False
				mergelist.append("<h1 align='center'>LOG_MONITOR</h1>")
				thresholdlist.append("<center><font size='5'>Threshold(임계치)</font></center>")
				thresholdlist.append("<table align='center' width='95%' cellpadding='5' cellspacing='0' border='1'>")
				thresholdlist.append("<tr bgcolor='#FFA500'><td></td><td>LOG_SECOND</td></tr>")
				try : thresholdlist.append("<tr><td>default Threshold</td><td>%s</td></tr>" % self.config.get('RESOURCES','LOG_SECOND'))
				except : __LOG__.Exception()
			
			if self.config.has_option(ip,'LOG_SECOND'):
				thresholdlist.append("<tr><td>%s</td><td>%s</td></tr>" % (ip,self.config.get(ip,'LOG_SECOND')))
			
			try:
				hostname=''
				hostname = self.raw_dict[ip]['HOSTNAME']['VALUE']
				hostname = ','.join(hostname)
				mergelist.append("<center><font size='5'>%s[%s]</font></center><hr>" % (ip,hostname))
			except:
				__LOG__.Exception()
			
			try:
				#title을 기준으로 sort한다.
				type_list = self.raw_dict[ip]['LOG'].keys()
				type_list.sort(key=natural_keys)
				#sorted_type_list = list()
				#for types in type_list:
				#	title_type_list = list()
				#	key = self.raw_dict[ip]['LOG'][types]['TITLE']['VALUE']
				#	for in_types in type_list:
				#		if key == self.raw_dict[ip]['LOG'][in_types]['TITLE']['VALUE']:
				#			if not in_types in sorted_type_list:
				#				title_type_list.append(in_types)
				#	#title별 LogName별로 정렬한다.
				#	for stype in sorted(title_type_list, key=natural_keys) :
				#		sorted_type_list.append(stype)
			except:
				type_list = list()
				#sorted_type_list=list()
				__LOG__.Exception()


			before_title=''
			title=''
			next_title=''
			
			#휴리스틱 - path가 같으면 같은 TITLE을 가질 확률이 높다는 가정하에 sort함
			for types in type_list:
				#__LOG__.Trace("Log Types :%s"% types)
				try: 
					index = type_list.index(types)

					if index != 0 :
						before_title = self.raw_dict[ip]['LOG'][type_list[index-1]]['TITLE']['VALUE']
					title = self.raw_dict[ip]['LOG'][types]['TITLE']['VALUE']
				except: before_title = ''
				
				try: next_title = self.raw_dict[ip]['LOG'][type_list[index+1]]['TITLE']['VALUE']
				except: next_title=''
				
				try:
					if title != before_title :
						mergelist.append("<font size='4'>%s</font>"%title)
						mergelist.append("<table align='center' width='95%' cellpadding='5' cellspacing='0' border='1'>")
						mergelist.append("<tr bgcolor='#FFA500'><td>LogName</td><td>FindString</td><td>수집로그시간</td><td>Description</td></tr>")
				except:
					__LOG__.Exception()
				
				#__LOG__.Trace(" END : before title :%s, title : %s, next title : %s" %(before_title, title, next_title))
				try:
					#groups가 1개이상이면 별도의 <table></table>을 만들고, 1개 이하면 하나로 이어붙이기 위함임.
					for groups in sorted(self.raw_dict[ip]['LOG'][types].keys(), key=natural_keys):
						if groups == 'TITLE':
							continue
						#__LOG__.Trace("%s %s"%(groups,self.raw_dict[ip]['LOG'][types][groups]['VALUE']))
						
						mergelist.append("<tr>")
						if self.raw_dict[ip]['LOG'][types][groups]['STATUS'] == 'NOK':
							status_nok_count+=1
							
							
							strNoklist.append("[LogMonitor] %s[%s - %s] : %s <br>" % ( ip, types, groups, ' '.join(self.raw_dict[ip]['LOG'][types][groups]['VALUE'])))
							
							mergelist.append("<td><font color='red'><b>%s</b></font></td>" % types)
							mergelist.append("<td><font color='red'><b>%s</b></font></td>" % groups)
							
							for elem in self.raw_dict[ip]['LOG'][types][groups]['VALUE']:
								mergelist.append("<td><font color='red'><b>%s</b></font></td>" % elem)
						else:
							mergelist.append("<td>%s</td>" % types)
							mergelist.append("<td>%s</td>" % groups)
							
							for elem in self.raw_dict[ip]['LOG'][types][groups]['VALUE']:
								mergelist.append("<td>%s</td>" % elem)
						mergelist.append("</tr>")
				except:
					pass

				if title!=next_title:
					mergelist.append("</table><br>")
		
		for index in range(len(mergelist)) : 
			if type(mergelist[index]) == unicode : 
				mergelist[index] = mergelist[index].encode('cp949')

		for index in range(len(strNoklist)) :
			if type(strNoklist[index]) == unicode :
				strNoklist[index] = strNoklist[index].encode('cp949')

		thresholdlist.append("</table><br>")
		strThreshold = ''.join(thresholdlist)
		mergelist.insert(1,strThreshold)
		__LOG__.Trace("[Noti]LogMonitorHTML End________________________________")
		return status_nok_count, strNoklist, mergelist 

def atoi(text):
	return int(text) if text.isdigit() else text
def natural_keys(text):
	key= [atoi(c) for c in re.split('(\d+)', text)]
	return key
if __name__=='__main__':
	lm = LogMoniterHTML()
	lm.run()
