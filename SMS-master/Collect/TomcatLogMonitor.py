# -*- coding: utf-8 -*-
#!/usr/bin python

import paramiko
import sys
import signal
import os
import Mobigen.Common.Log as Log
import re

class IndxHandler :

	def __init__(self, sRdir, sRidx) :

		self.sRdir = sRdir
		self.sBase = ''
		self.sRidx = sRidx

		if not os.path.exists(os.path.dirname(self.sRidx)) :
			os.makedirs(os.path.dirname(self.sRidx))

	def read(self) :

		try :
			oIndx = open( self.sRidx, 'r')
			sName, sLnum = oIndx.readline().strip().split(',')
			oIndx.close()
		except Exception, ex :
			sName, sLnum = self.make()

		self.FileName = sName
		self.FileLine = int(sLnum)

		__LOG__.Trace(self.sRidx)
		__LOG__.Trace(self.FileName)
		__LOG__.Trace(self.FileLine)

		return ( sName, int(sLnum) )

	def save(self) :

		try :
			__LOG__.Trace('Index Save [%s/%s]' % (self.FileName, self.FileLine))
			oIndx = open( self.sRidx, 'w' )
			oIndx.write( self.FileName + "," + str(self.FileLine) + "\n")
			oIndx.close()
		except Exception, ex :
			__LOG__.Exception()
			#__LOG__.Exception("Oops: %s" % (str(ex)))
			pass

	def make(self) :

		#self.sBase = self.sBase.replace('%', '%%')
		sTemp = time.strftime( self.sBase ) if self.sBase.find('%') >= 0 else self.sBase
		sRdnm = os.path.join( self.sRdir, sTemp ) + '.log' ; sRnum = "0"

		return ( sRdnm, int(sRnum) )

#로컬만 할꺼임
class TomcatLogMonitor() :
	def __init__(self, _Parser) :
		self.PARSER = _Parser
		self.GetConfig()
		self.GetIndexData()

   #Last Path 만큼 IndexHandler를 만듬
	def GetIndexData(self) :
		try :
	 		self.INDEX_HANDLER = IndxHandler( self.LOG_PATH, self.INDEX_PATH)
			self.INDEX_HEADLER.read()

	 		__LOG__.Trace(len(self.PATHDICT.keys()))
		except :
			__LOG__.Exception()

	def GetConfig(self) :
		
		#LOG_MONITOR에서 해당 값 가져오기
		self.LOG_PATH = self.PARSER.get('RESOURCES','USER')
		self.FILE_PATTERN = self.PARSER.get('RESOURCES','USER')
		self.FIND_STRING = self.PARSER.get('RESOURCES','USER')
		self.INDEX_PATH = self.PARSER.get('RESOURCES','USER')

	 def GetFileList(self) :
		 li = []
		 try :
			 FindPath = os.path.join(os.path.join(self.LOG_PATH), self.FILE_PATTERN)
			 liTemp = glob.glob(FindPath)
			 liTemp.sort(reverse = True)

			 for FilePath in liTemp :
				BaseName = os.path.basename(FilePath)
				if len(BaseName.split('.')) == 2 : #*.log인 경우에만 오늘 날짜로 변환
					FilePath = FilePath[:-4] + datetime.datetime.now().strftime('%Y-%d-%m') + FilePath[-4:]

				 if FilePath >= self.INDEX_HANDLER.FileName :
					 li.insert(0,FilePath)
				 else :
					 break

		 except :
			 __LOG__.Exception()

		 return li

	def GetTomcatLogMoniter(self) :
	
		liResult = []

		FileList = self.GetFileList()

		ReadFlag = False

		for strPath in FileList :
			
			if strPath != self.INDEX_HANDLER.FileName : self.INDEX_HANDLER.FileLine = 1

			if strPath.find(datetime.datetime.now().strftime('%Y-%m-%d')) >= 0 : strPath2 = strPath.replace('.' + datetime.datetime.now().strftime('%Y-%m-%d'),'')
			else : strPath2 = strPath

			cmd = 'tail -n +%d %s' % (self.INDEX_HANDLER.FileLine, strPath2)

			lines = os.popen(cmd)
			
			for line in lines :
				try : 
					if line.find(self.FIND_STRING) >= 0 :
				
					liResult.append(line)
		
				except : 
					__LOG__.Exception()

				self.INDEX_HANDLER.FileLine += 1
			
		return liresult

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
		__LOG__.Trace("[Collect]TOMCAT LOG MONITOR START_______________________")	
		__LOG__.Trace(self.htConfig)
		ResultDict = {}
		try :
			for key in self.htConfig.keys() :
				liResult = self.GetTomcatLogMoniter()

				ResultDict[key]['HOSTNAME'] = {'VALUE' : [self.GetLocalHostName(key)]}

				log_dict = {}

				if len(liResult) > 0 :
					DateTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
					log_dict = {'STATUS' : 'NOK' , 'VALUE' : [DateTime, liResult[0]]}
					try: log_dict['TITLE'] = {'VALUE' : 'TOMCAT LOG'}
					except: log_dict['TITLE'] = {'VALUE' : self.htConfig[key]['LOG_TITLE_LIST'][0]}
					ResultDict[key]['TOMCAT'] = log_dict
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
