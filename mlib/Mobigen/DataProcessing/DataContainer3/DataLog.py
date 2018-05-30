#!/usr/bin/python

VERSION = '2.9'
# V2.2 : 051101 : tesse
#   def binSearch(self, idx, rKey, sRec, eRec) :
#       ...
#       ansIdx = self.getIdx(mRec)
#       mKey = str(ansIdx[idx]).strip()
#
# V2.3 : 051121 : tesse
#	def check(self) :
#		...
#		time.sleep(10)
#		if not os.path.exists(self.idxFileName) :
#			raise Exception, 'no idx file exists'
#
# V2.4 : 051121 : tesse
#		if self.mode != 'r' : self.check()
#
# V2.5 : 051124 : tesse
#	def next(self) :
#		#dataInfo = str(self.fdData.read(OVH_SIZE))
#		#dataInfo = self.fdData.read(OVH_SIZE)
#		dataInfo = readFile( self.fdData, OVH_SIZE )
#		dataInfoLen = len(dataInfo)
#
# V2.6 : 051125 : tesse
#	def next(self) :
#		dataFileLen = os.path.getsize(self.dataFileName)
#
# V2.7 : 060724 : tesse
#	many bug fixed
#	idx data structure changed
#
# V2.71 : 061113 : tesse
### Very Important !!! : In case of HP-UX, it should be written like this when open( fileName, 'r+') ###
### when write after read
#	self.fdIdx.seek(self.fdIdx.tell())
#	self.fdData.seek(self.fdData.tell())
########################################################################################################
#	dataRecNo, data, msgTime, opt = (-1, '', '0000000000', '') ### 061113 : tesse ###
########################################################################################################

# V2.8 : 101118 : tesse
# reduce getsize systemcall
# three times faster to read ***

# V2.9 : 101126 : eek
#  dataLog3 merge

#import Mobigen.Common.Log as Log; Log.Init()
import struct, os, time, sys, os.path, types, fcntl
from socket import timeout ### for NonBlockTimeout

OVH_SIZE = 32
OVH_SIZE_2 = 32
OVH_SIZE_3 = 40

class FileNotFoundException(Exception) : pass

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

def dataPack(recNo, valLen, msgTime, opt, version=2) :
	if version == 3:
		return struct.pack('!QQQ16s', recNo, valLen, int(msgTime), '%16s'%opt )
	else:
		return struct.pack('!IIQ16s', recNo, valLen, int(msgTime), '%16s'%opt )

def dataUnpack(dataInfo, version=2) :
	if version == 3:
		dataRecNo, dataLen, msgTime, opt = struct.unpack('!QQQ16s', dataInfo)
	else:
		dataRecNo, dataLen, msgTime, opt = struct.unpack('!IIQ16s', dataInfo)
	return dataRecNo, dataLen, msgTime, opt

def idxPack(recNo, dataOffset, msgTime, opt, version=2) :
	if version == 3:
		return struct.pack('!QQQ16s', recNo, dataOffset, int(msgTime), '%16s'%opt )
	else:
		return struct.pack('!IIQ16s', recNo, dataOffset, int(msgTime), '%16s'%opt )

def idxUnpack(idxInfo, version=2) :
	if version == 3:
		dataRecNo, dataOffset, msgTime, opt = struct.unpack('!QQQ16s', idxInfo)
	else:
		dataRecNo, dataOffset, msgTime, opt = struct.unpack('!IIQ16s', idxInfo)
	return dataRecNo, dataOffset, msgTime, opt

def getLastIdx(idxFileName, version=2) :
	global OVH_SIZE, OVH_SIZE_3
	idxFileLen = os.path.getsize(idxFileName)

	if version == 3 :
		OVH_SIZE = OVH_SIZE_3

	return idxFileLen/OVH_SIZE - 1

