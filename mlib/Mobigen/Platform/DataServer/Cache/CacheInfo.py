#!/usr/bin/env python
# encoding: utf-8
"""
CacheInfo.py

Copyright (c) 2012 Mobigen. All rights reserved.
"""

import sys
import time
import copy
import os

class CacheInfo:
	
	CacheTimeMap = {}	# Cache파일에 최종으로 접근한 시간을 관리.
	CacheSeekMap = {}	# Cache파일의 파일 포인터 위치 정보를 관리.
	CacheStatMap = {}	# Cache상태 관리.
	
	CacheStart = "caching"
	CacheEnd = "complete"
	
	@staticmethod
	def insertPos(cacheKey, page, pos):
		if (not CacheInfo.CacheSeekMap.has_key(cacheKey)):
			CacheInfo.CacheSeekMap[cacheKey] = {}
			
		if (not CacheInfo.CacheTimeMap.has_key(cacheKey)):
			CacheInfo.updateTime(cacheKey)
			
		CacheInfo.CacheSeekMap[cacheKey][page] = pos
	
	@staticmethod
	def selectPos(cacheKey, page):
		CacheInfo.updateTime(cacheKey)
		return CacheInfo.CacheSeekMap[cacheKey].get(page)
		
	@staticmethod
	def updateTime(cacheKey):
		CacheInfo.CacheTimeMap[cacheKey] = time.strftime("%Y%m%d%H%M%S")
		
	@staticmethod
	def deleteCache(cacheKey):
		if (CacheInfo.CacheTimeMap.has_key(cacheKey)) :
			del(CacheInfo.CacheTimeMap[cacheKey])
			
		if (CacheInfo.CacheSeekMap.has_key(cacheKey)) :
			del(CacheInfo.CacheSeekMap[cacheKey])
			
		if (CacheInfo.CacheStatMap.has_key(cacheKey)) :
			del(CacheInfo.CacheStatMap[cacheKey])
			
	@staticmethod
	def startCache(cacheKey):
		CacheInfo.CacheStatMap[cacheKey] = CacheInfo.CacheStart
		
	@staticmethod
	def completeCache(cacheKey):
		CacheInfo.CacheStatMap[cacheKey] = CacheInfo.CacheEnd
		
	@staticmethod
	def isCache(cacheKey):
		return CacheInfo.CacheStatMap.has_key(cacheKey)
		
	@staticmethod
	def getStatus(cacheKey):
		return CacheInfo.CacheStatMap.get(cacheKey)
	
	@staticmethod
	def getTimeInfo(requestCacheKey=None):
		retList = []
		for cacheKey, _time in CacheInfo.CacheTimeMap.items() :
			if (requestCacheKey and cacheKey != requestCacheKey) : continue
			retList.append("key:%s\ttime:%s" % (cacheKey, _time))
		return retList
		
	@staticmethod
	def getPosInfo(requestCacheKey):
		retList = []
		for cacheKey, seekMap in CacheInfo.CacheSeekMap.items() :
			if (cacheKey != requestCacheKey) : continue
			for seekPage, seekPos in CacheInfo.CacheSeekMap[cacheKey].items() :
				retList.append("page:%-10d\tpos:%d" % (seekPage, seekPos))
		return retList
		
	@staticmethod
	def getStatusInfo(requestCacheKey=None):
		retList = []
		for cacheKey, status in CacheInfo.CacheStatMap.items() :
			if (requestCacheKey and cacheKey != requestCacheKey) : continue
			retList.append("key:%s\tstatus:%s" % (cacheKey, status))
		return retList
	
	@staticmethod	
	def getPosMap():
		retMap = {}
		for cacheKey, seekMap in CacheInfo.CacheSeekMap.items() :
			cacheStatus = CacheInfo.CacheStatMap.get(cacheKey)
			# 현재 Caching중인 파일은 제외.
			if (cacheStatus == None) : continue
			if (cacheStatus == CacheInfo.CacheStart) : continue
			retMap[cacheKey] = seekMap
		return retMap

