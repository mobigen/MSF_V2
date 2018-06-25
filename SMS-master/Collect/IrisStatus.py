# -*- coding: utf-8 -*-
#!/usr/bin python

import paramiko
import datetime
import sys
import signal
#import ConfigParser
import os
import Mobigen.Common.Log as Log
import API.M6 as M6
import time
import re
#import subprocess

IDX_NODEID = 0
IDX_SYS_STATUS = 1
IDX_ADM_STATUS = 2
IDX_UPDATE_TIME = 3
IDX_IP = 4
IDX_CPU = 5
IDX_LOADAVG = 6
IDX_MEMP = 7
IDX_MEMF = 8
IDX_DISK = 9

class IrisStatus() :
	def __init__(self, _Parser) :
		self.PARSER = _Parser
		self.GetConfig()

	def GetConfig(self) :
		try :
			self.IRIS_IP =  self.PARSER.get('IRIS','IRIS_IP')
			self.SSH_PORT = self.PARSER.get('IRIS','SSH_PORT')
			self.USER = self.PARSER.get('IRIS','USER')
			self.PASSWD = self.PARSER.get('IRIS','PASSWD')
			self.PASSWD2 = self.PARSER.get('IRIS','PASSWD2')
			self.CMDPATH = self.PARSER.get('IRIS','CMDPATH')

			self.IRIS_CON_IP = self.PARSER.get('IRIS', 'IRIS_CON_IP')
			self.IRIS_CON_ID = self.PARSER.get('IRIS', 'IRIS_CON_ID')
			self.IRIS_CON_PWD = self.PARSER.get('IRIS', 'IRIS_CON_PWD')

		except : 
			__LOG__.Exception()

	def sshProc(self) :
		result = None
		try :
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			__LOG__.Trace('%s %s %s %s' % (self.IRIS_IP, self.SSH_PORT, self.USER, self.PASSWD))
			try:
				ssh.connect(self.IRIS_IP, port = int(self.SSH_PORT), username = self.USER, password = self.PASSWD, timeout=5 )
			except:
				ssh.connect(self.IRIS_IP, port = int(self.SSH_PORT), username = self.USER, password = self.PASSWD2, timeout=5 )

			stdin, stdout, stderr = ssh.exec_command('bash -lc %s' % self.CMDPATH)
	
			result = stdout.readlines()
			if len(result) == 0 : result = stderr.readlines()
						
			ssh.close()
		except :
			#Connect Error?
			__LOG__.Exception()

		return result

	def sshGetHostName(self, _IP) :
		result = ''
		try :
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(_IP, port = int(self.SSH_PORT), username = self.USER, password = self.PASSWD, timeout=5 )
			
			stdin, stdout, stderr = ssh.exec_command('bash -lc hostname')
	
			liResult = stdout.readlines()
			if len(liResult) == 0 : liResult = stderr.readlines()
			
			for str in liResult :
				result = '%s%s' % (result,str)
				
			result = result.replace('\n','')
			ssh.close()
		except :
			#Connect Error?
			__LOG__.Exception()

		return result
	
	def GetLocalHostName(self, _IP) :
		strip = _IP
		if type(strip) == unicode : strip = strip.encode('cp949')

		result = ''
		patt = re.compile('(\S+)')
		try :
			f = os.popen('cat /etc/hosts')
			li = f.readlines()

			for line in li :
				if line.find(strip) >= 0 : 
					
					__LOG__.Trace(line[len(_IP):])
					tmp = patt.search(line[len(_IP):])
					if tmp != None :
						result = tmp.group()
						__LOG__.Trace(tmp.group())
		except :
			__LOG__.Exception()

		return result
	def run(self) :
		__LOG__.Trace("[Collect]IRIS STATUS START_______________________")		
		ResultDict = {}
		try :
			strResult = self.sshProc()

			if strResult == None :
				ResultDict[self.IRIS_IP] = {'STATUS' : 'NOK'}
				ResultDict[self.IRIS_IP]['HOSTNAME'] = {'VALUE' : [self.GetLocalHostName(self.IRIS_IP)]}
			elif str(strResult).find('Failed') >= 0 :
				__LOG__.Trace(strResult)
				ResultDict[self.IRIS_IP] = {'STATUS' : 'NOK'}
				ResultDict[self.IRIS_IP]['HOSTNAME'] = {'VALUE' : [self.GetLocalHostName(self.IRIS_IP)]}
			elif str(strResult).find('bash') >= 0 : #실행 파일 존재 않함
				__LOG__.Trace(strResult)
				ResultDict[self.IRIS_IP] = {'STATUS' : 'NOK'}
				ResultDict[self.IRIS_IP]['HOSTNAME'] = {'VALUE' : [self.GetLocalHostName(self.IRIS_IP)]}
			else :
				#0 - Header
				#1 , lastLine ===========

				irisListenerStatus = 'NOK'

				try : 
					conn = M6.Connection(self.IRIS_CON_IP, self.IRIS_CON_ID, self.IRIS_CON_PWD, Direct = True)
					curs = conn.Cursor()
					curs.SetFieldSep(',')
					curs.SetRecordSep('\n')
					curs.SetTimeout(120)

					sql = '''table list'''

					strRes = None
					strRes = curs.Execute2(sql)

					if strRes[:3] == '+OK' :
						irisListenerStatus = 'OK'

					curs.Close()
					conn.close()
				except :
					__LOG__.Exception() 

				for line in strResult[2:] :
					li = line.replace(' ','').replace('\n','').split(',')
					#Key(Type) : [Value, Desc]
					__LOG__.Trace(li)
					irisDict = {'STATUS' : 'OK' ,'VALUE' :[li[IDX_NODEID], li[IDX_SYS_STATUS], li[IDX_ADM_STATUS], li[IDX_UPDATE_TIME], li[IDX_CPU], li[IDX_LOADAVG], li[IDX_MEMP], li[IDX_MEMF], li[IDX_DISK]]}

					#Hostname 가져오기
					strHostName = self.sshGetHostName(li[IDX_IP])
					dict = {'STATUS' : 'OK' , 'IRIS' : irisDict, 'IRIS_LISTENER' : irisListenerStatus}
					if strResult == None or str(strResult).find('bash') >= 0 : 
						#접속이 되지 않았거나 명령어가 정상적으로 수행이 되지 않았으면
						dict['HOSTNAME'] = {'VALUE' : [self.GetLocalHostName(li[IDX_IP])]}
					else : dict['HOSTNAME'] = {'VALUE' : [strHostName]}
					ResultDict[li[IDX_IP]] = dict
		except :
			__LOG__.Exception()
	
		#__LOG__.Trace(ResultDict)
		__LOG__.Trace("[Collect]IRIS STATUS END_______________________")
		return ResultDict

def Main() :
	obj = IrisStatus(sys.argv[1], sys.argv[2], sys.argv[3])
	dict = obj.run()
	for NodeID in dict.keys() :
		for Key in dict[NodeID].keys() :
			print '%s %s = %s' % (NodeID, Key, dict[NodeID][Key])

if __name__ == '__main__' :
	Main()	