def checkDB(dataFileName) :
	fdData = open( dataFileName )
	fdIdx = open( dataFileName + '.idx' )

	dataOffset = 0
	serialNum = 0
	global OVH_SIZE
	while True :
		ovh = fdData.read(OVH_SIZE)
		if len(ovh) == 0 : break

		if len(ovh) != OVH_SIZE :
			raise Exception, \
				'serial=%s, data file correpted, (overhead=%s) != %s' \
				% (serialNum, len(ovh), OVH_SIZE )

		recnoInDataFile, dataLenInDataFile, msgTime, opt = dataUnpack(ovh)
		print recnoInDataFile, dataLenInDataFile, msgTime, opt

		if recnoInDataFile != serialNum :
			raise Exception, \
				'serial=%s, data file correpted, (serialNum=%s) != (recnoInDataFile=%s)' \
				% (serialNum, serialNum, recnoInDataFile)

		if dataLenInDataFile > 1000000000 or dataLenInDataFile < 0 :
			fdData.close()
			fdIdx.close()
			raise Exception, \
				'serial=%s, data file correpted, dataLenInDataFile=%s' \
				% (serialNum, dataLenInDataFile)

		data = fdData.read(dataLenInDataFile)
		if len(data) != dataLenInDataFile :
			fdData.close()
			fdIdx.close()
			raise Exception, \
				'serial=%s, data file correpted, realReadDataLen=%s, dataLenInDataFile=%s' \
				% (serialNum, len(data), dataLenInDataFile)

		ovh = fdIdx.read(OVH_SIZE)
		if len(ovh) != OVH_SIZE :
			raise Exception, \
				'serial=%s, idx file correpted, (overhead=%s) != 8' \
				% (serialNum, len(ovh))

		recnoInIdxFile, dataOffsetInIdxFile, msgTime, opt = idxUnpack(ovh)
		if recnoInIdxFile != serialNum :
			raise Exception, \
				'serial=%s, idx file correpted, (serialNum=%s) != (recnoInIdxFile=%s)' \
				% (serialNum, serialNum, recnoInIdxFile)

		if dataOffset != dataOffsetInIdxFile :
			raise Exception, \
				'serial=%s, idx,data file mismatch, (dataOffsetInIdxFile=%s) != (dataOffset=%s)' \
				% (serialNum, dataOffsetInIdxFile, dataOffset)

		serialNum += 1
		dataOffset += OVH_SIZE + dataLenInDataFile

		if serialNum % 1000 == 0 :
			print '%s processed' % (serialNum)
	
	if len(fdIdx.read(1)) > 0 :
		raise Exception, \
			'idx file correpted, (serialNum=%s) != (serialNumByIdxFileLen=%s)' \
			% (serialNum-1, os.path.getsize(dataFileName+'.idx')/8 )
	fdData.close()
	fdIdx.close()

	print '* check OK, serial=%s' % (serialNum)

def recoverIdx(idxFileName, version=2) :
	idxFileNameTmp = idxFileName + '.tmp'
	dataFileName = idxFileName[:-4]

	fdData = open( dataFileName )
	fdIdxTmp = open( idxFileNameTmp, 'w' )

	dataOffset = 0
	serialNum = 0
	buf = []

	global OVH_SIZE
	while True :
		try :
			ovh = fdData.read(OVH_SIZE)
			if len(ovh) != OVH_SIZE : break
	
			dataRecNo, dataLenInDataFile, msgTime, opt = dataUnpack(ovh, version)
	
			if serialNum != dataRecNo :
				fdData.close()
				fdIdxTmp.close()
				raise Exception, \
					'data file correpted, recnoInDataFile=%s, serialNum=%s' \
					% (dataRecNo, serialNum)
	
			### check recno and data length in data file
			if dataLenInDataFile > 1000000000 or dataLenInDataFile < 0 :
				fdData.close()
				fdIdxTmp.close()
				raise Exception, \
					'data file correpted, recnoInDataFile=%s, dataLenInDataFile=%s' \
					% (dataRecNo, dataLenInDataFile)
	
			idxInfo = idxPack( dataRecNo, dataOffset, msgTime, opt, version )
	
			buf.append(idxInfo) ### fdIdxTmp.write(idxInfo)
	
			dataOffset += OVH_SIZE + dataLenInDataFile
			serialNum += 1
	
			if serialNum % 1000 == 0 :
				mergeBuf = ''.join( buf )
				fdIdxTmp.write(mergeBuf)
				fdIdxTmp.flush()
				log( '%s processed' % (serialNum) )
				buf = []
		
			fdData.seek(dataLenInDataFile, 1)
			# data = fdData.read(dataLenInDataFile)

		except Exception, err :
			error( err.__str__() )
			break

	if len(buf) != 0 :
		mergeBuf = ''.join( buf )
		fdIdxTmp.write(mergeBuf)
		fdIdxTmp.flush()
		log( '%s processed' % (serialNum) )
		
	fdData.close()
	fdIdxTmp.close()
	os.rename(idxFileName + '.tmp', idxFileName)

	print '* recover OK, serial=%s' % (serialNum)

