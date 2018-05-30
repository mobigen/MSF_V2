#!/usr/bin/python

VERSION = 1.2
# 050905 : tesse
# 060223 : sunghoon

import time, signal, re, os, threading
import Mobigen.Collector.ColFtp as ColFtp
import Mobigen.DataProcessing.DataContainer3 as DataContainer
import Mobigen.Common.Log as Log; Log.Init()

class ColFtpDC( ColFtp.ColFtp ) :
	def __init__(self, ip, id, passwd, rmtDir, tmpDir, localDir, **args) :
		self.localDir = localDir

		try : self.lsPat = args['LsPat']
		except : self.lsPat = '*'

		try : self.port = args['Port']
		except : self.port = 21

		try : self.sleep = int( args['Sleep'] )
		except : self.sleep = 10

		try : self.debugMode = args['DebugMode']
		except : self.debugMode = False

		try : self.filetimeinterval = args['FileTimeInterval']
		except : self.filetimeinterval = -1

		# self.ftp = ColFtp.ColFtp(ip, id, passwd, rmtDir, tmpDir, \
		# 	LsPat=self.lsPat, Port=self.port, DebugMode=self.debugMode )

		ColFtp.ColFtp.__init__(self, ip, id, passwd, rmtDir, tmpDir, **args )
		#ColFtp.ColFtp.__init__(self, ip, id, passwd, rmtDir, tmpDir, \
		#	LsPat=self.lsPat, Port=self.port, Sleep=self.sleep, DebugMode=self.debugMode, **args )

		try : self.bufSize = int( args['BufSize'] )
		except : self.bufSize = 0

		try : self.keepHour = args['KeepHour']
		except : self.keepHour = 24

		try : self.version = args['Version']
		except : self.version = 2

		self.db = DataContainer.DataContainer( self.localDir, Mode='a', \
			KeepHour=self.keepHour, DebugMode=self.debugMode, BufSize=self.bufSize, FileTimeInterval = self.filetimeinterval, Version=self.version )

	def action(self, fileName) :
		for msgTime, opt, data in self.action2(fileName) :
			recno = self.db.put(msgTime, data, opt)

			# if self.debugMode and recno % 1000 == 0 :
			# 	print 'debug : file=%s, msgTime=%s recno=%s processed' % \
			# 		(fileName, msgTime, recno)

def main() :
	class FtpCdrPrism( ColFtpDC ) :
		def __init__(self) :
			PRISM_IP = '150.23.15.61'
			PRISM_ID = 'eva'
			PRISM_PASSWD = 'fpdl321'
			PRISM_CDR_DIR = '/disk1/data/cdr_old'
			E2E_DATA_DIR = '/home/eva/E2E/DATA/VOICE_CDR'
			E2E_TEMP_DIR = '%s/TEMP' % (E2E_DATA_DIR)

			ColFtpDC.__init__(self, PRISM_IP, PRISM_ID, PRISM_PASSWD, \
				PRISM_CDR_DIR, E2E_TEMP_DIR, E2E_DATA_DIR )
		
		def actionMakeRealFileName( fileName ) :
			return fileName

		def action2(self, fileName) :
			fh = open(fileName)

if __name__ == '__main__' : main()
