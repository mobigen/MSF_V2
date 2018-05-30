#!/usr/bin/env python
# encoding: utf-8
"""
CacheDump.py

Copyright (c) 2012 Mobigen. All rights reserved.
"""

import sys
import os
import glob
import time
import threading
import cPickle as pickle
from CacheInfo import CacheInfo
import Mobigen.Common.Log as Log; Log.Init()


class CacheDump(threading.Thread):
	
	def __init__(self, conf):
		threading.Thread.__init__(self)
		
		self.conf = conf
		
		self.dumpCycle = 60*60
		self.dumpPath = self.conf.get("dataserver", "dump_path")
		
	def run(self):
		
		# 재기동 시 기존 cache정보를 메모리에 load한다.
		try:
			posMapDump = os.path.join(self.dumpPath, "cacheMap.dump")
			
			if (os.path.exists(posMapDump)):
				fd = open(posMapDump, "r")
				posMap = pickle.load(fd)
				fd.close()
			
				curTime = time.strftime("%Y%m%d%H%M%S")
				for cacheKey in posMap.keys():
					CacheInfo.CacheTimeMap[cacheKey] = curTime
					CacheInfo.CacheSeekMap[cacheKey] = posMap[cacheKey]
					CacheInfo.CacheStatMap[cacheKey] = CacheInfo.CacheEnd
				__LOG__.Trace("Cache load success.")
			else :
				__LOG__.Trace("Cache dump file is not found.")
		except Exception, ex:
			__LOG__.Trace("Cache load error. cause(%s)" % str(ex))
		

		while (True):
			try:
				# 주기에 한번씩 Cache정보를 dump한다.
				time.sleep(self.dumpCycle)
				
				posMap = CacheInfo.getPosMap()
				posMapDump = os.path.join(self.dumpPath, "cacheMap.dump.tmp")

				fd = open(posMapDump, "w")
				pickle.dump(posMap, fd)
				fd.close()
				
				os.rename(posMapDump, posMapDump[:-4])
				__LOG__.Trace("Cache dump success.")
			except Exception, ex:
				__LOG__.Trace("Cache dump error. cause(%s)" % str(ex))


def start(conf):
	return CacheDump(conf)