def recoverData(dataFileName, version=2) :
	dataFileNameTmp = dataFileName + '.tmp'

	fdData = open( dataFileName, 'r' )
	fdDataTmp = open( dataFileNameTmp, 'w' )

	dataOffset = 0
	serialNum = 0
	buf = []
	
	global OVH_SIZE
	while True :
		ovh = fdData.read(OVH_SIZE)
		if len(ovh) != OVH_SIZE : break

		dataRecNo, dataLenInDataFile, msgTime, opt = dataUnpack(ovh, version)

		if serialNum != dataRecNo :
			fdData.close()
			fdDataTmp.close()
			raise Exception, \
				'data file correpted, recnoInDataFile=%s, serialNum=%s' \
				% (dataRecNo, serialNum)

		### check recno and data length in data file
		if dataRecNo > 1000000000 or dataLenInDataFile > 1000000000 \
			or dataRecNo < 0 or dataLenInDataFile < 0 :

			fdData.close()
			fdIdxTmp.close()
			raise Exception, \
				'data file correpted, recnoInDataFile=%s, dataLenInDataFile=%s' \
				% (dataRecNo, dataLenInDataFile)

		if dataLenInDataFile > 1000000000 or dataLenInDataFile < 0 :
			fdData.close()
			fdDataTmp.close()
			print 'data file correpted, dataLenInDataFile=%s' % (dataLenInDataFile)
			break

		data = fdData.read(dataLenInDataFile)

		if len(data) != dataLenInDataFile :
			fdData.close()
			fdDataTmp.close()
			print 'data file correpted, len(data)=%s, dataLenInDataFile=%s' \
				% (len(data), dataLenInDataFile)
			break

		dataInfo = dataPack( serialNum, dataLenInDataFile, msgTime, opt, version )
		fdDataTmp.write(dataInfo+data)
		serialNum += 1

		if serialNum % 1000 == 0 :
			print '%s processed' % (serialNum)
	
	fdData.close()
	fdDataTmp.close()

	os.rename(dataFileName, dataFileName + '.org')
	os.rename(dataFileName + '.tmp', dataFileName)

	print '* recover OK, serial=%s' % (serialNum)

