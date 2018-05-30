#!/usr/bin/env python
# encoding: utf-8
"""
CacheCleaner.py

Copyright (c) 2012 Mobigen. All rights reserved.
"""

import sys
import os
import time
import threading
from CacheInfo import CacheInfo
import Mobigen.Common.Log as Log; Log.Init()

class CacheCleaner(threading.Thread):
	
	def __init__(self, conf):
		threading.Thread.__init__(self)
		
		self.conf = conf

		try : self.keepSec = self.conf.getint("dataserver", "cache_keep_time")
		except : self.keepSec = 30*60
		
		self.cachePath = self.conf.get("dataserver", "cache_path")
		
		__LOG__.Trace("Cache keep time : %d" % self.keepSec)
		
	def timeGap(self, curTime, strTime):
		ret = 0
		try :
			tt1	= time.mktime(time.strptime(curTime, "%Y%m%d%H%M%S"))
			tt2 = time.mktime(time.strptime(strTime, "%Y%m%d%H%M%S"))
			ret = tt1 - tt2
		except :
			__LOG__.Exception()
			ret = 0

		return int(ret)
		
	def run(self):
		
		while (True):
			
			curTime = time.strftime("%Y%m%d%H%M%S")
			for cacheKey, updateTime in CacheInfo.CacheTimeMap.items():
				gap = self.timeGap(curTime, updateTime)
				
				__LOG__.Trace("Cache : %s, updateTime : %s, gap : %d" % \
							(cacheKey, updateTime, gap) )
						
				if (gap >= self.keepSec):
					cacheFile = os.path.join(self.cachePath, cacheKey + ".dat")
					if (os.path.exists(cacheFile)):
						try:
							os.remove(cacheFile)
							__LOG__.Trace("Delete cache file : %s" % cacheFile)
						except:
							__LOG__.Exception()
							
					CacheInfo.deleteCache(cacheKey)
					
			time.sleep(60*5)
			
			
def start(conf):
	return CacheCleaner(conf)