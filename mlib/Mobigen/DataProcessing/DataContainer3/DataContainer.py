#!/usr/bin/python
# -*- coding: cp949 -*-

VERSION = '2.9'
# 050906 : tesse
# 050908 : tesse
# 050914 : tesse
# V2.1 : 051121 : tesse
#	def getFileNameList(self) :
#		#filePattern = self.makeFileName( '20*' )
#		filePattern = self.makeIdxName( '20*' )
#		tmpFileNames = glob.glob(filePattern)
#		fileNames = []
#		for fileName in tmpFileNames :
#			fileNames.append( fileName[:-4] )
#
#		fileNames.sort()
#		return fileNames
#
#	def makeIdxName(self, fileTime) :
#		return '%s/%s%s' % (self.homeDir, fileTime, '.db.idx')
#
# V2.2 : 051125 : tesse, hoon
# 	def next()
# 	def nextFileTime()
# 	def makeFileNameList()
# 	def existNextFile()
#
# V2.3 : 051126 : tesse
#		try :
#			if args['Mode'] == 'a' :
#				tmpCurFileTime, tmpRecno = getLastFileTimeRecno(self)
#				if tmpCurFileTime != None :
#					self.curFileTime = tmpCurFileTime
#					fileName = self.makeFileName(self.curFileTime)
#					self.curDB = self.createDB(fileName)
#		except :
#			pass
# V2.4 : 060306 : hoon
# V2.5 : 060621 : hoon - FileTimeInterval
# V2.7 : 060725 : tesse
# V2.8 : 060731 : tesse
#		homeDir = re.sub('\/+$', '', homeDir)

#import Mobigen.Common.Log as Log; Log.Init()
import os, re, glob, time, sys, struct
import types
from socket import timeout ### for timeout exception

import DataLog

def error(val) :
	try :
		sys.stderr.write( "--- error : %s\n" % val )
		sys.stderr.flush()
	except : pass

def debug(val) :
	try :
		sys.stderr.write( "*** debug : %s\n" % val )
		sys.stderr.flush()
	except : pass

def log(val) :
	try :
		sys.stderr.write( "+++ log   : %s\n" % val )
		sys.stderr.flush()
	except : pass

class DataContainer :
	def __init__(self, homeDir, **args) :
		# for C Embedding
		if(type(homeDir)==types.DictType) :
			args = homeDir
			homeDir = args['HomeDir']

		homeDir = re.sub('\/+$', '', homeDir)

		if os.path.isdir(homeDir) == False :
			os.makedirs(homeDir)

		self.curDB = None
		self.nextFileBuf = []
		self.args = args
		self.existNextFile = False
		self.debugStat = 0
		self.curFileTime = '00000000000000'
		self.version = 2

		self.homeDir = homeDir
		if os.path.exists(self.homeDir) == False :
			os.mkdir(self.homeDir)

		# one week keep
		try : self.keepHour = args['KeepHour']
		except : self.keepHour = 168

		try : self.intervalTime = args['FileTimeInterval']
		except : self.intervalTime = -1
		self.bFirstPut = True

		try : 
			if(args['NonBlock']) : args['ReadBlockTimeout'] = 1
		except : 
			pass

		try : self.readBlockTimeout = args['ReadBlockTimeout']
		except : self.readBlockTimeout = 0

		try : self.waitDataSec = args['WaitDataSec']
		except : self.waitDataSec = 0.1

		try : self.nextFileCheckSec = args['NextFileCheckSec']
		except : self.nextFileCheckSec = 10
		self.nextFileCheckCnt = 0

		try : self.mode = args['Mode']
		except : self.mode = 'r'

		try : self.version = args['Version']
		except : self.version = 2