class DataLog :

	def __init__(self, fileName, **args) :

		try : self.mode = args['Mode']
		except : self.mode = 'r'

		try : self.bufSize = args['BufSize']
		except : self.bufSize = 0

		try : self.autoRecover = args['AutoRecover']
		except : self.autoRecover = True

		try : self.waitDataSec = args['WateDataSec']
		except : self.waitDataSec = 0.1

		try : self.readBlockTimeout = args['ReadBlockTimeout']
		except : self.readBlockTimeout = 0

		try : self.version = args['Version']
		except : self.version = 2

		self.idxFileName = fileName + '.idx'
		self.dataFileName = fileName

		self.recNo = 0
		self.bufIdx = []
		self.bufData = []
		self.curDataInfo = None # for def next()
		self.dataOffset = 0
		self.dataFileLen = 0

		if self.version == 3 :
			global OVH_SIZE, OVH_SIZE_3
			OVH_SIZE = OVH_SIZE_3

		if self.mode == 'w' :
			self.fdData = open( self.dataFileName, 'w' )
			self.fdIdx = open( self.idxFileName, 'w' )

			fcntl.flock( self.fdData.fileno(), fcntl.LOCK_EX )
			fcntl.flock( self.fdIdx.fileno(), fcntl.LOCK_EX )

		elif self.mode == 'a' :
			if os.path.exists(self.dataFileName) and  os.path.exists(self.idxFileName) :

				self.fdData = open( self.dataFileName, 'r+' )
				self.fdIdx = open( self.idxFileName, 'r+' )

				self.recoverWriter()

			elif os.path.exists(self.dataFileName) and not os.path.exists(self.idxFileName) :

				self.fdData = open( self.dataFileName, 'r+' )
				self.fdIdx = open( self.idxFileName, 'w' )

				self.recoverWriter()

			elif ( not os.path.exists(self.dataFileName) and  os.path.exists(self.idxFileName) ) or \
			     ( not os.path.exists(self.dataFileName) and not os.path.exists(self.idxFileName) ) :

				self.fdData = open( self.dataFileName, 'w' )
				self.fdIdx = open( self.idxFileName, 'w' )

			else :
				raise Exception, 'bad open'

			fcntl.flock( self.fdData.fileno(), fcntl.LOCK_EX )
			fcntl.flock( self.fdIdx.fileno(), fcntl.LOCK_EX )

			# print 'debug : self.recNo = %s' % self.recNo

		else :
			while 1 :
				if os.path.exists(self.dataFileName) and os.path.exists(self.idxFileName) :

					self.fdData = open( self.dataFileName, self.mode )
					self.fdIdx = open( self.idxFileName, self.mode )
					self.dataFileLen = os.path.getsize(self.dataFileName)
					break

				else :
					log('%s, %s file not exist, so sleep 60 loop' % (self.dataFileName, self.idxFileName) )
					time.sleep(60)
			
	def recoverWriter(self) :

		### 1. 데이터를 불완전하게 쓰고 인덱스를 쓰지 못한경우 
		### 2. 데이터를 완전하게   쓰고 인덱스를 쓰지 못한경우
		### 3. 데이터를 완전하게   쓰고 인덱스를 불완전하게 쓴경우
	
		lastIdx = getLastIdx(self.idxFileName, self.version)
		# debug('get last idx : lastIdx=%s' % (lastIdx) )

		### move data, idx file pointer to current ###
		if lastIdx == -1 :
			dataRecNo, data, msgTime, opt = (-1, '', '0000000000', '') ### 061113 : tesse ###
		else :
			dataRecNo, data, msgTime, opt = self.get(lastIdx)

		# debug('get last rec : dataRecNo, data, msgTime, opt = %s, %s, %s, %s' % (dataRecNo, data, msgTime, opt))

		self.recNo = dataRecNo + 1
		self.dataOffset = self.fdData.tell()

		buf = []

		while True :

			curDataOffset = self.fdData.tell()
			oldDataOffset = curDataOffset
			# debug( 'curDataOffset = %s' % curDataOffset )
			# time.sleep(1)
	
			dataFileLen = os.path.getsize(self.dataFileName)
	
			### 색인의 마지막 레코드다음 레코드를 데이터파일에서 읽기를 시도 ###
			if curDataOffset + OVH_SIZE <= dataFileLen :
				self.curDataInfo = self.fdData.read( OVH_SIZE )
				# log( 'index file(%s) crashed, so recovering ... ' % self.idxFileName )
	
			else :
				### 색인의 마지막 레코드다음 레코드가 존재하지 않으므로 색인 정상 ###
				log( 'index file(%s) status ok' % self.idxFileName )
				break

			### data header unpack ###
			(dataRecNo, dataLen, msgTime, opt) = dataUnpack(self.curDataInfo, self.version)

			curDataOffset = self.fdData.tell()
			dataFileLen = os.path.getsize(self.dataFileName)

			if curDataOffset + dataLen <= dataFileLen :
				self.fdData.seek(dataLen, 1)

				idxInfo = idxPack( dataRecNo, oldDataOffset, msgTime, opt, self.version )
				buf.append(idxInfo) ### fdIdxTmp.write(idxInfo)
				self.recNo = dataRecNo + 1
				self.dataOffset = self.fdData.tell()

				if dataRecNo % 1000 == 0 :
					mergeBuf = ''.join( buf )
					self.fdIdx.write(mergeBuf)
					self.fdIdx.flush()
					log( 'recno %s recover processed' % (dataRecNo) )
					buf = []

			else :
				self.fdData.seek(oldDataOffset)
				break
		
		if len(buf) != 0 :
			mergeBuf = ''.join( buf )
			self.fdIdx.write(mergeBuf)
			self.fdIdx.flush()
			log( 'recno %s recover processed' % (dataRecNo) )
			
		### 061113 : tesse ###
		### Very Important !!! : In case of HP-UX, it should be written like this when open( fileName, 'r+') ###
		### when write after read
		self.fdIdx.seek(self.fdIdx.tell())
		self.fdData.seek(self.fdData.tell())
		########################################################################################################

		log( 'index file (%s) check ok, last recno=%s' % (self.idxFileName, dataRecNo) )
		
	def getCurPutRecNo(self) :
		return self.recNo - 1

	def put(self, val, msgTime='00000000000000', opt='') :
		val = str(val)
		valLen = len(val)

		idxInfo = idxPack(self.recNo, self.dataOffset, msgTime, opt, self.version)

		dataInfo = dataPack(self.recNo, valLen, msgTime, opt, self.version)
		data = dataInfo + val
		
		#debug('put data info : self.recNo, valLen, msgTime, opt = %s, %s, %s, %s' % (self.recNo, valLen, msgTime, opt) )
		#debug('put idx  info : self.recNo, dataOffset, msgTime, opt = %s, %s, %s, %s' % (self.recNo, self.dataOffset, msgTime, opt) )
		#time.sleep(1)

		if self.bufSize == 0 :
			
			### update 060724 ###
			self.fdData.write( data )
			self.fdData.flush()

			self.fdIdx.write(idxInfo)
			self.fdIdx.flush()

		else :
			self.bufData.append(data)
			self.bufIdx.append(idxInfo)

			if self.bufSize == len(self.bufIdx) :
				joinData = ''.join(self.bufData)
				joinIdx = ''.join(self.bufIdx)

				### update 060724 ###
				self.fdData.write( joinData )
				self.fdData.flush()

				self.fdIdx.write( joinIdx )
				self.fdIdx.flush()

				self.bufData = []
				self.bufIdx = []

		self.recNo += 1
		self.dataOffset += OVH_SIZE + valLen

		return self.recNo - 1

	def binSearch(self, idx, rKey, sRec, eRec) :
		# idx : 2=msgTime, 3=opt
		# rKey : request key, ex='yyyymmddhhmmss', ex='opt'
		# sRec : start recno, 0~xxx
		# eRec : end recno, 0~xxx

		if abs(sRec - eRec) < 2 :

			ansIdx = self.getIdx(sRec)
			sKey = str(ansIdx[idx]).strip()

			if sKey == rKey :
				return sRec
			else :
				return eRec

		mRec = (sRec+eRec) / 2
		ansIdx = self.getIdx(mRec)
		mKey = str(ansIdx[idx]).strip()

		if mKey == rKey :
			return mRec

		elif mKey > rKey :
			return self.binSearch( idx, rKey, sRec, mRec )

		else :
			return self.binSearch( idx, rKey, mRec, eRec )

	def set(self, key) :
		idxRecNo, dataOffset, msgTime, opt = self.getIdx(key)

		### update 060724 ###
		dataFileLen = os.path.getsize(self.dataFileName)
		if dataOffset <= dataFileLen : 
			self.fdData.seek(dataOffset)

		else :
			raise Exception, \
				'data file out of range: dataOffset(%s) <= dataFileLen(%s)' \
				% (dataOffset, dataFileLen)

		return idxRecNo, dataOffset, msgTime, opt

	def get(self, key) :
		self.set(key)
		return self.next()

	def getByTime(self, reqTime) :
		eRec = getLastIdx(self.idxFileName)
		aRec = self.binSearch( 2, reqTime, 0, eRec )
		return self.get(aRec)

	def getByOpt(self, reqTime) :
		eRec = getLastIdx(self.idxFileName)
		aRec = self.binSearch( 3, reqTime, 0, eRec )
		return self.get(aRec)

	def getIdx(self, key) :
		idxOffset = key * OVH_SIZE

		### update 060724 ###
		idxFileLen = os.path.getsize(self.idxFileName)
		if idxOffset <= idxFileLen : pass
		else :
			raise Exception, \
				'idx out of range: idxOffset(%s) <= idxFileLen(%s)' \
				% (idxOffset, idxFileLen)

		self.fdIdx.seek(idxOffset)
		(idxRecNo, dataOffset, msgTime, opt) = self.nextIdx()

		if idxRecNo != key :
			### 일부러 timeout 처리를 하지 않았음 ###
			raise Exception, \
				'key idxRecNo mismatch: key = %s, idxRecNo = %s' \
				% (key, idxRecNo)

		return idxRecNo, dataOffset, msgTime, opt

	def nextIdx(self) :

		### update 060724 ###
		curIdxPos = self.fdIdx.tell()
		idxFileLen = os.path.getsize(self.idxFileName)

		if curIdxPos + OVH_SIZE <= idxFileLen :
			idxInfo = self.fdIdx.read(OVH_SIZE)
		else :
			### 일부러 timeout 처리를 하지 않았음 ###
			raise Exception, \
				'idx out of range: curIdxPos(%s) + OVH_SIZE(%s) <= idxFileLen(%s)' \
				% (curIdxPos, OVH_SIZE, idxFileLen)

		(idxRecNo, dataOffset, msgTime, opt) = idxUnpack(idxInfo, self.version)

		return idxRecNo, dataOffset, msgTime, opt

	def next(self) :

		waitDataCnt = 0

		if self.curDataInfo == None : # this is first attempt to read header
			curDataOffset = self.fdData.tell()

			while 1 :
				if curDataOffset + OVH_SIZE <= self.dataFileLen :
					self.curDataInfo = self.fdData.read( OVH_SIZE )
					break

				else :
					self.dataFileLen = os.path.getsize(self.dataFileName)
					if curDataOffset + OVH_SIZE <= self.dataFileLen :
						self.curDataInfo = self.fdData.read( OVH_SIZE )
						break

					if self.readBlockTimeout == 0 :
						raise timeout, 'no header to read'
						# time.sleep( self.waitDataSec )

					elif waitDataCnt > self.readBlockTimeout :
						raise timeout, 'no header to read'

					else :
						waitDataCnt += self.waitDataSec
						time.sleep( self.waitDataSec )

		(dataRecNo, dataLen, msgTime, opt) = dataUnpack(self.curDataInfo, self.version)
		curDataOffset = self.fdData.tell()

		while 1 :
			if curDataOffset + dataLen <= self.dataFileLen :
				data = self.fdData.read( dataLen )
				break

			else :
				self.dataFileLen = os.path.getsize(self.dataFileName)
				if curDataOffset + dataLen <= self.dataFileLen :
					data = self.fdData.read( dataLen )
					break

				if self.readBlockTimeout == 0 :
					#time.sleep( self.waitDataSec )
					raise timeout, 'no data body to read'

				elif waitDataCnt > self.readBlockTimeout :
					raise timeout, 'no data body to read'

				else :
					waitDataCnt += self.waitDataSec
					time.sleep( self.waitDataSec )

		self.curDataInfo = None
		return dataRecNo, data, msgTime, opt

	def close(self) :
		if (self.mode == 'a' or self.mode == 'w') and self.bufSize != 0 and len(self.bufIdx) > 0 :
			joinData = ''.join(self.bufData)
			joinIdx = ''.join(self.bufIdx)
	
			self.fdData.write( joinData )
			self.fdData.flush()

			self.fdIdx.write( joinIdx )
			self.fdIdx.flush()
	
			self.bufData = []
			self.bufIdx = []

		self.fdData.close()
		self.fdIdx.close()

	def __del__(self) :
		try : self.close()
		except Exception, err : pass

