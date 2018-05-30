#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, operator, TopRankHeap, os, ConfigParser, re

class SumTable :
	def __init__(self, sumDir, tableName, keyColIdxList, valColIdxList, funcSet, topRankList, isOrder ) :
		self.tableName = tableName
		self.sumDir = sumDir
		self.keyColIdxList = keyColIdxList ## Conf key Column Index list
		self.valColIdxList = valColIdxList ## Conf value Column Index list
		self.funcSet = funcSet
		self.topRankList = topRankList
		self.isOrder = isOrder

		self.sumHash = {} ## for sum()
		self.cntHash = {} ## for count(*)

	def clear(self) :
		del(self.sumHash)
		del(self.cntHash)
		self.sumHash = {}
		self.cntHash = {}

	def put(self, vals) :
		try :  ## skip for known error
			keyStr = ",".join( map( vals.__getitem__, self.keyColIdxList ) )
	
			if "count" in self.funcSet :
				try :
					self.cntHash[keyStr] += 1
				except KeyError :
					self.cntHash[keyStr] = 1
	
			## make sum()
			try :
				self.sumHash[keyStr] = map( operator.add, self.sumHash[keyStr], [ float(vals[i]) for i in self.valColIdxList ]) 
			except KeyError :
				self.sumHash[keyStr] = [ float(vals[i]) for i in  self.valColIdxList ]

		except Exception, err :
		#	print "debug : %s, value = [%s]" % ( str(err), vals )
			pass
		
	def svf(self, filePfx, dataPfx) :
		fileName = "%s/%s_%s" % (self.sumDir, filePfx, self.tableName)
		
		if dataPfx == '' : dataPfx = None 
		return self.saveSummary(fileName, dataPfx)

		######### tesse
		for i in xrange( len(self.topRankList)/2 ) :
			(rankIdx, rankCnt) = (self.topRankList[i*2], int(self.topRankList[i*2+1]) )
			self.saveTopRank( fileName, dataPfx, rankIdx, rankCnt )

	def saveSummary(self, fileName, pfxStr) :
		tmpFileName = "%s.tmp" % fileName
		fh = open( tmpFileName, "w" ) 

		for keyStr in self.sumHash :

			if (self.isOrder == "Y") :	# modify 2012. 07. 26 (sooyeol)
				keyList = map( str, re.split("\s*,\s*", keyStr) )
				valList = self.sumHash[keyStr]
				sumPair = map(None, self.keyColIdxList, keyList)
				sumPair.extend( map(None, self.valColIdxList, valList) )
				sumPair.sort()
				ans = ",".join( map(str, [ pair[1] for pair in sumPair ] ) )
			else :
				valStr = ",".join( map( str, self.sumHash[keyStr] ) )
				ans = "%s,%s" % (keyStr, valStr)

			if pfxStr != None :
				ans = "%s,%s" % (pfxStr, ans)

			if "count" in self.funcSet :
				ans = "%s,%s" % (ans, self.cntHash[keyStr])

			fh.write( "%s\n" % ans)
		fh.close()

		saveFileName = "%s.csv" % fileName
		os.rename(tmpFileName, saveFileName)
		return saveFileName

	def saveTopRank(self, fileName, pfxStr, rankIdx, rankCnt) :
		topRankHeap = TopRankHeap.TopRankHeap( rankCnt )
		topFileName = "%s.top_%s.csv" % (fileName, rankIdx)

		if rankIdx == "count" :
			for keyStr, val in self.cntHash.items() :
				topRankHeap.put(keyStr, val)
		else :
			rankIdx = int(rankIdx)
			for keyStr, valList in self.sumHash.items() :
				topRankHeap.put(keyStr, valList[rankIdx])

		fh = open( "%s.tmp" % topFileName, "w" )

		for ans in topRankHeap.get() :
			if pfxStr != None :
				ans = "%s,%s" % (pfxStr, ans)

			fh.write( "%s" % ans )

		fh.close()
		os.rename( "%s.tmp" % topFileName, topFileName )
			
class SummaryCore :
	def __init__(self, confFileName, section = None) :
		conf = ConfigParser.ConfigParser()
		conf.read( confFileName )

		self.sumTables = []

		self.sectionList = None
		if (section != None) :
			self.sectionList = section.strip().split(",")

	#	sumDir = conf.get("General", "summary dir")

		tableNameList = []
		for cs in conf.sections() :
			if (cs == "General") : continue
			if (cs == "Dict") : continue
			if ( (self.sectionList) and (not cs in self.sectionList) ) : continue
			tableNameList.append(cs)

		for tableName in tableNameList :
			keyColIdxList = map( int, re.split("\s*,\s*", conf.get(tableName, "key column index")) )
			valColIdxList = map( int, re.split("\s*,\s*", conf.get(tableName, "value column index")) )

			sumDir = conf.get(tableName, "summary dir")

			try :
				funcSet = set( re.split("\s*,\s*", conf.get(tableName, "functions") ) )
			except :
				funcSet = set()

			try :
				topRankList = re.split("\s*,\s*", conf.get(tableName, "top rank") )
				if len(topRankList) % 2 != 0 :
					topRankList = []
			except :
				topRankList = []

			try :
				isOrder = conf.get(tableName, "column order")
			except :
				isOrder = "N"

			self.sumTables.append( SumTable(sumDir, tableName, keyColIdxList, valColIdxList, funcSet, topRankList, isOrder) )

	def sfio(self, line) :
		words = line.strip().split(",")
		if len(words) < 1 :
			return None

		cmd = words.pop(0).upper()

		if cmd == "PUT" :
			for sumTable in self.sumTables :
				sumTable.put(words)
			return None

		elif cmd == "SVF" and len(words) == 2 :
			(filePfx, dataPfx) = words
			retList = []
			for sumTable in self.sumTables :
				retList.append( sumTable.svf(filePfx, dataPfx) )

			return "OK ,%s\n" % ",".join(retList)

	def getSumTable(self, section) :
		for sumTable in self.sumTables :
			if (section != sumTable.tableName) : continue
			return sumTable

	def getSumTables(self) :
		return self.sumTables
	
	def run(self, line) :
		while True :
			line = sys.stdin.readline()
			self.sfio(line)

def main() :
	if len(sys.argv) != 2 :
		print "usage : %s confFileName" % (sys.argv[0])
		sys.exit()

	confFileName = sys.argv[1]
	sumCore = SummaryCore( confFileName )
	sumCore.run()

if __name__ == "__main__" : main()
