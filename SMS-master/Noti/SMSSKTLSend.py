# -*- coding: utf-8 -*-
#!/usr/bin python

import datetime
import sys
import os
import re

import Mobigen.Common.Log as Log
from socket import *
import time
#import ConfigParser
import struct
import MariaDB

IDX_IP = 0
IDX_PORT = 1

IDX_VALUE = 0
IDX_DESC = 1

IDX_IRIS_NODEID = 0
IDX_IRIS_SYS_STATUS = 1
IDX_IRIS_ADM_STATUS = 2
IDX_IRIS_UPDATE_TIME = 3
IDX_IRIS_CPU = 4
IDX_IRIS_LOADAVG = 5
IDX_IRIS_MEMP = 6
IDX_IRIS_MEMF = 7
IDX_IRIS_DISK = 8

IDX_MEMORY_TOTAL = 0
IDX_MEMORY_USED = 1
IDX_MEMORY_AVAILABE = 2
IDX_MEMORY_USE_PER = 3

IDX_DISK_MOUNT = 0
IDX_DISK_1MBLOCKS = 1
IDX_DISK_USED = 2
IDX_DISK_AVAILABLE = 3
IDX_DISK_USE_PER = 4

IDX_LOG_DATE = 0
IDX_LOG_VALUE = 1
IDX_FILE_VALUE =1 
class SMSSKTLSend() :

	#제목 / 통신사 정보 Dict / 전화번호 정보 Dict / 값 Dict
	def __init__(self, _Parser, _ValueDict,collect) :
		self.ValueDict = _ValueDict
		self.PARSER = _Parser
		self.Collect = collect
		
		self.GetConfig()
		self.MariaDB.MariaDB(self.PARSER)
		
	def GetConfig(self) :
		try :
			#SMS Info
			self.CorpDict = {}

			self.NumberDict = {}
			for numli in self.PARSER.get('SMS','NumberList').split(',') :
				if self.NumberDict.has_key(numli.split(':')[0]) : self.NumberDict[numli.split(':')[0]].append(numli.split(':')[1])
				else : self.NumberDict[numli.split(':')[0]] = [numli.split(':')[1]]

			self.Title = self.PARSER.get('SMS','Title')
			self.SendNumber = self.PARSER.get('SMS','SendNumber')
		except :
			__LOG__.Exception()

	def run(self) :
		try :
			#Make Msg List
			MsgList = []
			for Server in self.ValueDict.keys() :
				for Type in self.ValueDict[Server].keys() :
					Msg = ''

					HostName = self.ValueDict[Server]['HOSTNAME']['VALUE'][0]
					__LOG__.Trace(type(HostName))
					if type(HostName)==unicode : HostName = HostName.encode('cp949')


					#Connected Fail
					if (Type == 'STATUS' and self.ValueDict[Server][Type] == 'NOK') : 
						Msg = '[%s]\n%s\n(%s)\nConnected Fail' % (self.Title, Server,HostName)
					elif Type == 'IRIS' :
						if self.ValueDict[Server][Type]['STATUS'] == 'NOK' : 
							Desc = self.ValueDict[Server][Type]['VALUE'][IDX_IRIS_SYS_STATUS] + '/' + self.ValueDict[Server][Type]['VALUE'][IDX_IRIS_UPDATE_TIME]
							Msg = '[%s]\n%s\n(%s)\n%s\n%s' % (self.Title, Server, HostName, Type, Desc)
						
						if self.ValueDict[Server][Type]['STATUS'] == 'NOK2' :
							iris_stats_L = self.ValueDict[Server][Type]['VALUE'][5:9]
							noti_L = []
							for stat in iris_stats_L:
								if stat.find('NOK2') >= 0 :
									noti_L.append(stat.strip())
							Desc = '\n'.join(noti_L).replace('NOK2','')
							Msg = '[%s]\n%s\n%s \n%s' % (self.Title, HostName, Type, Desc)
							Msg = Msg.decode('utf-8')
					elif Type == 'MEMORY' or Type == 'SWAP' :
						#__LOG__.Trace(self.ValueDict[Server][Type]['VALUE'][IDX_MEMORY_USE_PER])
						if self.ValueDict[Server][Type]['STATUS'] == 'NOK' : 
							Msg = '[%s]\n%s\n(%s)\n%s\n%s(%%)' % (self.Title, Server, HostName, Type, self.ValueDict[Server][Type]['VALUE'][IDX_MEMORY_USE_PER])
					elif Type == 'LOAD_AVG' :
						if self.ValueDict[Server][Type]['STATUS'] == 'NOK' : 
							Msg = '[%s]\n%s\n(%s)\n%s\n%s' % (self.Title, Server, HostName, Type, '/'.join(self.ValueDict[Server][Type]['VALUE']))
					elif Type == 'DISK' :
						for Disk in self.ValueDict[Server][Type] :
							__LOG__.Trace(Disk)
							if Disk['STATUS'] == 'NOK' : 
								Msg = '[%s]\n%s\n(%s)\n%s\n%s\n%s(%%)' % (self.Title, Server, HostName, Type, Disk['VALUE'][IDX_DISK_MOUNT], Disk['VALUE'][IDX_DISK_USE_PER])
								Msg = Msg.decode('utf-8')
								MsgList.append(Msg)
						continue
					elif Type=='LOG':
						for LogPath in self.ValueDict[Server][Type]:
							logpath_dict = self.ValueDict[Server][Type][LogPath]
							for FindStr in logpath_dict.keys():
								if FindStr=='TITLE':
									continue
								if logpath_dict[FindStr]['STATUS'] =='NOK':
									sample = logpath_dict[FindStr]['VALUE'][IDX_LOG_VALUE]
									Msg = '[%s]\n%s(%s)\n%s(%s)\n%s\n%s' % (self.Title, Server, HostName, Type, logpath_dict['TITLE']['VALUE'],logpath_dict[FindStr]['VALUE'][IDX_LOG_DATE],sample)
									Msg = Msg.decode('utf-8')
									MsgList.append(Msg)
						continue
					elif Type=='FILE':
						for FilePath in self.ValueDict[Server][Type]:
							filepath_dict = self.ValueDict[Server][Type][FilePath]
							for FindStr in filepath_dict.keys():
								if FindStr=='TITLE':
									continue
								if filepath_dict[FindStr]['STATUS'] =='NOK':
									Msg = '[%s]\n%s(%s)\n%s(%s)\n%s\n%s' % (self.Title, Server, HostName, Type, filepath_dict['TITLE']['VALUE'],filepath_dict[FindStr]['VALUE'][IDX_LOG_DATE],filepath_dict[FindStr]['VALUE'][IDX_FILE_VALUE])
									Msg = Msg.decode('utf-8')
									MsgList.append(Msg)
									__LOG__.Trace(MsgList)
						continue
					elif Type=='QUEUE_COUNT':
												for val in self.ValueDict[Server][Type] :
														__LOG__.Trace(val)
														if val['STATUS'] == 'NOK' :
																Msg = '[%s]\n%s\n%s \n%s' % (self.Title, HostName, Type, val['VALUE'])
																Msg = Msg.decode('utf-8')
																MsgList.append(Msg)
												continue
					else : pass

					if len(Msg) > 0 :
						Msg = Msg.decode('utf-8')
						MsgList.append(Msg)

			#Msg 전송 = 한 Connection 당 한 Number 메시지 전송
			for Corp in self.NumberDict.keys():
				for Number in self.NumberDict[Corp] :
					__LOG__.Trace('Corp[%s] Number[%s]' % (Corp, Number))
					for Msg in MsgList :
						Msg = Msg.encode('cp949')
						__LOG__.Trace(Msg)
						self.putSMS(Number, self.SendNumber, self.Title , Msg)
		except :
			__LOG__.Exception()

	def putSMS(self, recvPhoneNo, sendPhoneNo, title, addedText):
		
		time_now = datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d%H%M%S')
		Text = '[%s]\n%s' % (title, addedText)

		used_cd = '00'
		content_cnt = 0
		content_mime_type = ''
		mms_title = ''

		if len(Text) >= 140 :
			used_cd = '10'
			content_cnt = 1
			content_mime_type = 'text/plain'
			mms_title = 'SKTLNMS NOTI'

		sSQL = "insert into TBL_SUBMIT_QUEUE values ('', '1', 'NMS_T1', '1', '%s', 'I', '%s', '1', '%s', '%s', '', '00000', '%s', '',%d,'%s','','%s', '','','','','0','','%s','','','','','','',0,0,0);" % (used_cd, time_now, recvPhoneNo, sendPhoneNo, Text, content_cnt, content_mime_type, time_now, mms_title)
		
		self.DB.excuteQuery(sSQL)
				__LOG__.Trace("SQL : %s" % sSQL)
				#__LOG__.Trace("Send SMS to RECV PHONE NO : %s success" % recvPhoneNo)
			except:
				__LOG__.Exception()