#		try :
#			if args['Mode'] == 'a' :
#				tmpCurFileTime, tmpRecno = self.getLastFileTimeRecno()
#				#__LOG__.Watch(tmpCurFileTime)
#
#				if tmpCurFileTime != None :
#					self.curFileTime = tmpCurFileTime
#					fileName = self.makeFileName(self.curFileTime)
#					self.curDB = self.createDB(fileName)
#		except :
#			#__LOG__.Exception()
#			pass

		
		if self.mode == 'a' :
			tmpCurFileTime, tmpRecno = self.getLastFileTimeRecno()
			#__LOG__.Watch(tmpCurFileTime)

			if tmpCurFileTime != None :
				self.curFileTime = tmpCurFileTime
				fileName = self.makeFileName(self.curFileTime)
				self.curDB = self.createDB(fileName)

	def makeFileName(self, fileTime) :
		if self.version == 3:
			return '%s/%s%s' % (self.homeDir, fileTime, '.db3')
		else:
			return '%s/%s%s' % (self.homeDir, fileTime, '.db')
	
	def makeIdxName(self, fileTime) :
		return '%s/%s%s' % (self.homeDir, fileTime, '*.idx')
	
	def makeIdxNameByFileName(self, fileName) :
		return '%s.idx' % (fileName)
	
	def makeFileTimeByFileName(self, fileName) :
		#return fileName[:10] + '0000'
		#return fileName[-17:-7] + '0000'
		rfindPos = fileName.rfind("/")
		return fileName[ rfindPos+1 : rfindPos+11 ] + '0000'

	def makeFileTimeByMsgTime(self, msgTime) :
		return msgTime[:10] + '0000'

	def createDB(self, fileName) :
		#print self.version
		return DataLog.DataLog( fileName, **self.args )

	def rmData(self) :
		s = re.search('^(\d{4})(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)$', self.curFileTime)
		julFmtStr = '%s-%s-%s %s:%s:%s' % (s.group(1), s.group(2), \
			s.group(3), s.group(4), s.group(5), s.group(6) )
		julTime = time.mktime( time.strptime( julFmtStr, '%Y-%m-%d %H:%M:%S') )
		rmFileTime = time.strftime( '%Y%m%d%H0000', time.localtime( \
			julTime - (3600 * self.keepHour ) ) )
		rmFileName = self.makeFileName(rmFileTime)

		filePattern = self.makeFileName( '20*' )
		fileNames = glob.glob(filePattern)
		fileNames.sort()

		for fname in fileNames :
			if fname < rmFileName :
				os.remove(fname)
				idxName = self.makeIdxNameByFileName(fname)
				os.remove(idxName)

	def put(self, msgTime, rawData, optData = '' ) :
		# msgTime = yyyymmddhhmmss
		fileTime = self.makeFileTimeByMsgTime(msgTime)

		### to make new partition ###
		if fileTime > self.curFileTime :

			if self.bFirstPut or self.intervalCheck(fileTime, self.curFileTime):

				self.curFileTime = fileTime
				fileName = self.makeFileName(self.curFileTime)
				if self.curDB :
					self.curDB.close()
				self.curDB = self.createDB(fileName)
				self.rmData()

			else :
				tmpFd = open( "%s/error.log" % self.homeDir, 'a' )
				tmpFd.write( "%s : msgTime=[%s], rawData=[%s], optData=[%s]\n" % ( time.ctime(), msgTime, rawData, optData ) )
				tmpFd.close()
				return self.curDB.getCurPutRecNo()

		self.bFirstPut = False
		return self.curDB.put(rawData, msgTime, optData) # return recno

	def intervalCheck(self, newTime, oldTime) :
		try :
			if( self.intervalTime == -1 or oldTime=="00000000000000" ) :
				return True

			ntime = time.mktime(time.strptime(newTime[:10],'%Y%m%d%H'))
			otime = time.mktime(time.strptime(oldTime[:10],'%Y%m%d%H'))

			interval = (ntime - otime) / 3600
			# debug( 'newTime=%s, oldTime=%s, ntime=%s, otime=%s, intarval=%s, self.intervalTime=%s' % (newTime, oldTime, ntime, otime, intarval, self.intervalTime) )

			if( interval <= self.intervalTime ) : 
				return True
			else :
				return False
		except :
			return False

	def getFileNameList(self) :
		#filePattern = self.makeFileName( '20*' )
		filePattern = self.makeIdxName( '20*' )
		tmpFileNames = glob.glob(filePattern)
		fileNames = []
		for fileName in tmpFileNames :
			fileNames.append( fileName[:-4] )

		fileNames.sort()
		return fileNames

	def getFirstFileTimeRecno(self) :
		fileNames = self.getFileNameList()
		if len(fileNames) == 0 :
			return None, None
		else :
			return self.makeFileTimeByFileName( fileNames[0] ), 0

	def getLastFileTimeRecno(self) :
		fileNames = self.getFileNameList()

		#print fileNames, self.version

		if len(fileNames) == 0 :
			return None, None

		#print fileNames[-1]

		if self.version == 2 and fileNames[-1][-1] == "3":
			self.version = 3
	
		lastFileName = fileNames[-1]
		idxFileName = self.makeIdxNameByFileName(lastFileName)

		#print fileNames, self.version
		lastRecno = DataLog.getLastIdx(idxFileName, self.version)

		return self.makeFileTimeByFileName(lastFileName), lastRecno

	def get(self, fileTime, recno=0) :
		fileTime = self.makeFileTimeByMsgTime(fileTime)

		if fileTime != self.curFileTime :
			self.curFileTime = self.makeFileTimeByMsgTime(fileTime)
			fileName = self.makeFileName(self.curFileTime)
			if self.curDB :
				self.curDB.close()

			# db3 file exists
			if os.path.exists(fileName + "3"):
				self.version = 3
				fileName = self.makeFileName(self.curFileTime)

			self.curDB = self.createDB(fileName)

		try :
			key, value, msgTime, opt = self.curDB.get(recno)
			return self.curFileTime, msgTime, opt, key, value
	
		except Exception, err :
			raise Exception, 'no data to read'

	def getBy(self, fileTime, key, flag='Time') :
		fileTime = self.makeFileTimeByMsgTime(fileTime)

		if fileTime != self.curFileTime :
			self.curFileTime = self.makeFileTimeByMsgTime(fileTime)
			if self.curDB :
				self.curDB.close()
			self.curDB = self.createDB(fileName)

		try :
			if flag == 'Time' :
				key, value, msgTime, opt = self.curDB.getByTime(key)
				return self.curFileTime, msgTime, opt, key, value
			else :
				key, value, msgTime, opt = self.curDB.getByOpt(key)
				return self.curFileTime, msgTime, opt, key, value
	
		except Exception, err :
			raise Exception, 'no data to read'
	
	def getByTime(self, fileTime, msgTime) :
		return self.getBy( fileTime, msgTime, 'Time' )

	def getByOpt(self, fileTime, opt) :
		return self.getBy( fileTime, opt, 'Opt' )

	def getFirst(self) :
		fileTime, recno = self.getFirstFileTimeRecno()
		return self.get(fileTime, recno)

	def getLast(self) :
		fileTime, recno = self.getLastFileTimeRecno()
		return self.get(fileTime, recno)

	def next(self) :

		while True :
			try :
				### 초기 get 없이 바로 next 를 수행하였는데 homeDir 에 
				### 아무 파일도 없을경우 ###
				if self.curDB == None :
					tmpCurFileTime, tmpRecno = self.getLastFileTimeRecno()

					if tmpCurFileTime == None :
						raise timeout

					else :
						self.curFileTime = tmpCurFileTime
						fileName = self.makeFileName(self.curFileTime)
						self.curDB = self.createDB(fileName)

						return self.get(tmpCurFileTime, tmpRecno)

				### normal case ###
				else :
					key, value, msgTime, opt = self.curDB.next()
					return self.curFileTime, msgTime, opt, key, value

			except timeout, err :

				if self.existNextFile == False : ### to check once more

					if self.existNextFileTime() :
						self.existNextFile = True
						continue

					else :
						### In this case, DataLog NonBlock, no sleep
						### DataContainer2 sleep and wait forever,
						### no raise timeout
						if self.readBlockTimeout == 0 :
							time.sleep(self.waitDataSec)
							continue

						### In this case,DataLog block for self.readBlockTimeout
						### DataContainer2 passthrough timeout
						else :
							raise timeout, err.__str__()

				else :
					# switchFile...

					self.curFileTime = self.getNextFileTime()
					fileName = self.makeFileName(self.curFileTime)
	
					if self.curDB :
						self.curDB.close()
					self.curDB = self.createDB(fileName)

					self.existNextFile = False
					continue

	def makeFileNameList(self):
		fileNames = self.getFileNameList()
		curFileName = self.makeFileName(self.curFileTime)
		for fname in fileNames :
			if fname > curFileName :
				self.nextFileBuf.append(fname)

	def getNextFileTime(self) :
		return self.makeFileTimeByFileName( self.nextFileBuf.pop(0) )

	def existNextFileTime(self) :
		if len(self.nextFileBuf) > 0 : 
			return True

		if self.nextFileCheckCnt > self.nextFileCheckSec :
			self.makeFileNameList()
			self.nextFileCheckCnt = 0
		else :
			self.nextFileCheckCnt += self.waitDataSec

		# NonBlock Mode 일때 self.next에서
		# timeoutExcpetion 발생시 다음 DC가 있는지 검사
		if(self.readBlockTimeout) : self.makeFileNameList()

		if len(self.nextFileBuf) > 0 : return True

		return False

	def close(self) :
		try : self.curDB.close()
		except : pass
	
	def __del__(self) :
		self.close()

