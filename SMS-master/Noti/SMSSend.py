# -*- coding: utf-8 -*-
#!/usr/bin python

import datetime
import sys
import os
import Mobigen.Common.Log as Log
import socket
import time

IDX_IP = 0
IDX_PORT = 1

IDX_VALUE = 0
IDX_DESC = 1

IDX_MEMORY_TOTAL = 0
IDX_MEMORY_USED = 1
IDX_MEMORY_AVAILABE = 2
IDX_MEMORY_USE_PER = 3

IDX_DISK_MOUNT = 0
IDX_DISK_1MBLOCKS = 1
IDX_DISK_USED = 2
IDX_DISK_AVAILABLE = 3
IDX_DISK_USE_PER = 4

class SMSSend() :
	#제목 / 통신사 정보 Dict / 전화번호 정보 Dict / 값 Dict
	def __init__(self, _Parser, _ValueDict, _CollectName) :
		self.ValueDict = _ValueDict
		self.PARSER = _Parser
		self.CollectName = _CollectName

		self.GetConfig()

	def GetConfig(self) :
		try :
			#SMS Info
			self.CorpDict = {}
			self.CorpDict['SKT'] = [self.PARSER.get('SMS','SKTSMSIP'), self.PARSER.get('SMS','SKTSMSPort')]
			self.CorpDict['KT'] = [self.PARSER.get('SMS','KTSMSIP'), self.PARSER.get('SMS','KTSMSPort')]
			self.CorpDict['LGU'] = [self.PARSER.get('SMS','LGUSMSIP'), self.PARSER.get('SMS','LGUSMSPort')]

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
					#Connected Fail
					if (Type == 'STATUS' and self.ValueDict[Server][Type] == 'NOK') : Msg = '[%s] %s Connected Fail' % (self.Title, Server)
					elif Type == 'IRIS' : 
						if self.ValueDict[Server][Type]['STATUS'] == 'NOK' : Msg = '[%s] %s %s %s' % (self.Title, Server, Type, '/'.join(self.ValueDict[Server][Type]['VALUE']))
					elif Type == 'MEMORY' or Type == 'SWAP' :
						#__LOG__.Trace(self.ValueDict[Server][Type]['VALUE'][IDX_MEMORY_USE_PER])
						if self.ValueDict[Server][Type]['STATUS'] == 'NOK' : Msg = '[%s] %s %s %s(%%)' % (self.Title, Server, Type, self.ValueDict[Server][Type]['VALUE'][IDX_MEMORY_USE_PER])
					elif Type == 'LOAD_AVG' :
						if self.ValueDict[Server][Type]['STATUS'] == 'NOK' : Msg = '[%s] %s %s %s' % (self.Title, Server, Type, '/'.join(self.ValueDict[Server][Type]['VALUE']))
					elif Type == 'DISK' :
						for Disk in self.ValueDict[Server][Type] :
							__LOG__.Trace(Disk)
							if Disk['STATUS'] == 'NOK' : Msg = '[%s] %s %s %s %s(%%)' % (self.Title, Server, Type, Disk['VALUE'][IDX_DISK_MOUNT], Disk['VALUE'][IDX_DISK_USE_PER])
					else : pass

					if len(Msg) > 0 :
						Msg = Msg.decode('utf-8')
						MsgList.append(Msg)

			#Msg 전송 = 한 Connection 당 한 Number 메시지 전송
			for Corp in self.NumberDict.keys():			
				for Number in self.NumberDict[Corp] :
					__LOG__.Trace('Corp[%s] Number[%s]' % (Corp, Number))
					for Msg in MsgList :
						sms_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						sms_sock.connect( ( self.CorpDict[Corp][IDX_IP], int(self.CorpDict[Corp][IDX_PORT]) ) )
					
						#Make Msg
						Data = u'SEND-SMS %s %s %s' % (self.SendNumber, Number, Msg)
						Data =Data.encode('cp949')
						__LOG__.Trace("Data : %s" % (Data))
						sms_sock.sendall(Data)
						sms_sock.close()
						time.sleep(2) #빨리 보내면 안감 ㅡㅡ; 그래서 Sleep 줌
		except :
			__LOG__.Exception()

def Main() :
	obj = SMSFilter()
	dict = obj.run()
	for ServerID in dict.keys() :
		for Key in dict[ServerID].keys() :
			print '%s %s = %s' % (ServerID, Key, dict[ServerID][Key])

if __name__ == '__main__' :
	Main()	
