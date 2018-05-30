#!/data01/mobizen1/bin/python
# -*- coding: cp949 -*-

__doc__ = """
	import Mobigen.DataProcessing.CSV

	w = CSV.Writer("/path", CSV.PARTITION, Mode="a")
	w.put(msgTime, line)

	w = CSV.Writer("/path/filename", CSV.FILE, Mode="a")
	w.append(line)
"""

import re
import os
import glob
import time
import StringIO
import Mobigen.DataProcessing.CSV2
from Mobigen.DataProcessing.CSV2.Exception import *
import Mobigen.Common.Log as Log; Log.Init()


FLUSHMODE = True

class Writer2 :
	
	def __init__(self, path, type, **args) :
		global FLUSHMODE

		self.path = path
		self.type = type
		self.curFileTime = "00000000000000"
		self.curFD = None
		self.separate = ","
		self.curLineNum = 0
		self.bufData = []
		self.bufCnt = 0

		try : self.mode = args["Mode"]
		except : self.mode = "w"

		try : self.keepHour = args["KeepHour"]
		except : self.keepHour = 24

		try : self.intervalTime = args["FileTimeInterval"]
		except : self.intervalTime = -1

		try : self.lineNum = args["lineNum"]
		except : self.lineNum = 0

		try : self.bufSize = args["Buffer"]
		except : self.bufSize = 0

		if (self.type == Mobigen.DataProcessing.CSV.PARTITION) :
			FLUSHMODE = True
			if (os.path.isfile(path)) :
				raise TypeDefineErrorException
			else :	
				try : os.makedirs(path)
				except : pass

		if (self.type == Mobigen.DataProcessing.CSV.FILE) :
			FLUSHMODE = False
			if (os.path.isfile(path) == False) :	# 파일이 아닌데 path가 존재하면 Exception
				if (os.path.exists(path) == True) :
					raise TypeDefineErrorException
				else : 
					try : os.makedirs(os.path.dirname(path))
					except : pass
			else :
				try : os.makedirs(os.path.dirname(path))
				except : pass
				

			self.CreateFD(path)

	def CreateFD(self, path) :
		if (self.mode == "w") : self.curFD = open(path, "w")
		elif (self.mode == "a") : self.curFD = open(path ,"a")
		else : raise ModeDefineErrorException

	def Close(self) :
		if (len(self.bufData)) :
			joinData = "\n".join(self.bufData)
			self.curFD.write(joinData + "\n")

		try : self.curFD.close()
		except : pass

	def SetSeparate(self, sep) :
		self.separate = sep

	def makeFileTimeByMsgTime(self, msgTime) :
		return msgTime[:10] + '0000'

	def makeFileName(self, fileTime) :
		return "%s/%s%s" % (self.path, fileTime, '.csv')

	def WriteLine(self, line) :
		line = line.strip()
		if (self.bufSize == 0) :
			self.curFD.write(line + "\n")
		else :
			self.bufData.append(line)
			self.bufCnt += 1
			if (self.bufSize == self.bufCnt) :
				joinData = "\n".join(self.bufData)
				self.curFD.write(joinData + "\n")
				self.bufData = []
				self.bufCnt = 0
				
		if(FLUSHMODE) :	self.curFD.flush()

	def rmData(self) :
		s = re.search("^(\d{4})(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)$", self.curFileTime)
		julFmtStr = "%s-%s-%s %s:%s:%s" % (s.group(1), s.group(2), s.group(3), s.group(4), s.group(5), s.group(6))
		julTime = time.mktime(time.strptime(julFmtStr, "%Y-%m-%d %H:%M:%S"))
		rmFileTime = time.strftime("%Y%m%d%H0000", time.localtime(julTime - (3600 * self.keepHour)))
		rmFileName = self.makeFileName(rmFileTime)

		filePattern = self.makeFileName("20*")
		fileNames = glob.glob(filePattern)
		fileNames.sort()

		for fname in fileNames :
			if (fname < rmFileName) :
				os.remove(fname)

	def append(self, line) :
		self.WriteLine(line)

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
