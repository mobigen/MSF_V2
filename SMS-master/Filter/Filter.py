# -*- coding: utf-8 -*-
#!/usr/bin python

import datetime
import sys
import os
import Mobigen.Common.Log as Log
import time

IDX_MAX = 0
IDX_MIN = 1

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

class Filter() :
	#임계치 Dict, 필터 Dict
	def __init__(self, _Parser, _ValueDict) :
		self.PARSER = _Parser
		self.ValueDict = _ValueDict
		self.GetConfig()

	def GetConfig(self) :

		"""
		임계치 값을 config에서 불러와서 dict에 넣는다.
		"""
		try :
			self.Thresholddict = {}
			
			#default Threshold 
			self.Thresholddict['DEFAULT'] = {'LOAD_AVG':self.PARSER.get('RESOURCES', 'LOAD_AVG') ,
					 'MEMORY':self.PARSER.get('RESOURCES', 'MEMORY') ,
					 'DISK':self.PARSER.get('RESOURCES', 'DISK') ,
					 'SWAP':self.PARSER.get('RESOURCES', 'SWAP'), 
					 'LOG_SECOND':self.PARSER.get('RESOURCES', 'LOG_SECOND'),
					 'FILE_SECOND':self.PARSER.get('RESOURCES','FILE_SECOND'),
					 'QUEUE_COUNT':self.PARSER.get('EVENTFLOW','QUEUE_COUNT'),
					 'IRIS_LOAD_AVG' : self.PARSER.get('IRIS','IRIS_LOAD_AVG'),
					 'IRIS_MEM_P' : self.PARSER.get('IRIS','IRIS_MEM_P'),
					 'IRIS_MEM_F' : self.PARSER.get('IRIS','IRIS_MEM_F'),
					 'IRIS_DISK' : self.PARSER.get('IRIS','IRIS_DISK')}
					
			ServerList = self.PARSER.get('RESOURCES','SERVER_LIST').split(',')
			__LOG__.Trace(ServerList)
			THRESHOLD_TYPE_LIST = ['LOAD_AVG','MEMORY','DISK','SWAP','LOG_SECOND','FILE_SECOND']
			for ServerIP in ServerList :
				value_dict = {}
				for Type in THRESHOLD_TYPE_LIST :
					try :
						tmp_str = self.PARSER.get(ServerIP,Type)
						value_dict[Type] = tmp_str
					except :
						pass
				if len(value_dict) > 0 : self.Thresholddict[ServerIP] = value_dict
				
		except :
			__LOG__.Exception()

	def GetTresholdValue(self, _Server, _Type) :
		"""사용자가 설정한 임계치를 사용하고 싶을 때 사용함"""
		try :
			if self.Thresholddict.has_key(_Server) :
				if self.Thresholddict[_Server].has_key(_Type) : return self.Thresholddict[_Server][_Type]
			
			return self.Thresholddict['DEFAULT'][_Type]
			
			__LOG__.Trace(self.Thresholddict)
		except :
			__LOG__.Exception()

		
	def run(self) :
		try :
			for Server in self.ValueDict.keys() :
				__LOG__.Trace(Server)
				__LOG__.Trace(self.ValueDict[Server])


				#상태가 NOK-접속불가면 확인할 필요 없음
				if self.ValueDict[Server]['STATUS'] == 'NOK' :
					continue

				for Type in self.ValueDict[Server].keys() :
					__LOG__.Trace('Type ----> %s' % Type)
					if Type == 'IRIS' : #{'STATUS':'OK' , 'VALUE':[SYS_STATUS, UPDATE_TIME]}
						Value = self.ValueDict[Server][Type]['VALUE']

						#만약 아이리스 SYS_STATUS가 BUSY나 WARN이 되어있으면 오류
						if Value[IDX_IRIS_SYS_STATUS] != 'VALID' : 
							self.ValueDict[Server][Type]['STATUS'] = 'NOK'
						#현재시간보다 5분이 느리다면 오류
						if datetime.datetime.strptime(Value[IDX_IRIS_UPDATE_TIME], '%Y%m%d%H%M%S') < datetime.datetime.now() - datetime.timedelta(minutes=5) : 
							self.ValueDict[Server][Type]['STATUS'] = 'NOK'
						avg = Value[IDX_IRIS_LOADAVG]
						mem_p = Value[IDX_IRIS_MEMP]
						mem_f = Value[IDX_IRIS_MEMF]
						disk = Value[IDX_IRIS_DISK]
						IRIS_LOAD_AVG = self.GetTresholdValue(Server,'IRIS_LOAD_AVG')
						IRIS_MEM_P = self.GetTresholdValue(Server,'IRIS_MEM_P')
						IRIS_MEM_F = self.GetTresholdValue(Server,'IRIS_MEM_F')
						IRIS_DISK = self.GetTresholdValue(Server,'IRIS_DISK')

						if float(avg) > float(IRIS_LOAD_AVG) :
        						self.ValueDict[Server][Type]['STATUS'] = 'NOK2'
        						self.ValueDict[Server][Type]['VALUE'][IDX_IRIS_LOADAVG] = 'NOK2 LOAD_AVG:'+str(avg)
						if float(mem_p) > float(IRIS_MEM_P) :
        						self.ValueDict[Server][Type]['STATUS'] = 'NOK2'
        						self.ValueDict[Server][Type]['VALUE'][IDX_IRIS_MEMP] = 'NOK2 MEM_P:'+str(mem_p)
						if float(mem_f) > float(IRIS_MEM_F) :
        						self.ValueDict[Server][Type]['STATUS'] = 'NOK2'
        						self.ValueDict[Server][Type]['VALUE'][IDX_IRIS_MEMF] = 'NOK2 MEM_F:'+str(mem_f)
						if float(disk) > float(IRIS_DISK) :
        						self.ValueDict[Server][Type]['STATUS'] = 'NOK2'
        						self.ValueDict[Server][Type]['VALUE'][IDX_IRIS_DISK] = 'NOK2 DISK:'+str(disk)
							
					elif Type == 'LOAD_AVG' : #{'STATUS':'OK' , 'VALUE':[1분,5분,15분]}
						for Per in self.ValueDict[Server][Type]['VALUE'] :
							ThreshValue = self.GetTresholdValue(Server, Type)
							if float(Per) > float(ThreshValue) : 
								self.ValueDict[Server][Type]['STATUS'] = 'NOK'
								break
					elif Type == 'MEMORY' or Type == 'SWAP': #{'STATUS':'OK' , 'VALUE':[Total, Used, Available, Use%]}
						ThreshValue = self.GetTresholdValue(Server, Type)
						if int(self.ValueDict[Server][Type]['VALUE'][IDX_MEMORY_USE_PER]) > int(ThreshValue) :
							self.ValueDict[Server][Type]['STATUS'] = 'NOK'
					
					elif Type == 'DISK' : #[{'STATUS':'OK', VALUE[Mount, 1M-blocks, Used, Available, Use%]}]
						ThreshValue = self.GetTresholdValue(Server, Type)
						for Disk in self.ValueDict[Server][Type] :
							if int(Disk['VALUE'][IDX_DISK_USE_PER]) > int(ThreshValue) :
								Disk['STATUS'] = 'NOK'
					
					elif Type =='FILE':
						ThreshValue = self.GetTresholdValue(Server, 'FILE_SECOND')

						for filePath in self.ValueDict[Server][Type].keys() :
							value_dict = self.ValueDict[Server][Type][filePath]
							for FindStr in value_dict.keys():
								if FindStr == 'TITLE': continue
								__LOG__.Trace(FindStr)
								Status = 'OK'
								__LOG__.Trace(value_dict[FindStr]['VALUE'])

								#파일 변경시간
								StrDateTime = value_dict[FindStr]['VALUE'][0]
								
								#파일 modify time이 없을 시 NOK
								if len(StrDateTime) ==0 : Status = 'NOK'
								else:
									try:
										StrDateTime = StrDateTime.replace('/','').replace(':','').replace(' ','')
										if type(StrDateTime) == unicode:
											StrDateTIme = StrDateTime.encode('cp949')
										DateTime = datetime.datetime(int(StrDateTime[:4]),int(StrDateTime[5:7]), int(StrDateTime[8:10]),int(StrDateTime[10:12]),int(StrDateTime[12:14]), int(StrDateTime[14:16]))
										__LOG__.Trace(DateTime)
										if DateTime < datetime.datetime.now() - datetime.timedelta(seconds=int(ThreshValue)) : Status = 'NOK'
									except:
										__LOG__.Exception()
										Status='NOK'
								value_dict[FindStr]['STATUS'] = Status

					elif Type == 'LOG' : #{'LogPath':{'STATUS':'OK', {'FindStr':{'STATUS':'OK','VALUE':[DateTime,Value]}}}}
						ThreshValue = self.GetTresholdValue(Server, 'LOG_SECOND')

						for logPath in self.ValueDict[Server][Type].keys() :
							value_dict = self.ValueDict[Server][Type][logPath]
							for FindStr in value_dict.keys() :
								if FindStr == 'TITLE' : continue
								__LOG__.Trace(FindStr)
								Status = 'OK'
								__LOG__.Trace(value_dict[FindStr]['VALUE'])
								StrDateTime = value_dict[FindStr]['VALUE'][0]
								if len(StrDateTime) == 0 : Status = 'NOK'
								else :
									try : 
										StrDateTime = StrDateTime.replace('/','').replace(':','').replace(' ','')
										if type(StrDateTime) == unicode : StrDateTime = StrDateTime.encode('cp949')
										DateTime = datetime.datetime(int(StrDateTime[:4]),int(StrDateTime[4:6]), int(StrDateTime[6:8]), int(StrDateTime[8:10]), int(StrDateTime[10:12]),int(StrDateTime[12:14]))
										__LOG__.Trace(DateTime)
										if DateTime < datetime.datetime.now() - datetime.timedelta(seconds=int(ThreshValue)) : Status = 'NOK'	
									except : 
										__LOG__.Exception()
										Status = 'NOK'
								
								value_dict[FindStr]['STATUS'] = Status
								
					elif Type == 'QUEUE_COUNT' :
                                                ThreshValue = self.GetTresholdValue(Server, Type)
                                                for val in self.ValueDict[Server][Type]:
                                                        qu = val['VALUE'].split(':')[1]
                                                        if int(qu) > int(ThreshValue) :
                                                                val['STATUS'] = 'NOK'
		except :
			__LOG__.Exception()

		return self.ValueDict

def Main() :
	obj = SMSFilter()
	value_dict = obj.run()
	for ServerID in value_dict.keys() :
		for Key in value_dict[ServerID].keys() :
			print '%s %s = %s' % (ServerID, Key, value_dict[ServerID][Key])

if __name__ == '__main__' :
	Main()	
