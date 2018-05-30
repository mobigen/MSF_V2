__doc__ = """
import Mobigen.DataProcessing.CSV2

w = CSV.Reader("/path", CSV.PARTITION)
w.next()


w = CSV.Reader("/path/filename", CSV.FILE)
w.readline()
w.readlines()
for data in w :
	print data
"""

import time
import glob
import os.path

import Mobigen.DataProcessing.CSV2 
from Mobigen.DataProcessing.CSV2.Exception import *

import Mobigen.Common.Log as Log; Log.Init()

class Reader :
	def __init__(self, path, type, prefix = '', **args) :
		self.path = path
		self.type = type

		self.curFilePath = ''
		self.curFileFD = None
		self.seperate = ","
		self.ext = ".csv"
		self.splitFlag = True
		self.lsIntervalTime = 5
		self.curLineNum = 0
		if prefix:
			prefix += '_'
		self.prefix = prefix

		try : self.nonBlock = args['NonBlock']
		except : self.nonBlock = False
			
		self.filePat = "20????????????.csv"

		self._TypeCheck()
		if(self._IsFileType()) : self._CSVFileOpen(self.path)

	def _TypeCheck(self) :
		if self.type == Mobigen.DataProcessing.CSV2.PARTITION :
			if(not os.path.isdir(self.path)) :
				raise TypeDefineErrorException 

		if self.type == Mobigen.DataProcessing.CSV2.FILE :
			if(not os.path.isfile(self.path)) :
				raise TypeDefineErrorException 

	def _IsFileType(self) :
		return self.type == Mobigen.DataProcessing.CSV2.FILE

	def _IsParitionType(self) :
		return self.type == Mobigen.DataProcessing.CSV2.PARTITION

	def _CSVFileOpen(self, path) :
		if self.curFileFD : self.curFileFD.close()
		self.curFilePath = path
		
		try:
			self.curFileFD = open(self.curFilePath,'r')
		except Exception, err:
			if self._IsParitionType():
				if self._IsExistNextFile():
					self._SwitchNextFile()
					self.curLineNum = 0
			else:
				raise err

	def _GetFileList(self) :
		flist = glob.glob("%s/%s%s" % (self.path, self.prefix, self.filePat))
		flist.sort()
	#	return flist[:-1]
		return flist

	def _GetLastFilePath(self) :
		return self._GetFileList()[-1]

	def _IsExistNextFile(self) :
		tmpFileNames = self._GetFileList()

		for filepath in tmpFileNames :
			if self.curFilePath < filepath :
				return True
		
		return False	

	def _SwitchNextFile(self) :
		tmpFileNames = self._GetFileList()

		for filepath in tmpFileNames :
			if self.curFilePath < filepath :
			#	__LOG__.Watch((self.curFilePath, filepath))
				self._CSVFileOpen(filepath)
				return	

	def SetSeperate(self, sep) :
		self.seperate = sep

	def SetFilePattern(self, pat) :
		self.filePat = pat

	def SetExt(self, ext) :
		self.ext = ext

	def SetLsIntervalTime(self, lsTime) :
		self.lsIntervalTime = lsTime

	def EnableSplit(self, flag=True) :
		self.splitFlag = flag

	def SetPosition(self, strTime, pos = 0) : 
		if not self._IsParitionType() : raise TypeDefineErrorException 

		tmpFilePath = "%s/%s%s%s" % (self.path, self.prefix, strTime, self.ext) 
		#__LOG__.Watch(tmpFilePath)
		self._CSVFileOpen(tmpFilePath)

		if self.curFileFD:
			self.curLineNum = pos
		else:
			pos = 0

		if(pos) :
			posCnt = 0
			for line in self.curFileFD.xreadlines() :
				posCnt += len(line)
				pos -= 1
				if(pos == 0) : break
			self.curFileFD.seek(posCnt)

			#for line in self.curFileFD.xreadlines() : 
			#	print line
			#	pos = pos - 1
			#	if(pos==0) : break

	def SetLast(self) :
		if not self._IsParitionType() : raise TypeDefineErrorException 

		tmpFilePath = self._GetLastFilePath()
		self._CSVFileOpen(tmpFilePath)
		
		for line in self.curFileFD.xreadlines() :
			self.curLineNum += 1

		st_results = os.stat(self.curFilePath)
		st_size = st_results[6]
		self.curFileFD.seek(st_size)

	def SetOffset(self, strTime, pos = 0) : 
		if not self._IsParitionType() : raise TypeDefineErrorException 

		tmpFilePath = "%s/%s%s%s" % (self.path, self.prefix, strTime, self.ext) 
		#__LOG__.Watch(tmpFilePath)
		self._CSVFileOpen(tmpFilePath)

		if(pos) : self.curFileFD.seek(pos)

	def __iter__(self):
		return self	
		
	def next(self):
		while 1:
			file = self.curFileFD
		#	where = file.tell()
			try:
				line = file.readline()
			except Exception, err:
				if self._IsParitionType() : 
					if self.curFilePath == '':
						if self._IsExistNextFile():
							self.SetLast()
					"""
					else:		# check current file
						if os.path.exists(self.curFilePath):
							self.curFileFD = open(self.curFilePath,'r')
							strTime, lineNum = self.GetCurFileInfo(False)
							self.SetPosition(strTime, lineNum)
					"""
					line = ''
					
			if not line:
				if self._IsFileType() : 
					raise StopIteration
				
		#	#	file.seek(where)
		#	#	__LOG__.Trace("Waitting next file...") 
				if self.nonBlock:
					if(self._IsExistNextFile()) :
						self._SwitchNextFile()
						file = self.curFileFD
						self.curLineNum = 0
						continue
					else:
						return ''
				else:
					if(self._IsExistNextFile()) :
						self._SwitchNextFile()
						file = self.curFileFD
						self.curLineNum = 0
        	
					time.sleep(self.lsIntervalTime)
					continue

			self.curLineNum += 1
			if (self.splitFlag) : return line.strip().split(self.seperate)
			else                : return line.strip()

	def readline(self) :
		data = self.curFileFD.readline()
		return data.strip().split(self.seperate)
		
	def readlines(self) :
		lines = []
		while True : 	
			try : data = self.next()  
			except StopIteration : break

			lines.append(data)

		return lines

	def GetCurFileInfo(self, fullPath = True) :
		if fullPath:
			return self.curFilePath, self.curLineNum
		else:
			return self.curFilePath[-18:-4], self.curLineNum

	def GetOffset(self):
		return self.curFilePath[-18:-4], self.curFileFD.tell()
