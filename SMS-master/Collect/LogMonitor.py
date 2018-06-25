# -*- coding: utf-8 -*-
#!/usr/bin python

import paramiko
import sys
import signal
#import ConfigParser
import os
import Mobigen.Common.Log as Log
import re

class LogMonitor() :
	def __init__(self, _Parser) :
		self.PARSER = _Parser
		self.GetConfig()

	def GetConfig(self) :
		
		#LOG_MONITOR에서 해당 값 가져오기
		self.htConfig = {}
		for key in self.PARSER.get('LOG_MONITOR','SERVER_LIST').split(',') :
			self.htConfig[key] = { 'USER' : self.PARSER.get('RESOURCES','USER') , \
								   'PASSWD' : self.PARSER.get('RESOURCES','PASSWD'), \
								   'SSH_PORT' : self.PARSER.get('RESOURCES','SSH_PORT'), \
								   'LOG_PATH_LIST' : self.PARSER.get('LOG_MONITOR','LOG_PATH_LIST').split(','), \
								   'LOG_FIND_STRING_LIST' : self.PARSER.get('LOG_MONITOR','LOG_FIND_STRING_LIST').split(','), \
								   'VALUE_PATT' : self.PARSER.get('LOG_MONITOR','VALUE_PATT').split(','),
								   'LOG_TITLE_LIST' : self.PARSER.get('LOG_MONITOR','LOG_TITLE_LIST').split(',') }
									
		for key in self.htConfig.keys() :
			if self.PARSER.has_section(key) : 
				for option in self.htConfig[key].keys() :
					if self.PARSER.has_option(key, option) : 
						if option in ('LOG_PATH_LIST', 'LOG_FIND_STRING_LIST', 'VALUE_PATT', 'LOG_TITLE_LIST') : self.htConfig[key][option] = self.PARSER.get(key, option).split(',')
						else : 	self.htConfig[key][option] = self.PARSER.get(key, option)
		
		#로그 파일별로 Sub Find String 확인
		#self.htLogSubString = {}
		#for LogPath in self.PARSER.get('LOG_MONITOR','LOG_PATH_LIST').split(',') :
		#	if self.PARSER.has_section(LogPath) : self.htLogSubString[LogPath] = self.PARSER.get(LogPath, 'SUB_FIND_STRING_LIST').split(',')
		#__LOG__.Trace(self.htConfig)

	def sshGetLogMoniter(self, _IP, _Port, _ID, _PWD, _LogPath, _FindString) :
		result = []
		try :
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(_IP, port = int(_Port), username = _ID, password = _PWD, timeout=5 )
		except:
			__LOG__.Exception()
		try:
			for index in range(len(_LogPath)) :
				try:
					cmdList = []
					for FindStr in _FindString[index].split('|') :
						cmd = 'grep \'%s\' %s | tail -n 1' % (FindStr, _LogPath[index])
						cmdList.append([FindStr, cmd])
				except:
					for FindStr in _FindString[0].split('|') :
						cmd = 'grep \'%s\' %s | tail -n 1' % (FindStr, _LogPath[index])
						cmdList.append([FindStr, cmd])

				li = []
				for licmd in cmdList :
					FindStr, cmd = licmd
					stdin, stdout, stderr = ssh.exec_command(cmd)
			
					liResult = stdout.readlines()
					if len(liResult) == 0 : liResult = stderr.readlines()
	
					strResult = ''
					for str in liResult :
						strResult = '%s%s' % (strResult,str)
				
					li.append([_LogPath[index], FindStr, strResult.replace('\n','')])
				result.append(li)
			ssh.close()
		except :
			#Connect Error?
			__LOG__.Exception()

		#__LOG__.Trace(result)
		# [ LogPath, FindString, Log String] , ....]
		return result

	def sshGetHostName(self, _IP, _Port, _ID, _PWD) :
		result = ''
		try :
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(_IP, port = int(_Port), username = _ID, password = _PWD, timeout=5 )

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

					#__LOG__.Trace(line[len(_IP):])
					tmp = patt.search(line[len(_IP):])
					if tmp != None :
						result = tmp.group()
						#__LOG__.Trace(tmp.group())
		except :
			__LOG__.Exception()

		return result

	def GetDateTime(self, _Line) :
		result = '' 

		try : 
			patt = re.compile('\d{4}[/]\d{2}[/]\d{2}\s\d{2}[:]\d{2}[:]\d{2}')
			Value = patt.search(_Line)
			if Value != None : 
				result = Value.group(0)
				__LOG__.Trace("Datetime : %s" % result)
		except : 
			__LOG__.Exception()

		return result

	def GetValue(self, _Line, _Patt) :
		result = '' 

		#__LOG__.Trace(_Line)
		#__LOG__.Trace(_Patt)
		try :

			patt = re.compile(_Patt)
			Value = patt.search(_Line)
			#__LOG__.Trace(Value)
			if Value != None : 
				result = Value.group(0)
				__LOG__.Trace("Value : %s" % result)
		except : 
			__LOG__.Exception()

		return result 

	def run(self) :
		__LOG__.Trace("[Collect]LOG MONITOR START_______________________")	
		__LOG__.Trace(self.htConfig)
		ResultDict = {}
		try :
			for key in self.htConfig.keys() :
				liResult = self.sshGetLogMoniter(key, self.htConfig[key]['SSH_PORT'] , self.htConfig[key]['USER'], self.htConfig[key]['PASSWD'], self.htConfig[key]['LOG_PATH_LIST'], self.htConfig[key]['LOG_FIND_STRING_LIST'])

				if len(liResult) == 0 : 
					ResultDict[key] = {'STATUS' : 'NOK'}
					ResultDict[key]['HOSTNAME'] = {'VALUE' : [self.GetLocalHostName(key)]}
				else :
					ResultDict[key] = {'STATUS' : 'OK'}
					ResultDict[key]['HOSTNAME'] = {'VALUE' : [self.sshGetHostName(key, self.htConfig[key]['SSH_PORT'] , self.htConfig[key]['USER'], self.htConfig[key]['PASSWD'])]}

					index = 0
					log_dict = {}
					for	liValue in liResult : # liValue = [[ LogPath, FindString, Log String] , ....]
						for li in liValue : # li = [LogPath, FindString, Log String],[LogPath, FindString, Log String],...
							Path, FindStr, LogStr = li
							__LOG__.Trace(li)	
							if not log_dict.has_key(Path) : 
								log_dict[Path] = {}
							#Get DateTime
							DateTime = self.GetDateTime(LogStr)

							#Get Value
							if len(self.htConfig[key]['VALUE_PATT']) > 0 : 
								try: Value = self.GetValue(LogStr, self.htConfig[key]['VALUE_PATT'][index]) 
								except: Value = self.GetValue(LogStr, self.htConfig[key]['VALUE_PATT'][0])
							else : Value = ''
							
							log_dict[Path][FindStr] = {'STATUS' : 'OK' , 'VALUE' : [DateTime, Value]}
							#log_dict[Path]['VALUE'] = {FindStr : {'STATUS' : 'OK' , 'VALUE' : [DateTime, Value]}}

						try: log_dict[Path]['TITLE'] = {'VALUE' : self.htConfig[key]['LOG_TITLE_LIST'][index]}
						except: log_dict[Path]['TITLE'] = {'VALUE' : self.htConfig[key]['LOG_TITLE_LIST'][0]}
						ResultDict[key]['LOG'] = log_dict
						index+=1
		except :
			__LOG__.Exception()
		__LOG__.Trace("[Collect]LOG MONITOR END_______________________")
		return ResultDict

def Main() :
	obj = IrisStatus(sys.argv[1], sys.argv[2], sys.argv[3])
	log_dict = obj.run()
	for NodeID in log_dict.keys() :
		for Key in log_dict[NodeID].keys() :
			print '%s %s = %s' % (NodeID, Key, log_dict[NodeID][Key])

if __name__ == '__main__' :
	Main()	
