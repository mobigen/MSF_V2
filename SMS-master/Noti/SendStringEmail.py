#! usr/env python
#coding:utf8

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.header import Header
from email import Encoders

#import ConfigParser
import smtplib
import datetime
import sys
import signal
import Mobigen.Common.Log as Log

SHUTDOWN = False

def signalHandler(sigNum, frame):
	global SHUTDOWN
	self.SHUTDOWN = True
	sys.stderr.write('Catch Signal %s',sigNum)
	sys.stderr.flush()

signal.signal(signal.SIGTERM, signalHandler)
signal.signal(signal.SIGINT, signalHandler)
signal.signal(signal.SIGHUP, signalHandler)
signal.signal(signal.SIGPIPE, signalHandler)


class SendStringEmail(object):
	def __init__(self, confParser, dict_obj):
		self.config = confParser
		self.raw_dict = dict_obj

	def getConfParser(self):
		title = self.config.get('EMAIL','TITLE')
		emaillist = self.config.get('EMAIL','EMAILLIST').split(',')
		user = self.config.get('EMAIL','SEND_USER')
		passwd = self.config.get('EMAIL','SEND_PASSWD')
		smtpip = self.config.get('EMAIL','SMTP_IP')
		smtpport = self.config.get('EMAIL','SMTP_PORT')
		return (title, emaillist, user, passwd, smtpip, smtpport)

	def sendGmail(self, to, subject, html, user, passwd, smtp_ip, smtp_port, attach=None):
		msg = MIMEMultipart('alternative')
		msg['From']=user
		msg['To']=to
		msg['Subject']=Header(subject,'utf-8')
		msg.attach(MIMEText(html, 'html', 'utf-8'))

		mailServer = smtplib.SMTP(smtp_ip,smtp_port)
		mailServer.ehlo()
		mailServer.starttls()
		mailServer.ehlo()
		mailServer.login(user,passwd)
		mailServer.sendmail(user, to, msg.as_string())
		mailServer.close()

	def run(self):
		html = str(self.raw_dict)#dict를 받아서 넘김
		now_time = datetime.datetime.now()
		title, emails, user, passwd, smtpip, smtpport = self.getConfParser()
		subject = '[' + title + '] ' + str(now_time.strftime("%Y/%m/%d %H:%M:%S"))  
		for email in emails:
			while SHUTDOWN:
				return
			email = email.strip()
			if email=='':
				continue
			__LOG__.Trace('['+str(datetime.datetime.now())+'] Sending Email to '+email+'!!!')
			self.sendGmail(email,subject,html,user,passwd,smtpip,smtpport)
			__LOG__.Trace('['+str(datetime.datetime.now())+'] Complete.'+email+'!!!')
		__LOG__.Trace("______________________MAIL SEND COMPLETE_____________________")
