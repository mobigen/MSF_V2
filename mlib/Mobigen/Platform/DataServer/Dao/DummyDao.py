# -*- coding: utf-8 -*-

import re
import os
import time
from md5 import md5
from Cache.FileCache import FileCache
from Cache.CacheInfo import CacheInfo
import Mobigen.Common.Log as Log; Log.Init()

class DummyDao :

	def __init__(self, conf):
		
		self.conf = conf
		self.cacheCount = 10000
		self.totalCount = 50000
		
	def connect(self):
		return True
		
	def close(self):
		pass
		
	def _makeKey(self, query):
		query = re.sub("\r\n", "", query)
		query = re.sub("\n", "", query)
		query = re.sub("\t", "", query)
		query = re.sub(" ", "", query)
		query = re.sub("'", "", query)
		query = re.sub("\"", "", query)
		return md5(query.upper()).hexdigest()
		
	def query(self, requestStart, requestCount, query):
		
		cacheKey = self._makeKey(query)
		
		cacheFile = os.path.join(self.conf.get("dataserver", "cache_path"), \
			cacheKey + ".dat")
		
		# 이미 caching된 경우.
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
		else :
			cacheList = []
			
			for idx in range(1, self.totalCount+1) :
				cacheList.append(["%05d" % idx, "AA", "BB", "CC", "DD", "FF", "GG"])
			
			csr = iter(cacheList)
			
			writeCount = 0
			startPos = 0
			currentPage = 1
			
			try: lookupCount = requestStart + requestCount
			except: lookupCount = 0
			
			# column 정보 전송.			
			columnNames = "INDEX,COL1,COL2,COL3,COL4,COL5,COL6\r\n"
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
					line = csr.next()
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
				self.cache = FileCache(csr, \
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

		# caching이 안된 경우 IRIS에서 조회한다.
		if (not CacheInfo.isCache(cacheKey)) :
			
			cacheList = []
			
			for idx in range(1, self.totalCount+1) :
				cacheList.append(["%05d" % idx, "AA", "BB", "CC", "DD", "FF", "GG"])
			
			csr = iter(cacheList)

			options = {}
			options["writeCount"] = 0
			options["startPos"] = 0
			options["currentPage"] = 1
			self.cache = FileCache(csr, \
							cacheFile,	\
							self.cacheCount,	\
							**options
						)
			self.cache.start()
		# caching되어 있는 경우 cache cleaner에 의해 삭제 되는 것을 방지하기 위해
		# cache 정보를 현재시간으로 갱신한다.
		else :
			CacheInfo.updateTime(cacheKey)

		return cacheFile
			
			
