#!/usr/bin/env python
# encoding: utf-8
"""
FileCache.py

Copyright (c) 2012 Mobigen. All rights reserved.
"""

import os
import threading
from CacheInfo import CacheInfo
import Mobigen.Common.Log as Log; Log.Init()

class FileCache(threading.Thread):
	
	def __init__(self, iterator, cacheFile, cacheCount, **args):
		threading.Thread.__init__(self)
		
		self.iterator = iterator
		self.cacheFile = cacheFile
		self.cacheCount = cacheCount
		
		try: self.writeCount = args["writeCount"]
		except: self.writeCount = 0
		
		try: self.startPos = args["startPos"]
		except: self.startPos = 0
		
		try: self.currentPage = args["currentPage"]
		except: self.currentPage = 1
		
		self.cacheKey = os.path.splitext(os.path.basename(self.cacheFile))[0]
		
	def run(self):
		
		CacheInfo.startCache(self.cacheKey)
		
		fd = open(self.cacheFile, "a")
		__LOG__.Trace("File caching start (%s)." % fd.name)
		
		# 남은 데이터 Caching.
		while (True):
			try: data = self.iterator.next()
			except StopIteration: break
			
			data = ",".join(data) + "\r\n"
			fd.write(data)
			fd.flush()
			
			self.startPos += len(data)
			
			self.writeCount += 1
			if (self.writeCount % self.cacheCount == 0):
				CacheInfo.insertPos(self.cacheKey, self.currentPage, self.startPos)
				self.currentPage += 1

		__LOG__.Trace("File caching end   (%s)." % fd.name)
		fd.close()
		
		CacheInfo.completeCache(self.cacheKey)