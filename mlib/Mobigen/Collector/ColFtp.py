#!/usr/bin/python

VERSION = '1.10'
# 050905 : tesse

from ftplib import FTP
import threading, time, signal, re, os
import Mobigen.Common.Log as Log; Log.Init()

class TimeReachException(Exception) : pass
class FileNotFoundException(Exception) : pass

class ColFtp(threading.Thread) :
	def __init__(self, ip, id, passwd, rmtDir, homeDir, **args) :
		threading.Thread.__init__(self)

		# try : self.lsPat = '%s/%s' % (rmtDir, args['LsPat'])
		try : self.lsPat = args['LsPat']
		except : self.lsPat = '*'

		try : self.port = int( args['Port'] )
		except : self.port = 21

		try : self.sleep = int( args['Sleep'] )
		except : self.sleep = 10

		try : self.DisconnectCount = int( args['DisconnectCount'] )
		except : self.DisconnectCount = 0
	#	__LOG__.Watch(self.DisconnectCount)

		try :
			# Recovery = "20060214120000,20060215120000"
			self.timerange = args['TimeRange'].split(",")
			self.maketime = args['TimeRangeFormat']
		except :
			self.timerange = None
			self.timerangepos = None

		self.ip = ip
		self.id = id
		self.passwd = passwd
		self.rmtDir = rmtDir

		self.connectFTP()

		self.idxFileName = '%s/ftp.info' % (homeDir)
		self.homeDir = homeDir
		self.oldFileNames = {}
		self.shutdown = False

		if os.path.exists(homeDir) == False :
			os.mkdir(homeDir)

	def connectFTP(self) :
		while True:
			try :
				self.ftp = FTP(host=self.ip, user=self.id, passwd=self.passwd)
				self.ftp.cwd(self.rmtDir)
				break
			except :
				time.sleep(10)
				continue

	def run(self) :
		try :
			count = 0
			while True :
				if self.shutdown : break

				if os.path.exists(self.idxFileName) :
					self.loadIdx()
	
				newFileNames = self.getNewFileNames()
				self.mkIdxTrue(newFileNames)
	

				if(self.timerange!=None and len(newFileNames) ==0 ) :
					raise FileNotFoundException

				for fileName in newFileNames :
				#	__LOG__.Watch(fileName)

					if(self.timerange!=None) : 
						__FILE_TIME_CHECK__ = fileName
						exec("strTime = %s" % (self.maketime))
					#	__LOG__.Watch((strTime, self.timerange[0], self.timerange[1]))
	
						if strTime < self.timerange[0] : continue
						if strTime > self.timerange[1] : raise TimeReachException

					if self.oldFileNames.has_key(fileName) == False :
						se = re.search( '([^/]+)$', fileName )
						wFileName = '%s/%s' % ( self.homeDir, se.group(1) )
	
						try :
							self.getFile(fileName, wFileName)
							self.action(wFileName)
							__LOG__.Trace( '[%d]%s -> %s processed' % (count, fileName, wFileName) )

							if(self.DisconnectCount) : 
								count = count + 1
								if(count%self.DisconnectCount==0) : self.shutdown = True

						except :
							__LOG__.Exception()
	
						self.oldFileNames[fileName] = True

				if(self.timerange!=None ) :
					raise FileNotFoundException
					
				self.dumpIdx()
				time.sleep(self.sleep)

		except FileNotFoundException :
			raise FileNotFoundException

		except TimeReachException :
			raise TimeReachException

		except :
			__LOG__.Exception()

		self.dumpIdx()

		try : self.ftp.quit()
		except : pass
		

	def mkIdxTrue(self, newFileNames) :
		for fileName in newFileNames :
			if self.oldFileNames.has_key(fileName) :
				self.oldFileNames[fileName] = True

		for key in self.oldFileNames.keys() :
			if self.oldFileNames[key] == False :
				self.oldFileNames.pop(key)
		
	def loadIdx(self) :
		self.oldFileNames = {}
		fh = open(self.idxFileName)
		for fileName in fh.readlines() :
			try : self.oldFileNames[ fileName[:-1] ] = False
			except : pass
		fh.close()
	
	def dumpIdx(self) :
		fh = open(self.idxFileName + '.tmp', 'w')
		fileNames = self.oldFileNames.keys()
		fileNames.sort()
		for fileName in fileNames :
			if self.oldFileNames[fileName] == True :
				fh.write( fileName + '\n' )
		fh.close()
		os.rename( self.idxFileName + '.tmp', self.idxFileName )

	def getNewFileNames(self) :
		__LOG__.Trace( 'lsPat=%s' % self.lsPat )
		lsCount = 0
		while True :
			try :
				fileNames = self.ftp.nlst(self.lsPat)
				break
			except :
				time.sleep(10)
				lsCount = lsCount + 1

				if(lsCount > 10) :
					try : self.ftp.quit()
					except : pass
					self.connectFTP()
					__LOG__.Trace( 'FTP Reconnection...')
					lsCount = 0
				else :
					__LOG__.Trace( 'nlst fail, try again...' )

		fileNames.sort()
		return fileNames
	
	def getFile(self, fileName, wFileName) :
		if len(self.ftp.nlst(fileName)) == 0 : raise Exception, 'to late to get file=[%s]' % fileName
		cmd = 'RETR %s' % (fileName)
		self.ftp.retrbinary( cmd, open(wFileName + '.tmp', 'wb' ).write )	
		os.rename( wFileName + '.tmp', wFileName )
	
	def rmFile(self, fileName) :
		try : os.unlink( rmFileName)
		except : pass

	def close(self) :
		self.shutdown = True
		self.join()

def main() :
	class Test(ColFtp) :
		def __init__(self) :
			ColFtp.__init__(self, 'localhost', 'eva', 'hello.mobigen', '/home/eva/temp', '.')

		def action(self, fileName) :
			__LOG__.Trace( 'action fileName = %s' % (fileName) )
			pass

	obj = Test()
	obj.run()

if __name__ == '__main__' : main()
