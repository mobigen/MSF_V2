# -*- coding: utf-8 -*-
#!/usr/bin python

import paramiko
import datetime
import sys
import signal
import os
import Mobigen.Common.Log as Log
import time
import re

class FileMonitor() :
	def __init__(self, _Parser) :
		self.PARSER = _Parser
		self.GetConfig()

	def GetConfig(self) :
		
		#FILE_MONITOR에서 해당 값 가져오기
		self.htConfig = {}
		for key in self.PARSER.get('FILE_MONITOR','SERVER_LIST').split(',') :
			self.htConfig[key] = { 'USER' : self.PARSER.get('RESOURCES','USER') , \
								   'PASSWD' : self.PARSER.get('RESOURCES','PASSWD'), \
								   'SSH_PORT' : self.PARSER.get('RESOURCES','SSH_PORT'), \
								   'FILE_PATH_LIST' : self.PARSER.get('FILE_MONITOR','FILE_PATH_LIST').split(','), \
								   'FILE_FIND_STRING_LIST' : self.PARSER.get('FILE_MONITOR','FILE_FIND_STRING_LIST').split(','), \
								   'FILE_TITLE_LIST' : self.PARSER.get('FILE_MONITOR','FILE_TITLE_LIST').split(',') }
									
		for key in self.htConfig.keys() :
			if self.PARSER.has_section(key) : 
				for option in self.htConfig[key].keys() :
					if self.PARSER.has_option(key, option) : 
						if option in ('FILE_PATH_LIST', 'FILE_FIND_STRING_LIST','FILE_TITLE_LIST') : 
							self.htConfig[key][option] = self.PARSER.get(key, option).split(',')
						else : 	
							self.htConfig[key][option] = self.PARSER.get(key, option)
		
		#__LOG__.Trace(self.htConfig)

	def sshGetFileMoniter(self, _IP, _Port, _ID, _PWD, _FilePath, _FindString) :
		result = []
		try :
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(_IP, port = int(_Port), username = _ID, password = _PWD, timeout=5 )
			
			for index in range(len(_FilePath)) :
				try:
					cmdList = []
					for FindStr in _FindString[index].split('|') :
						cmd = 'ls -l --full-time /%s -r -t | grep %s | tail -n 1' % (_FilePath[index],FindStr)
						cmdList.append([FindStr, cmd])
				except:
					for FindStr in _FindString[0].split('|') : 
						cmd = 'ls -l --full-time /%s -r -t | grep %s | tail -n 1' % (_FilePath[index],FindStr)
						cmdList.append([FindStr, cmd])

				li = []
				for licmd in cmdList :
					FindStr, cmd = licmd
					#__LOG__.Trace(cmd)
					stdin, stdout, stderr = ssh.exec_command(cmd)
			
					liResult = stdout.readlines()
					#drwxrwxr-x  3 junga junga 4096 2015-04-20 11:43 tutorial
					if len(liResult) == 0 : liResult = stderr.readlines()
	
					strResult = ''
					for stre in liResult :
						strResult = '%s%s' % (strResult,stre)
				
					li.append([_FilePath[index], FindStr, strResult.replace('\n','')])
				result.append(li)
			ssh.close()
		except :
			#Connect Error?
			__LOG__.Exception()

		# [ FilePath, FindString, File String] , ....]
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
						result = tmp.group(0)
		except :
			__LOG__.Exception()

		return result

	def GetDateTime(self, _Line) :
		result = ''
		try :
			patt = re.compile('\d{4}[-]\d{2}[-]\d{2} [0-9:]*')
			Value = patt.search(_Line)
			if Value != None : 
				result = str(Value.group(0))
				__LOG__.Trace("Datetime : %s " % result)
		except : 
			__LOG__.Trace(Value)
			__LOG__.Exception()

		return result

	def GetValue(self, _Line) :
		result = '' 
		try :
			Value = _Line.split()
			Value = Value[-1]
			__LOG__.Trace("%s " % Value)
			result = Value
		except : 
			__LOG__.Exception()
		return result 

	def run(self) :
		__LOG__.Trace("[Collect]FILE MONITOR START_______________________")
		__LOG__.Trace(self.htConfig)
		ResultDict = {}
		try :
			for key in self.htConfig.keys() :
				liResult = self.sshGetFileMoniter(key, self.htConfig[key]['SSH_PORT'] , self.htConfig[key]['USER'], self.htConfig[key]['PASSWD'], self.htConfig[key]['FILE_PATH_LIST'], self.htConfig[key]['FILE_FIND_STRING_LIST'])

				if len(liResult) == 0 : 
					ResultDict[key] = {'STATUS' : 'NOK'}
					ResultDict[key]['HOSTNAME'] = {'VALUE' : [self.GetLocalHostName(key)]}
				else :
					ResultDict[key] = {'STATUS' : 'OK'}
					ResultDict[key]['HOSTNAME'] = {'VALUE' : [self.sshGetHostName(key, self.htConfig[key]['SSH_PORT'] , self.htConfig[key]['USER'], self.htConfig[key]['PASSWD'])]}

					index = 0
					file_dict = {}
					for	liValue in liResult : # liValue = [[ LogPath, FindString, Log String] , ....]
						for li in liValue : # li = [LogPath, FindString, Log String],[LogPath, FindString, Log String],...
							Path, FindStr, FileStr = li
							if not file_dict.has_key(Path) : 
								file_dict[Path] = {}
							#Get DateTime
							DateTime = self.GetDateTime(FileStr)

							#Get Value
							try: Value = self.GetValue(FileStr)
							except: Value =''
							
							file_dict[Path][FindStr] = {'STATUS' : 'OK' , 'VALUE' : [DateTime, Value]}
							#file_dict[Path]['VALUE'] = {FindStr : {'STATUS' : 'OK' , 'VALUE' : [DateTime, Value]}}

						try: file_dict[Path]['TITLE'] = {'VALUE' : self.htConfig[key]['FILE_TITLE_LIST'][index]}
						except: file_dict[Path]['TITLE'] = {'VALUE' : self.htConfig[key]['FILE_TITLE_LIST'][0]}	
						index += 1
						ResultDict[key]['FILE'] = file_dict
				#__LOG__.Trace(ResultDict[key])
		except :
			__LOG__.Exception()
		__LOG__.Trace("[Collect]FILE MONITOR END_______________________")
		#__LOG__.Trace(ResultDict)
		return ResultDict

def Main() :
	obj = IrisStatus(sys.argv[1], sys.argv[2], sys.argv[3])
	file_dict = obj.run()
	for NodeID in file_dict.keys() :
		for Key in file_dict[NodeID].keys() :
			print '%s %s = %s' % (NodeID, Key, file_dict[NodeID][Key])

if __name__ == '__main__' :
	Main()	
