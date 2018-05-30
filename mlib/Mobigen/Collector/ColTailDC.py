#!/usr/bin/python
# -*- coding: cp949 -*-

VERSION = '1.12'

import threading, re, sys, os, time

import Mobigen.Collector.ColTail as ColTail
import Mobigen.DataProcessing.DataContainer3 as DataContainer
import Mobigen.Common.Log as Log; Log.Init()

class ColTailDC( threading.Thread, ColTail.ColTail ) :
	def __init__(self, rmtIp, rmtId, rmtPasswd, rmtHome, rmtFilePat, localDir, **args) :
		threading.Thread.__init__(self)

		self.localDir = localDir
		self.idxFileName = '%s/tail.info' % (self.localDir)
		self.filePat = rmtFilePat
		self.shutdown = False

		try : self.port = args['Port']
		except : self.port = 23

		try : self.timeout = args['Timeout']
		except : self.timeout = 10

		try : self.bufSize = args['BufSize']
		except : self.bufSize = 0

		args['Mode'] = 'a'

		try :
			fileName, lineNum = args['StartFileName'].split(':')
		except :
			try :
				fileName, lineNum = self.loadIdx()
			except :
				fileName, lineNum = "-1", 0

		args['StartLine'] = int(lineNum)

		self.db = DataContainer.DataContainer( self.localDir, **args )

		# parent class : self.curFileName, self.curFileLine
		# self.curFileName = '' # '050906-121/050906-121.db'

		ColTail.ColTail.__init__( self, rmtIp, rmtId, rmtPasswd, \
			rmtHome, rmtFilePat, fileName, **args )

	def dumpIdx(self) :
		fh = open( self.idxFileName + '.tmp', 'w' )
		fh.write( "%s,%s" % (self.curFileName, self.curFileLine) )
		fh.close()
		os.rename( self.idxFileName + '.tmp', self.idxFileName )

	def loadIdx(self) :
		fh = open( self.idxFileName )
		curFileName, lineNum = fh.readline().split(',')
		fh.close()
		lineNum = int( lineNum )

		return curFileName, lineNum

	def run(self) :
		try :
			while 1 :
				if self.shutdown : break

				lineList = self.next()
				for line in lineList :
		
					msgTime, opt, data = self.action(line)
					if msgTime :
						self.db.put(msgTime, data, opt)
		
						if self.bufSize == 0 :
							self.dumpIdx()
						elif self.curFileLine % self.bufSize == 0 :
							self.dumpIdx()
		
						if self.curFileLine % 1000 == 0 :
						 	__LOG__.Trace( 'file=%s, lineNum=%s, msgTime=%s processed' \
								% (self.curFileName, self.curFileLine, msgTime) )

		except ColTail.TimeReachException:
			__LOG__.Watch(self.curFileName)

		except :
			__LOG__.Exception()

		self.dumpIdx()
		self.db.close()
		ColTail.ColTail.close(self)

	def close(self) :
		self.shutdown = True
		self.join()

if __name__ == '__main__' : main()