def main() :
	dbFileName = 'testDataLog.db'
	loopCnt = 100000

	if 1 :
		try :
			os.unlink(dbFileName)
			os.unlink(dbFileName + '.idx')
		except :
			pass

	wdl = DataLog( dbFileName, Mode='a', BufSize=10, AutoRecover=True )
	rdl = DataLog( dbFileName, BufSize=1000)

	if 1 :
		print "*** write start"
		stime = time.time()
		for i in range(0,loopCnt) :
			wdl.put(i,i,str(i))
		etime = time.time()
		print "* write time = %s" % (etime-stime)
		
	if 1 :
		print "*** next test"
		stime = time.time()
		for i in range(0,loopCnt) :
			try :
				key, val, msgTime, opt = rdl.next()
			except Exception, err :
			#	__LOG__.Exception()
				time.sleep(0.1)

		etime = time.time()
		print "* next time = %s" % (etime-stime)
	
	if 1 :
		print "*** read start"
		stime = time.time()
		for i in range(0,loopCnt) :
			key, val, msgTime, opt = rdl.get(i)
			#print val
		etime = time.time()
		print "* read time = %s" % (etime-stime)
	
	if 1 :
		print "*** getIdx start"
		stime = time.time()

		key, offset, msgTime, opt = rdl.getIdx(0)
		for i in range(0,loopCnt-1) :
			key, offset, msgTime, opt = rdl.nextIdx()
		etime = time.time()
		print "* read time = %s" % (etime-stime)
	
	if 1 :
		print "*** getByTime start"
		stime = time.time()

		key, offset, msgTime, opt = rdl.getByTime(99990)
		for i in range(0,9) :
			key, offset, msgTime, opt = rdl.nextIdx()
			print key, offset, msgTime, opt
		etime = time.time()
		print "* read time = %s" % (etime-stime)
	
	if 1 :
		print "*** getByOpt start"
		stime = time.time()

		key, offset, msgTime, opt = rdl.getByOpt('99990')
		for i in range(0,9) :
			key, offset, msgTime, opt = rdl.nextIdx()
			print key, offset, msgTime, opt
		etime = time.time()
		print "* read time = %s" % (etime-stime)
	
	if 0 :
		print "*** read rand test"
		while True :
			key = sys.stdin.readline()
			key = int(key[:-1])
			try :
				key, val, msgTime, opt = rdl.get(key)
			except Exception, err:
			#	__LOG__.Exception()
				pass
			print "key = %s, val = %s" % (key, val)

if __name__ == '__main__' : main()
