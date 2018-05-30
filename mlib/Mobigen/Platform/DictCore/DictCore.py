#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-----------------------------------------------------
# version | date : writer : description
#---------+-------------------------------------------
# V1.0    | 110829 : tesse & seory : first edtion
#---------+-------------------------------------------

import os, sys, thread
#import Mobigen.Common.Log as Log; Log.Init()

HLP_STR = '''
=============================================================================================
cmd | description | command format                      | answer format
---------------------------------------------------------------------------------------------
PUT | put data                   | put,tableName,colName,value                   | no answer
APP | append data                | app,tableName,colName,value                   | no answer
MPT | multiple put               | mpt,tableName,colName,value,colName,value ... | no answer
MAP | multiple app               | map,tableName,colName,value,colName,value ... | no answer
GET | get value                  | get,tableName,colName    | "OK ,tableName,colName,value"
POP | get and del value          | pop,tableName,colName    | "OK ,tableName,colName,value"
MGT | multiple get               | mgt,tableName,colName,.. | "OK ,value, ..."
MPP | multiple pop               | mpp,tableName,colName,.. | "OK ,value, ..."
TBL | get tableNames 100         | tbl                      | "OK ,tableName, ..."
COL | get colNames 100           | col,tableName            | "OK ,colName, ..."
LEN | count tableNames           | len                      | "OK ,count"
LEN | count colNames             | len,tableName            | "OK ,count"
DEL | delete tableName           | del,tableName            | no answer
DEL | delete colName             | del,tableName,colName    | no answer
CLR | clear data                 | clr                      | "OK ,all data cleared"
HLP | help                       | hlp                      | this document
BYE | disconnect                 | bye                      | no answer
KIL | shutdown                   | kil                      | no answer
SVF | save to file all by fg     | svf,fileName             | "OK ,end save to .."
SVB | save to file all by bg     | svb,fileName             | "OK ,start bg save to ..."
SVF | save to file table by fg   | svf,fileName,tableName   | "OK ,end save tableName to .."     
SVB | save to file table by bg   | svb,fileName,tableName   | "OK ,start bg save tableName to .." 
LDF | load from file all by fg   | ldf,fileName             | "OK ,end load from ..."
LDB | load from file all by bg   | ldb,fileName             | "OK ,start bg load from ..."
LDF | load from file table by fg | ldf,fileName,tableName   | "OK ,end load tableName from ..."
LDB | load from file table by bg | ldb,fileName,tableName   | "OK ,start bg load tableName from ..."
=============================================================================================
'''

