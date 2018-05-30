#!/data01/mobizen1/bin/python
# -*- coding: cp949 -*-

__doc__ = """
	import Mobigen.DataProcessing.CSV2

	w = CSV.Writer("/path", CSV.PARTITION, Mode="a")
	w.put(msgTime, line)

	w = CSV.Writer("/path/filename", CSV.FILE, Mode="a")
	w.append(line)
"""

import re
import os
import glob
import time
import Mobigen.DataProcessing.CSV2
from Mobigen.DataProcessing.CSV2.Exception import *
import Mobigen.Common.Log as Log; Log.Init()


FLUSHMODE = True

class Writer :
	
	def __init__(self, path, type, **args) :
		global FLUSHMODE

		self.path = path.rstrip('/')
		self.type = type
		self.curFileTime = "00000000000000"
		self.curFD = None
		self.separate = ","
		self.curLineNum = 0
		
		try: self.prefix = args["Prefix"] + '_'
		except: self.prefix = "" # add

		try : self.mode = args["Mode"]
		except : self.mode = "w"

		try : self.keepHour = args["KeepHour"]
		except : self.keepHour = 24

		try : self.intervalTime = args["FileTimeInterval"]
		except : self.intervalTime = -1

		try : self.lineNum = args["lineNum"]
		except : self.lineNum = 0

		try : self.partition = args["Partition"]
		except : self.partition = "1H"

		if (self.type == Mobigen.DataProcessing.CSV2.PARTITION) :
			FLUSHMODE = True
			if (os.path.isfile(path)) :
				raise TypeDefineErrorException
			else :	
				try : os.makedirs(path)
				except : pass
			if self.mode == "a":
				pattern = self.makeFileName("[0-9]" * 14)
				list = glob.glob(pattern)
				if list:
					lastfile = max(list)
					s = re.search("(\d{14}).csv", lastfile) # only works between 1000AD and 9999AD
					lasttime = s.group(1)
					self.curFileTime = lasttime
					self.CreateFD(lastfile)

		if (self.type == Mobigen.DataProcessing.CSV2.FILE) :
			FLUSHMODE = False
			if (os.path.isfile(path) == False) :
				if (os.path.exists(path) == True) :
					raise TypeDefineErrorException
				else : 
					try : os.makedirs(os.path.dirname(path))
					except : pass
			else :
				try : os.makedirs(os.path.dirname(path))
				except : pass
				

			self.CreateFD(path)

	def __del__(self) :
		self.Close()

	def CreateFD(self, path) :
		if (self.mode == "w") : self.curFD = open(path, "w")
		elif (self.mode == "a") : self.curFD = open(path ,"a")
		else : raise ModeDefineErrorException

	def Close(self) :
		try : self.curFD.close()
		except : pass

	def SetSeparate(self, sep) :
		self.separate = sep

	def makeFileTimeByMsgTime(self, msgTime) :
		if (self.partition == "1M") : return msgTime[:12] + '00'
		else : return msgTime[:10] + '0000'

	def makeFileName(self, fileTime) :
		return "%s/%s%s%s" % (self.path, self.prefix, fileTime, '.csv')


	def rmData(self) :
		s = re.search("^(\d{4})(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)$", self.curFileTime)
		julFmtStr = "%s-%s-%s %s:%s:%s" % (s.group(1), s.group(2), s.group(3), s.group(4), s.group(5), s.group(6))
		julTime = time.mktime(time.strptime(julFmtStr, "%Y-%m-%d %H:%M:%S"))
		if (self.partition  == "1M") : strFormat = "%Y%m%d%H%M00"
		else : strFormat = "%Y%m%d%H0000"
		rmFileTime = time.strftime(strFormat, time.localtime(julTime - (3600 * self.keepHour)))
		rmFileName = self.makeFileName(rmFileTime)

		filePattern = self.makeFileName("20*")
		fileNames = glob.glob(filePattern)
		fileNames.sort()

		for fname in fileNames :
			if (fname < rmFileName) :
				os.remove(fname)

	def DataCheck(self, listData) :
		size = len(listData)
		for i in range(size) :
			if(listData[i] == None) : listData[i] = ""
			else : listData[i] = str(listData[i])

		return listData

	def WriteLine(self, line) :
		line = line.strip()
		self.curFD.write(line + "\n")
		if(FLUSHMODE) :	self.curFD.flush()

	def append(self, line) :
	#	self.WriteLine(line)
		line = line.strip()
		self.curFD.write(line + "\n")
		if(FLUSHMODE) :	self.curFD.flush()

	def put(self, msgTime, line) :
		if (not msgTime or len(msgTime)<14) : return
		fileTime = self.makeFileTimeByMsgTime(msgTime)

		if (fileTime > self.curFileTime) :
			if (self.intervalCheck(fileTime, self.curFileTime)) :
				self.curFileTime = fileTime
				fileName = self.makeFileName(self.curFileTime)	
				if (self.curFD) : self.Close()
				self.CreateFD(fileName)
				self.rmData()
			else :
				return

		self.WriteLine(line)

	def putEx(self, line) :
		if (self.curLineNum == 0) :
			while True :
				curTime = time.strftime("%Y%m%d%H%M%S")
				if (self.curFileTime != curTime) : break
			self.curFileTime = curTime
			fileName = self.makeFileName(self.curFileTime)
			if (self.curFD) : self.Close()
			self.CreateFD(fileName)
			self.rmData()

		self.curLineNum += 1
		if (self.curLineNum == self.lineNum) :
			self.curLineNum = 0

		self.WriteLine(line)


	def intervalCheck(self, newTime, oldTime) :
		try :
			if(self.intervalTime == -1 or oldTime=="00000000000000") :
				return True

			ntime = time.mktime(time.strptime(newTime[:10],'%Y%m%d%H'))
			otime = time.mktime(time.strptime(oldTime[:10],'%Y%m%d%H'))

			interval = (ntime - otime) / 3600

			if( interval <= self.intervalTime ) : return True
			else : return False
		except :
			return False
