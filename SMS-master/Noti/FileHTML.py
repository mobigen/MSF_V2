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

"""File에 대한 Dict 형식예시 :
{'ans01':			
	{'STATUS': 'OK',		
	'HOSTNAME': {'VALUE': ['ans01']}, 		
	FILE': {		
		'/home/junga/user/ja(types)': {	
			'S': {'STATUS': 'OK', 'VALUE': ['2015-05-19 15:42:03', '+0900']}, 
			'TITLE': {'VALUE': 'NSN'}
		}, 	
		'/home/junga/user/ja/SMS': {	
			'TITLE': {'VALUE': 'NSN'}, 
			'N': {'STATUS': 'OK', 'VALUE': ['2015-05-15 10:18:26', '+0900']}
			}
		}	
	}		
}
"""

class FileHTML(object):
	def __init__(self, raw_dict,cfg, ip_list):
		self.raw_dict = raw_dict
		self.config = cfg
		self.ip_list = ip_list

	def get_file_html(self):
		"""html string을 만듬."""
		__LOG__.Trace("[Noti]FileHTML Start________________________________")
		strNoklist = list()
		mergelist = list()
		thresholdlist = list()
		status_nok_count = 0

		file_flag = True
		for ip in self.ip_list :
			
			#임계치 표를 한번만 나타내기 위해서 file_flag사용	
			if file_flag :
				file_flag=False
				mergelist.append("<h1 align='center'>FILE_MONITOR</h1>")
				thresholdlist.append("<center><font size='5' align='left'>Threshold(임계치)</font></center>")
				thresholdlist.append("<table align='center' width='95%' cellpadding='5' cellspacing='0' border='1'>")
				thresholdlist.append("<tr bgcolor='#E0FFFF'><td></td><td>FILE_SECOND</td></tr>")
				
				try: thresholdlist.append("<tr><td>default Threshold</td><td>%s</td></tr>" % self.config.get('RESOURCES','FILE_SECOND'))
				except: __LOG__.Exception()
			
			if self.config.has_option(ip,'FILE_SECOND'):
				thresholdlist.append("<tr><td>%s</td><td>%s</td></tr>" % (ip,self.config.get(ip,'FILE_SECOND')))

			try:
				#IP 및 hostname 등록
				hostname=''
				hostname = self.raw_dict[ip]['HOSTNAME']['VALUE']
				hostname = ','.join(hostname)
				__LOG__.Trace("%s[%s]" % (ip,hostname))
				
				mergelist.append("<center><font size='5'>%s[%s]</font></center><hr>" % (ip, hostname))
			except:
				__LOG__.Exception()
			
			try:
				#file type list를 불러와서 sort	
				type_list = self.raw_dict[ip]['FILE'].keys()
				type_list.sort(key=natural_keys)	
				#__LOG__.Trace("TYPE_LIST %s" % type_list)
			except:
				type_list = list()
				sorted_type_list=list()
				__LOG__.Exception()
		
			before_title=''
			title =''
			next_title = ''
			for types in type_list :
				#types에 해당하는 TITLE이 같다면 하나의 표로 묶어준다.
				__LOG__.Trace("File Types : %s " % types)
				try:
					index = type_list.index(types)
				#	__LOG__.Trace(" START : before title :%s, title : %s, next title : %s" %(before_title, title, next_title))
					if index !=0: 
						before_title = self.raw_dict[ip]['FILE'][type_list[index-1]]['TITLE']['VALUE']
					title = self.raw_dict[ip]['FILE'][types]['TITLE']['VALUE']
				
				except : before_title = ''
					
				try : next_title = self.raw_dict[ip]['FILE'][type_list[index+1]]['TITLE']['VALUE']
				except : next_title = '' #마지막index에서는 IndexError가 날 것임.
					
				try :	
					if title != before_title:
						 mergelist.append("<font size='4'>%s</font>"%title)
						 mergelist.append("<table align='center' width='95%' cellpadding='5' cellspacing='0' border='1'>")
						 mergelist.append("<tr bgcolor='#E0FFFF'><td>FileName</td><td>FindString</td><td>수집시간</td><td>description</td></tr>")

				#	__LOG__.Trace(" END : before title :%s, title : %s, next title : %s" %(before_title, title, next_title))
				except: 
					__LOG__.Exception()

				#FindString 및 value값 처리하기 (FindString : 파일내 특정 문자를 찾는 string이 포함되어 있을 경우)
				try:
					for groups in sorted(self.raw_dict[ip]['FILE'][types].keys(), key=natural_keys):
						if groups == 'TITLE':
							continue
						
						mergelist.append("<tr>")
						if self.raw_dict[ip]['FILE'][types][groups]['STATUS'] == 'NOK':
							status_nok_count +=1
							
							strNoklist.append("[FileMonitor] %s[%s - %s] : %s <br>" % (ip,types,groups,'  '.join(self.raw_dict[ip]['FILE'][types][groups]['VALUE'])))
							mergelist.append("<td><font color='red'><b>%s</b></font></td>" % types)
							mergelist.append("<td><font color='red'><b>%s</b></font></td>" % groups)
							
							for elem in self.raw_dict[ip]['FILE'][types][groups]['VALUE']:
								mergelist.append("<td><font color='red'><b>%s</b></font></td>" % elem)
						else:
							mergelist.append("<td>%s</td>" % types)
							mergelist.append("<td>%s</td>" % groups)
							
							for elem in self.raw_dict[ip]['FILE'][types][groups]['VALUE']:
								mergelist.append("<td>%s</td>" % elem)
						mergelist.append("</tr>")
				except:
					pass
				
				if title!=next_title :
						mergelist.append("</table><br><br>")
		
		
		for index in range(len(mergelist)) : 
			if type(mergelist[index]) == unicode : 
				mergelist[index] = mergelist[index].encode('cp949')

		for index in range(len(strNoklist)) :
			if type(strNoklist[index]) == unicode :
				strNoklist[index] = strNoklist[index].encode('cp949')
	
		thresholdlist.append("</table><br>")
		strThreshold = ''.join(thresholdlist)
		mergelist.insert(1,strThreshold)

		return status_nok_count, strNoklist, mergelist 

def atoi(text):
	return int(text) if text.isdigit() else text

#int를 string 기준으로 sorting함
def natural_keys(text):
	key= [atoi(c) for c in re.split('(\d+)', text)]
	return key
if __name__=='__main__':
	lm = LogMoniterHTML()
	lm.run()
