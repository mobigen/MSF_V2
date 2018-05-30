#!/usr/bin/env python
# encoding: utf-8
"""
MasterHandler.py

Copyright (c) 2012 Mobigen. All rights reserved.
"""

import sys
import os
import time
import cPickle as pickle
from Cache.CacheInfo import CacheInfo
import Mobigen.Common.Log as Log; Log.Init()

HELP_STR = """
-------------------------------------------------------
command | description            | command format
-------------------------------------------------------
HLP     | help                   | hlp
QUT     | disconnect             | qut
SCT     | show cache update time | sct or sct,cachekey
SCI     | show cache info        | sci,cachekey
SCS     | show cache status      | scs or scs,cachekey
DMP     | dump cache             | dmp,filename
LOD     | load cache             | lod,filename
DEL     | delete cache           | del,cachekey
--------------------------------------------------------
"""

class MasterHandler:
	
	def __init__(self, sock, conf, addr) :
		self.sock = sock
		self.conf = conf
		self.address = addr
		
		self.dumpPath = self.conf.get("dataserver", "dump_path")
		self.cachePath = self.conf.get("dataserver", "cache_path")
		
	def start(self):
		
		self.sockfd = self.sock.makefile()
		self.writeLine(HELP_STR)
		self.writeLine(".\r\n")
		
		while (True):
			request = self.sockfd.readline()
			
			if (request == "" or request == None):
				break
				
			if (request == "\n" or request == "\r\n") :
				continue
				
			__LOG__.Trace("%s : request [ %s ]" % (self.address, request))
			
			request = request.strip().split(",")
			
			command = None
			option = None
			
			if (len(request) == 1) : command = request[0]
			else : command, option = request
				
			command = command.upper()
				
			if (command == "HLP"):
				self.help()
			elif (command == "SCT"):
				self.cacheTimeInfo(option)
			elif (command == "SCI"):
				self.cachePosInfo(option)
			elif (command == "SCS"):
				self.cacheStatusInfo(option)
			elif (command == "DMP"):
				self.cacheDump(option)
			elif (command == "LOD"):
				self.cacheLoad(option)
			elif (command == "DEL"):
				self.cacheDelete(option)
			elif (command == "QUT"):
				break
			else :
				self.writeLine("-ERR invalid command")
				self.writeLine(".\r\n")
				
		try:
			self.sockfd.close()
			self.sockfd = None
			self.sock.shutdown(socket.SHUT_RDWR)
			self.sock = None
		except:
			pass
	
	def cacheTimeInfo(self, cacheKey):
		infoList = CacheInfo.getTimeInfo(cacheKey)
		self.writeLine("\r\n+OK CACHE INFO")
		for info in infoList :
			self.writeLine(info)
		self.writeLine(".\r\n")
	
	def cacheStatusInfo(self, cacheKey):
		infoList = CacheInfo.getStatusInfo(cacheKey)
		self.writeLine("\r\n+OK CACHE STATUS")
		for info in infoList :
			self.writeLine(info)
		self.writeLine(".\r\n")
		
	def cachePosInfo(self, cacheKey):
		# Cache파일의 파일 포지션 정보는 반드시 해당하는 key로만 조회 가능.
		if (cacheKey == None):
			self.writeLine("-ERR invalid command")
			self.writeLine(".\r\n")
			return
			
		infoList = CacheInfo.getPosInfo(cacheKey)
		self.writeLine("\r\n+OK CACHE INFO")
		for info in infoList :
			self.writeLine(info)
		self.writeLine(".\r\n")
		
	def cacheDelete(self, cacheKey):
		# Cache정보 삭제는 반드시 하나의 cache만 삭제.
		if (cacheKey == None):
			self.writeLine("-ERR invalid command")
			self.writeLine(".\r\n")
			return
			
		cacheFile = os.path.join(self.cachePath, cacheKey + ".dat")
		if (os.path.exists(cacheFile)):
			try: os.remove(cacheFile)
			except: __LOG__.Exception()

		CacheInfo.deleteCache(cacheKey)
		
		self.writeLine("\r\n+OK CACHE DELETE")
		self.writeLine(".\r\n")
		
	def cacheDump(self, cacheFile):
		try:
			if (cacheFile == None):
				self.writeLine("-ERR invalid command")
				self.writeLine(".\r\n")
				return
				
			posMap = CacheInfo.getPosMap()
			posMapDump = os.path.join(self.dumpPath, cacheFile)
		
			fd = open(posMapDump, "w")
			pickle.dump(posMap, fd)
			fd.close()
			
			self.writeLine("+OK CACHE DUMP")
			self.writeLine(".\r\n")
		except Exception, ex:
			__LOG__.Trace("Oops! cache dump fail. cause(%s)" % str(ex))
			self.writeLine("-ERR CACHE DUMP")
			self.writeLine(str(ex))
			self.writeLine(".\r\n")
		
	def cacheLoad(self, cacheFile):
		try:
			if (cacheFile == None):
				self.writeLine("-ERR invalid command")
				self.writeLine(".\r\n")
				return
				
			posMapDump = os.path.join(self.dumpPath, cacheFile)
			
			fd = open(posMapDump, "r")
			posMap = pickle.load(fd)
			fd.close()
			
			curTime = time.strftime("%Y%m%d%H%M%S")
			for cacheKey in posMap.keys():
				CacheInfo.CacheTimeMap[cacheKey] = curTime
				CacheInfo.CacheSeekMap[cacheKey] = posMap[cacheKey]
				CacheInfo.CacheStatMap[cacheKey] = CacheInfo.CacheEnd
				
			self.writeLine("+OK CACHE LOAD")
			self.writeLine(".\r\n")
		except Exception, ex:
			__LOG__.Trace("Oops! cache load fail. cause(%s)" % str(ex))
			self.writeLine("-ERR CACHE LOAD")
			self.writeLine(str(ex))
			self.writeLine(".\r\n")

	def help(self):
		self.writeLine("\r\n+OK HELP COMMAND")
		self.writeLine(HELP_STR)
		self.writeLine(".\r\n")
				
	def writeLine(self, msg):
		self.sock.sendall(msg + "\r\n")

def main():
	pass


if __name__ == '__main__':
	main()