def main() :

	### test range
	day = 2
	hour = 24
	homeDir = './testdata'
	if os.path.exists(homeDir) == False :
		os.mkdir(homeDir)

	if 1 :
		os.system( 'rm -f %s/*' % homeDir )

	if 1 :
		print '*** insert test'
		stime = time.time()
		db = DataContainer( homeDir, AutoRecover=True, Mode='w', \
			KeepHour=1000, BufSize=100 )
		cnt = 0
		for dd in range(1,day) :
			dd = '%02i' % (dd)
			for hh in range(hour) :
				hh = '%02i' % (hh)
				for mm in range(60) :
					mm = '%02i' % (mm)
					for ss in range(60) :
						ss = '%02i' % (ss)
						msgTime = '200508%s%s%s%s' % (dd,hh,mm,ss)
						opt = 'opt'
						val = 'val'
						db.put(msgTime, val, opt)
						cnt += 1
						# print data
		etime = time.time()
		print '*** time = %s, cnt = %s' % (etime-stime, cnt)
	
	if 1 :
		print '*** get test'
		db = DataContainer( homeDir, AutoRecover=True, Mode='r', KeepHour=1000 )
		cnt = 0
		stime = time.time()
		for dd in range(1,day) :
			dd = '%02i' % (dd)
			for hh in range(hour) :
				hh = '%02i' % (hh)
				tcnt = 0
				for mm in range(60) :
					mm = '%02i' % (mm)
					for ss in range(60) :
						fileTime = '200508%s%s0000' % (dd, hh)
						fileTime, msgTime, opt, key, val \
							= db.get(fileTime, tcnt)
						tcnt += 1
						cnt += 1
		etime = time.time()
		print '*** time = %s, cnt = %s' % (etime-stime, cnt)
	
	if 1 :
		print '*** next test'
		stime = time.time()
		db = DataContainer( homeDir, AutoRecover=True, Mode='r', KeepHour=1000 )
		cnt = 0
		for dd in range(1,day) :
			dd = '%02i' % (dd)
			for hh in range(hour) :
				hh = '%02i' % (hh)
				for mm in range(60) :
					mm = '%02i' % (mm)
					for ss in range(60) :
						fileTime = '200508%s%s0000' % (dd, hh)
						fileTime, msgTime, opt, key, val = db.next()
						cnt += 1
					# print 'key = %s, opt = %s, val = %s' % (key, opt, val)
		etime = time.time()
		print '*** time = %s, cnt = %s' % (etime-stime, cnt)

	if 1 :
		print '*** getByTime test'
		stime = time.time()

		db = DataContainer( homeDir, AutoRecover=True, Mode='r', KeepHour=1000 )
		fileTime = '200508%s%s0000' % (dd, hh)
		fileTime, msgTime, opt, key, val \
			= db.getByTime(fileTime, 20050801235500)
		print fileTime, msgTime, opt, key, val

		for i in range(299) :
			fileTime, msgTime, opt, key, val = db.next()
			print fileTime, msgTime, opt, key, val

		etime = time.time()
		print '*** time = %s, cnt = %s' % (etime-stime, cnt)

	if 1 :
		print '*** get first last file test'
		stime = time.time()
		db = DataContainer( homeDir, AutoRecover=True, Mode='r', KeepHour=1000 )
		print 'first time=', db.getFirstFileTimeRecno()
		print 'last time=', db.getLastFileTimeRecno()
		print 'get first=', db.getFirst()
		print 'get last=', db.getLast()
		etime = time.time()
		print '*** time = %s' % (etime-stime)
if __name__ == '__main__' : main()