class DictCore :
	def __init__(self, confFile) :
		self.dict = {}
		self.maxRetCnt = 100
		self.confFile = confFile	

	def saveAll(self, fileName) :
		fp = open( fileName, "w" )
		for tableName in self.dict :
			for (colName, value) in self.dict[tableName].items() :
				fp.write( "%s,%s,%s\n" % (tableName, colName, value) )
		fp.close()

	def saveTable(self, fileName, tableName) :
		fp = open( fileName, "w" )
		for (colName, value) in self.dict[tableName].items() :
			fp.write( "%s,%s,%s\n" % (tableName, colName, value) )
		fp.close()

	def loadAll(self, fileName) :
		fp = open( fileName )
		for line in fp :
			line = line.strip()
			words = line.split(",")
			if len(words) == 3 :
				(tableName, colName, value) = words
				if not tableName in self.dict : self.dict[tableName] = {}
				self.dict[tableName][colName] = value
		fp.close()

	def loadTable(self, fileName, tName) :
		fp = open( fileName )
		for line in fp :
			line = line.strip()
			words = line.split(",")
			if len(words) == 3 :
				(tableName, colName, value) = words
				if tName == tableName :
					if not tableName in self.dict : self.dict[tableName] = {}
					self.dict[tableName][colName] = value
		fp.close()

	def sfio(self, line) :
		words = line.strip().split(',')
		if len(words) == 0 :
			return None

		cmd = words.pop(0).upper()

		if cmd == "GET" and len(words) == 2 :
			(tableName, colName) = words
			try :
				ansStr = "OK ,%s\n" % ( self.dict[tableName][colName] )
			except KeyError :
				ansStr = "NOK,no key exists : [%s-%s]\n" % (tableName, colName)
			return ansStr

		elif cmd == "PUT" and len(words) == 3 :
			(tableName, colName, value) = words
			try :
				self.dict[tableName][colName] = value
			except KeyError :
				self.dict[tableName] = {}
				self.dict[tableName][colName] = value
			return None

		elif cmd == "MGT" and len(words) >= 2 :
			tableName = words.pop(0)
			ansList = []

			for colName in words :
				try :
					ansList.append( self.dict[tableName][colName] )
				except KeyError :
					ansList.append( "" )

			ansStr = ",".join(ansList)
			ansStr = "OK ,%s\n" % ansStr
			return ansStr

		elif cmd == "MPT" and len(words) >= 3 :
			tableName = words.pop(0)
			for i in range( len(words)/2 ) :
				colName = words[i*2]
				value = words[i*2 + 1]

				try :
					self.dict[tableName][colName] = value
				except KeyError :
					self.dict[tableName] = {}
					self.dict[tableName][colName] = value
			return None


		elif cmd == "APP" and len(words) == 3 :
			(tableName, colName, value) = words
			try :
				self.dict[tableName][colName] += value
			except KeyError :
				# seory modify
				try : 
					self.dict[tableName][colName] = value
				except :
					self.dict[tableName] = {}
					self.dict[tableName][colName] = value
			except :
				return None
			return None

		elif cmd == "MAP" and len(words) >= 3 :
			tableName = words.pop(0)
			for i in range( len(words)/2 ) :
				colName = words[i*2]
				value = words[i*2 + 1]

				# seory modify
				try :
					self.dict[tableName][colName] += value
				except KeyError :
					try :
						self.dict[tableName][colName] = value
					except KeyError :
						self.dict[tableName] = {}
						self.dict[tableName][colName] = value
			return None

		elif cmd == "POP" and len(words) == 2 :
			(tableName, colName) = words
			try :
				ansStr = "OK ,%s\n" % ( self.dict[tableName].pop(colName) )
			except KeyError :
				ansStr = "NOK,no key exists : [%s-%s]\n" % (tableName, colName)
			return ansStr

		elif cmd == "MPP" and len(words) >= 2 :
			tableName = words.pop(0)
			ansList = []

			for colName in words :
				try :
					ansList.append( self.dict[tableName].pop(colName) )
				except KeyError :
					ansList.append( "" )

			ansStr = ",".join(ansList)
			ansStr = "OK ,%s\n" % ansStr
			return ansStr

		elif cmd == "TBL" :
			cnt = 0
			ansList = []
			for tableName in self.dict.keys() :
				ansList.append(tableName)
				cnt += 1
				if cnt >= self.maxRetCnt : break

			if cnt == 0 :
				ansStr = "NOK,no table exists\n"
			else :
				ansStr = ",".join( ansList )
				ansStr = "OK ,%s\n" % ansStr

			return ansStr

		elif cmd == "COL" and len(words) == 1 :
			tableName = words[0]
			if not tableName in self.dict :
				ansStr = "NOK,no table exists\n"
			else :
				cnt = 0
				ansList = []
				for colName in self.dict[tableName].keys() :
					ansList.append(colName)
					cnt += 1
					if cnt >= self.maxRetCnt : break
	
				if cnt == 0 :
					ansStr = "NOK,no column exists\n"
				else :
					ansStr = ",".join( ansList )
					ansStr = "OK ,%s\n" % ansStr

			return ansStr

		### return count of tables ###
		elif cmd == "LEN" and len(words) == 0 :
			return "OK ,%s\n" % ( len(self.dict) )

		### return count of table's column ###
		elif cmd == "LEN" and len(words) == 1 :
			tableName = words[0]
			try :
				return "OK ,%s\n" % ( len(self.dict[tableName]) )
			except :
				return "NOK,no table\n"

		elif cmd == "DEL" :
			if len(words) == 1 :
				tableName = words[0]
				if tableName in self.dict :
					del self.dict[tableName]

			elif len(words) == 2 :
				(tableName, colName) = words
				if tableName in self.dict and colName in self.dict[tableName] :
					del self.dict[tableName][colName]

			return None

		elif cmd == "CLR" :
			self.dict.clear()
			return "OK ,all data cleared\n"

		elif cmd == "HLP" :
			return HLP_STR

		elif cmd == "KIL" :
			sys.exit()

		### Save Forground and Background ###
		elif (cmd == "SVF" or cmd == "SVB") :
			if len(words) == 1 :
				fileName = words[0]

				if cmd == "SVF" :
					self.saveAll(fileName)
					return "OK ,end save to %s\n" % fileName
				elif cmd == "SVB" :
					thread.start_new_thread( self.saveAll, (fileName,) )
					return "OK ,start bg save to %s\n" % fileName
			elif len(words) == 2 :
				(fileName, tableName) = words

				if cmd == "SVF" :
					self.saveTable(fileName, tableName)
					return "OK ,end save table %s to %s\n" % (tableName, fileName)
				elif cmd == "SVB" :
					thread.start_new_thread( self.saveTable, (fileName, tableName) )
					return "OK ,start bg save table %s to %s\n" % (tableName, fileName)

		### Load Forground and Background ###
		elif (cmd == "LDF" or cmd == "LDB") : 
			if len(words) == 1 :
				fileName = words[0]

				if cmd == "LDF" :
					self.loadAll(fileName)
					return "OK ,end load from %s\n" % fileName
				elif cmd == "LDB" :
					thread.start_new_thread( self.loadAll, (fileName,) )
					return "OK ,start bg load from %s\n" % fileName
			elif len(words) == 2 :
				(fileName, tableName) = words

				if cmd == "LDF" :
					self.loadTable(fileName, tableName)
					return "OK ,end load table %s from %s\n" % (tableName, fileName)
				elif cmd == "LDB" :
					thread.start_new_thread( self.loadTable, (fileName, tableName) )
					return "OK ,start bg load table %s from %s\n" % (tableName, fileName)

		else :
			return None
	
	def run(self) :
		while (True) :
			line = sys.stdin.readline()
	
			if line[:3].upper() == "BYE" :
				ansStr = self.sfio( "KIL" )
			else :
				ansStr = self.sfio( line )
				if ansStr == None :
					pass
				else :
					sys.stdout.write(ansStr)
					sys.stdout.flush()

def main() :
	dict = DictCore("")
	dict.run()

if __name__ == "__main__" : main()
