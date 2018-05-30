# encoding: utf-8
"""
IRISDao.py

Copyright (c) 2012 Mobigen. All rights reserved.
"""

import sys
import re
import os
import time
import threading
from API import M6
from md5 import md5
from Modules.Exception import *
from Cache.FileCache import FileCache
from Cache.CacheInfo import CacheInfo
import Mobigen.Common.Log as Log; Log.Init()

class IRISDao:
	def __init__(self, conf):
		self.conf = conf
		self.host = self.conf.get("iris", "host")
		self.user = self.conf.get("iris", "user")
		self.passwd = self.conf.get("iris", "password")
		
		self.cacheCount = 10000
		self.cache = None
		
		self.conn = None
		self.csr = None
		
	def __del__(self):
		self._cacheWait()
		self._disconnect()
		
	def close(self):
		# caching이 끝난 후 IRIS를 close한다.
		self._cacheWait()
		self._disconnect()
		
	def _cacheWait(self):
		if (self.cache != None) :
			self.cache.join()
			self.cache = None

	def _disconnect(self):
		if (self.csr != None) :
			try : self.csr.Close()
			except : pass
			self.csr = None
			
		if (self.conn != None) :
			try : self.conn.close()
			except : pass
			self.conn = None
		
	def _connect(self):
		isConnect = True
		if (self.conn == None or self.csr == None):
			try:
				self.conn = M6.Connection(self.host, self.user, self.passwd)
				self.csr = self.conn.cursor()
				__LOG__.Trace("IRIS connect success.")
			except Exception, ex:
				__LOG__.Trace("IRIS connect error. cause(%s)" % str(ex))
				isConnect = False
		return isConnect
		
	def _makeKey(self, query):
		query = re.sub("\r\n", "", query)
		query = re.sub("\n", "", query)
		query = re.sub("\t", "", query)
		query = re.sub(" ", "", query)
		query = re.sub("'", "", query)
		query = re.sub("\"", "", query)
		return md5(query.upper()).hexdigest()
		
	def query(self, requestStart, requestCount, query):
		"""
		클라이언트 요청 쿼리 수행 해서 결과 return
		"""
		cacheKey = self._makeKey(query)
		
		cacheFile = os.path.join(self.conf.get("dataserver", "cache_path"), \
			cacheKey + ".dat")
			
		# 이미 caching된 경우 cache파일에서 데이터를 찾아 전송한다.
		if (CacheInfo.isCache(cacheKey)) :
			if (requestStart % self.cacheCount == 0) :
				page = requestStart / self.cacheCount
			else :
				page = (requestStart / self.cacheCount) + 1
			
			seekPos = CacheInfo.selectPos(cacheKey, page)
			
			if (seekPos == None) :
				raise DataNotFoundException
				
			fd = open(cacheFile, "r")
			columnNames = fd.readline()
			
			# column 정보 전송.
			yield columnNames.strip()
			
			fd.seek(seekPos)
			
			skipCount = self.cacheCount * (page - 1)
			sendCount = 0
			
			# caching된 파일에서 요청 데이터를 찾는다.
			while (True):
			
				try : line = fd.next()
				except StopIteration : break
				
				skipCount += 1
				if (skipCount < requestStart) :
					continue
				
				sendCount += 1
				# requestCount가 None이라면 모든 데이터를 전송.
				if (requestCount != None and \
					sendCount > requestCount):
					break
					
				yield line.strip()
			
			# file close.		
			fd.close()
		# caching된 파일이 없는 경우 IRIS에서 조회한다.
		else :
			if (not self._connect()) :
				raise IRISConnectException
			
			try :
				self.csr.SetFieldSep(",")
				self.csr.SetRecordSep('\r\n')
				self.csr.Execute2(query)
				meta = self.csr.Metadata()
			except Exception, ex :
				__LOG__.Exception()
				raise Exception, str(ex)
			
			writeCount = 0
			startPos = 0
			currentPage = 1
			
			try: lookupCount = requestStart + requestCount
			except: lookupCount = 0
			
			# column 정보 전송.			
			columnNames = ",".join(meta.get("ColumnName")) + "\r\n"
			yield columnNames.strip()
			
			fd = open(cacheFile, "w")
			fd.write(columnNames)
			fd.flush()
			
			startPos += len(columnNames)
			
			# 첫번째 페이지 Caching.
			CacheInfo.insertPos(cacheKey, currentPage, startPos)
			currentPage += 1
			
			isStopIteration = False
			
			while (True):
				try:
					line = self.csr.next()
				except StopIteration:
					isStopIteration = True
					break
				
				line = ",".join(line) + "\r\n"
				fd.write(line)
				fd.flush()

				startPos += len(line)

				writeCount += 1
				if (writeCount % self.cacheCount == 0):
					CacheInfo.insertPos(cacheKey, currentPage, startPos)
					currentPage += 1
					
				if (requestCount != None and \
					writeCount >= lookupCount):
					break

				# requestCount가 None이라면 모든 데이터를 전송.
				if (requestCount == None or \
					writeCount >= requestStart):
					# 요청 데이터 전송.
					yield line.strip()
					
			# file close.		
			fd.close()
			
			# 남아 있는 데이터가 존재 한다면 caching한다.
			if (not isStopIteration):
				options = {}
				options["writeCount"] = writeCount
				options["startPos"] = startPos
				options["currentPage"] = currentPage
				self.cache = FileCache(self.csr, \
								cacheFile,	\
								self.cacheCount,	\
								**options
							)
				self.cache.start()
			else :
				# 모든 데이터를 다 처리 한 경우 cache 완료 플래그를 세팅한다.
				CacheInfo.completeCache(cacheKey)
		
	def download(self, query):
		cacheKey = self._makeKey(query)
		cacheFile = os.path.join(self.conf.get("dataserver", "cache_path"), \
			cacheKey + ".dat")
			
		if (CacheInfo.isCache(cacheKey)) :
			# caching되어 있는 경우 cache cleaner에 의해 삭제 되는 것을 방지하기 위해
			# cache 정보를 현재시간으로 갱신한다.
			CacheInfo.updateTime(cacheKey)
			while (True) :
				status = CacheInfo.getStatus(cacheKey)
				if (status == CacheInfo.CacheEnd) : break
				__LOG__.Trace("File(%s) is still caching." % cacheKey)
				time.sleep(10)
		else :
			# caching이 안된 경우 IRIS에서 조회한다.
			if (not self._connect()) :
				raise IRISConnectException
		
			try :
				self.csr.SetFieldSep(",")
				self.csr.SetRecordSep('\r\n')
				self.csr.Execute2(query)
				meta = self.csr.Metadata()
			except Exception, ex :
				__LOG__.Exception()
				raise Exception, str(ex)
			
			columnNames = ",".join(meta.get("ColumnName")) + "\r\n"
		
			fd = open(cacheFile, "w")
			fd.write(columnNames)
			fd.close()
		
			startPos = len(columnNames)
			currentPage = 1
		
			# 첫번째 페이지 Caching.
			CacheInfo.insertPos(cacheKey, currentPage, startPos)
			currentPage += 1
			
			options = {}
			options["writeCount"] = 0
			options["startPos"] = startPos
			options["currentPage"] = currentPage
			self.cache = FileCache(self.csr, \
							cacheFile,	\
							self.cacheCount,	\
							**options
						)
			self.cache.start()
			self._cacheWait()
			
		return cacheFile

def test():
	import ConfigParser
	
	conf = ConfigParser.ConfigParser()
	conf.read("/Users/mega/Documents/workspace-python/DataServerEx/Config/dataserver.cnf")
	
	dao = IRISDao(conf)
	
	dao.connect()
	
	QUERY = """
		/*+ LOCATION ( PARTITION >= '20121123100900' AND PARTITION <= '20121123101000')*/
		select * from RAW_CDR where end_time >= '20121123100900' and end_time < '20121123101000' and msc = 210 and rnc = '01';
	"""

	for line in dao.query(1, 10, QUERY) :
		print unicode(line, 'utf-8')
	print

	dao.close()
				
if __name__ == '__main__':
	test()
