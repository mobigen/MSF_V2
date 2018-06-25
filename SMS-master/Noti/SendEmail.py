# -*- coding: utf-8 -*-
#!/bin/env python

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.header import Header
from email import Encoders

import smtplib
import datetime
import re
import signal
import sys
import getopt

import Mobigen.Common.Log as Log
from Noti.ServerHTML import *
from Noti.IrisHTML import *
from Noti.LogMonitorHTML import *
from Noti.FileHTML import *
from Noti.EFHTML import *

SHUTDOWN = True

def shutdown(sigNum, frame):
	SHUTDOWN = False
	sys.stderr.write("Catch Signal : %s" % sigNum)
	sys.stderr.flush()
signal.signal(signal.SIGTERM,shutdown) # sigNum 15 : Terminate
signal.signal(signal.SIGINT, shutdown)  # sigNum  2 : Interrupt
signal.signal(signal.SIGHUP, shutdown)  # sigNum  1 : HangUp
signal.signal(signal.SIGPIPE,shutdown) # sigNum 13 : Broken Pipe

class SendEmail(object):
	def __init__(self, conf_parser, dict_obj, collect_name):
		self.config = conf_parser
		self.raw_dict = dict_obj
		self.collect_name = collect_name
		self.connect_nok_count =0
		self.status_nok_count =0
		self.nok_list = list()
		self.merge_list = list()
	
	def get_emails_config(self):
		try :
			config_emaillist = self.config.get('EMAIL','EMAILLIST').split(',')
			config_title = self.config.get('EMAIL','TITLE')
			config_user = self.config.get('EMAIL','SEND_USER')
			config_passwd = self.config.get('EMAIL','SEND_PASSWD')
			config_smtpip = self.config.get('EMAIL','SMTP_IP')
			config_smtpport = self.config.get('EMAIL','SMTP_PORT')
			return (config_emaillist, config_title, config_user, config_passwd, config_smtpip, config_smtpport)
		except :
			__LOG__.Exception()

	def send_gmail(self, to, title, html, user, passwd, smtp_ip, smtp_port, attach=None):
		try:
			__LOG__.Trace(to, title)
			msg = MIMEMultipart('alternative')
			msg['From']=user
			msg['To']=to
			msg['Subject']=Header(title,'utf-8')
			msg.attach(MIMEText(html, 'html', 'utf-8'))

			mailServer = smtplib.SMTP(smtp_ip,smtp_port)
			mailServer.ehlo()
			mailServer.starttls()
			mailServer.ehlo()
			mailServer.login(user,passwd)
			mailServer.sendmail(user, to, msg.as_string())
			mailServer.close()
		except:
			__LOG__.Exception()

	def PreHTML(self):
		html_list=list()
		html_list.append("<html><head><meta charset='utf-8'>")
		html_list.append("<style type='text/css'>TR{height:20pt; font-family:Arial; font-size: 10pt; text-align:center;} TD{height:20pt; font-family:Arial; font-size:10pt; text-align:center;}</style></head><body>")
		html_list.append("<h3 align='left'>Problem Summary</h3>")
		return html_list

	def connect_nok_HTML(self, ip):
		html_list=list()
		hostname=''
		try:
			hostname= self.raw_dict[ip]['HOSTNAME']['VALUE']
			hostname=''.join(hostname)
		except:
			__LOG__.Exception()

		html_list.append("<h3 align='center'>%s[%s]</h3><hr>" % (ip,hostname))
		html_list.append("<font color='red'>Connection NOK</font>")
		self.nok_list.append("%s[%s] - CONNECTION NOK <br>" %(ip, hostname))
		return html_list

	def endHTML(self):
		html_list=list()
		html_list.append("</body></html>")
		return html_list

	def run(self):
		html_list=list()
		
		connect_error_list = list()
		iris_list = list()
		server_list=list()
		file_list = list()
		log_list = list()
		EF_list = list()

		try:
			#ip를 key 기준으로 나눈다.
			for ip in sorted(self.raw_dict.keys()):
				if self.raw_dict[ip]['STATUS']=='NOK':
					self.connect_nok_count +=1
					connect_error_list += self.connect_nok_HTML(ip)
					continue
				if 'IRIS' in self.raw_dict[ip].keys():
					iris_list.append(ip)
				if 'DISK' in self.raw_dict[ip].keys():
					server_list.append(ip)
				if 'LOG' in self.raw_dict[ip].keys():
					log_list.append(ip)
				if 'FILE' in self.raw_dict[ip].keys():
					file_list.append(ip)
				if 'PORTS' in self.raw_dict[ip].keys():
					EF_list.append(ip)

			if len(iris_list) >0 :
				Iris = IrisHTML(self.raw_dict,sorted(iris_list, key=natural_keys))
				status_nok_count, nok_list, merge_list = Iris.get_iris_html()
				self.status_nok_count+=status_nok_count
				self.nok_list+=nok_list
				self.merge_list+=merge_list

			if len(server_list) > 0:
				Server = ServerHTML(self.raw_dict, self.config, sorted(server_list, key=natural_keys))
				status_nok_count, nok_list, merge_list = Server.get_server_html()
				self.status_nok_count +=status_nok_count
				self.nok_list+=nok_list
				self.merge_list+=merge_list

			if len(log_list) >0:
				mLog = LogMonitorHTML(self.raw_dict, self.config,sorted(log_list, key=natural_keys))
				status_nok_count, nok_list, merge_list = mLog.get_log_html()
				self.status_nok_count+=status_nok_count
				self.nok_list+=nok_list
				self.merge_list+=merge_list

			if len(file_list) >0:
				mFile = FileHTML(self.raw_dict,self.config, sorted(file_list, key=natural_keys))
				status_nok_count, nok_list, merge_list = mFile.get_file_html()
				self.status_nok_count +=status_nok_count
				self.nok_list+=nok_list
				self.merge_list+=merge_list

			if len(EF_list) > 0:
				mEF = EFHTML(self.raw_dict, self.config, sorted(EF_list, key=natural_keys))
				status_nok_count, nok_list, merge_list = mEF.get_EF_html()
				self.status_nok_count += status_nok_count
				self.nok_list+=nok_list
				self.merge_list+=merge_list


			self.nok_list = sorted(self.nok_list, key=natural_keys)

			html_list = self.PreHTML()
			html_list = html_list+self.nok_list + self.merge_list + connect_error_list
			html_list += self.endHTML()
			html = ''.join(html_list)	
			
			t = datetime.datetime.now()
			emails,title,user,passwd,smtpip,smtpport = self.get_emails_config()
			title = "[%s][CONN_NOK:%s][NOK:%s] %s" %(title, str(self.connect_nok_count),str(self.status_nok_count),str(t.strftime('%Y/%m/%d %H:%M:%S')))
			for email in emails:
				while not SHUTDOWN : 
					return
				email = email.strip()
				if email=='':
					continue
				__LOG__.Trace('['+str(datetime.datetime.now())+'] Sending Email to '+email+'!!!')
				self.send_gmail(email,title,html,user,passwd,smtpip,smtpport)
				__LOG__.Trace('['+str(datetime.datetime.now())+'] Complete.'+email+'!!!')
			__LOG__.Trace("______________________MAIL SEND COMPLETE_____________________")
		except:
			__LOG__.Exception()

def atoi(text):
	return int(text) if text.isdigit() else text
def natural_keys(text):
	key= [atoi(c) for c in re.split('(\d+)', text)]
	return key
if __name__=='__main__':
	lm = LogMoniterHTML()
	lm.run()
