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


IDX_IP = 0
IDX_PORT = 1

#
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
class SMSNOKCheck() :
	#제목 / 통신사 정보 Dict / 전화번호 정보 Dict / 값 Dict
	def __init__(self, _Parser, _ValueDict,collect) :
		self.ValueDict = _ValueDict
		self.PARSER = _Parser
		self.Collect = collect
		
		self.GetConfig()
		self.status_nok_count = 0

	def GetConfig(self) :
		try :
			#SMS Noti Msg
			self.Msg = self.PARSER.get('SMS','NokMsg') 
			self.nok_limit_count = self.PARSER.get('SMS','NokLimitCount')
			
			#SMS Info
			self.CorpDict = {}
			self.CorpDict['SKT'] = [self.PARSER.get('SMS','SKTSMSIP'), self.PARSER.get('SMS','SKTSMSPort')]
			self.CorpDict['KT'] = [self.PARSER.get('SMS','KTSMSIP'), self.PARSER.get('SMS','KTSMSPort')]
			self.CorpDict['LGU'] = [self.PARSER.get('SMS','LGUSMSIP'), self.PARSER.get('SMS','LGUSMSPort')]

			#번호 정보 저장
			self.NumberDict = {}
			for numli in self.PARSER.get('SMS','NumberList').split(',') :
				if self.NumberDict.has_key(numli.split(':')[0]) : 
					self.NumberDict[numli.split(':')[0]].append(numli.split(':')[1])
				else : 
					self.NumberDict[numli.split(':')[0]] = [numli.split(':')[1]]

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
					#__LOG__.Trace(type(HostName))
					if type(HostName)==unicode : 
						HostName = HostName.encode('cp949')

					#Connected Fail
					if (Type == 'STATUS' and self.ValueDict[Server][Type] == 'NOK') : 
						self.status_nok_count +=1
					elif Type == 'IRIS' :
						if self.ValueDict[Server][Type]['STATUS'] == 'NOK' : 
							self.status_nok_count +=1
					elif Type == 'MEMORY' or Type == 'SWAP' :
						if self.ValueDict[Server][Type]['STATUS'] == 'NOK' : 
							self.status_nok_count +=1
					elif Type == 'LOAD_AVG' :
						if self.ValueDict[Server][Type]['STATUS'] == 'NOK' : 
							self.status_nok_count +=1
					elif Type == 'DISK' :
						for Disk in self.ValueDict[Server][Type] :
							__LOG__.Trace(Disk)
							if Disk['STATUS'] == 'NOK' : 
								self.status_nok_count +=1
						continue
					elif Type=='LOG':
						for LogPath in self.ValueDict[Server][Type]:
							logpath_dict = self.ValueDict[Server][Type][LogPath]
							for FindStr in logpath_dict.keys():
								if FindStr=='TITLE':
									continue
								if logpath_dict[FindStr]['STATUS'] =='NOK':
									self.status_nok_count +=1
						continue
					elif Type=='FILE':
						for FilePath in self.ValueDict[Server][Type]:
							filepath_dict = self.ValueDict[Server][Type][FilePath]
							for FindStr in filepath_dict.keys():
								if FindStr=='TITLE':
									continue
								if filepath_dict[FindStr]['STATUS'] =='NOK':
									self.status_nok_count +=1
						continue
					else : pass

			#Msg 전송 = 한 Connection 당 한 Number 메시지 전송
			for Corp in self.NumberDict.keys():
				for Number in self.NumberDict[Corp] :
					__LOG__.Trace('Corp[%s] Number[%s]' % (Corp, Number))
				
					#알람이 많이 발생할 경우 메일확인 권고메일 발송
					#사내 SMS 모듈 gmail 포워딩 버전
					if int(self.status_nok_count) > int(self.nok_limit_count) :
						sms_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						sms_sock.connect( ( self.CorpDict[Corp][IDX_IP], int(self.CorpDict[Corp][IDX_PORT]) ) )
						Msg = self.Msg % self.status_nok_count
						
						#make Msg - 왠진 모르겠으나 SEND-SMS 반드시 붙여야함, Msg는 string 이여야 하고 보낼 데이터는 cp949로...)
						Data = "SEND-SMS %s %s %s" % (self.SendNumber, Number, Msg)
						Data = Data.encode('cp949')

						__LOG__.Trace("Data : %s " % (Data))
						
						sms_sock.sendall(Data)
						sms_sock.close()

						time.sleep(2)

		except :
			__LOG__.Exception()

