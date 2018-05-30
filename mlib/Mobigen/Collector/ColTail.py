#!/bin/env python
# coding: iso-8859-1
#!/usr/local/mobigen/bin/python
# -*- coding: euc-kr -*-
# coding: ko_KR.eucKR

VERSION = '1.9.2'
# 050905 : tesse
# 050906 : tesse
#		*	self.filePatRe = re.subn( '\*', '.*', self.filePat )
#		=>	self.filePatRe, tmp = re.subn( '\*', '.*', self.filePat )
#		*	add def close(self) :
#		*	se = re.search( '([^\s+]$)', line )
#		=>	se = re.search( '([^\s+]\n$)', line )
# 050922 : 1.6 : tesse
#		*	self.filePatRe, tmp = re.subn( '\?', '.', self.filePatRe )
# 060222 : 1.7 : sunghoon
#		*	add TimeRange Mode
# 060305 : 1.8 : sunghoon
# 070529 : 1.9.2 : eek
#		*	add noDataRead(msg)
#		*	add error(msg) 


from telnetlib import Telnet
import time, sys, re, os, types
import socket  # socket
import Mobigen.Common.Log as Log; Log.Init()

class FileNotFoundException(Exception) : pass
class TimeReachException(Exception) : pass

class ColTail(object) :

	def __init__(self, ip, id, passwd, homeDir, filePat, curFileName, **args) :
		# homeDir = '.'
		# filePat = '*-121/*.db'
		# filePatRe = '\S+-121/\S+.db'
		# curFileName = '050906-121/050906-121.db'


		object.__init__(self)

		if(type(ip)==types.DictType) :
			args = ip
			ip = args['RemoteIP']
			id = args['RemoteID']
			passwd = args['RemotePassword']
			homeDir = args['HomeDir']
			filePat = args['RemoteFilePat']
			curFileName = args['CurrentFileName']

		try : self.nonBlock = args['NonBlock']
		except : self.nonBlock = False

		try : self.timeout = int( args['Timeout'] )
		except : self.timeout = 10

		try : self.curFileLine = int( args['StartLine'] )
		except : self.curFileLine = 0

		try : self.debugMode = args['DebugMode']
		except : self.debugMode = False

		try : self.port = int( args['Port'] )
		except : self.port = 23

		try : self.isamMode = args['ISAM']
		except : self.isamMode = False

		try : self.PromptCheck = args['PromptCheck']
		except : self.PromptCheck = True

		try : self.UserPrompt = args['UserPrompt']
		except : self.UserPrompt = '%'


		try : self.UserTailFormat = args['UserTailFormat']
		except : self.UserTailFormat = None

		try : self.tailOpt = args['TailOpt']
		except : self.tailOpt = 0

		__LOG__.Trace("ColTail : tailOpt = %s" % self.tailOpt)

		try : 
			# Recovery = "20060214120000,20060215120000"
			self.timerange = args['TimeRange'].split(",")
			self.maketime = args['TimeRangeFormat']
			curFileName = '0'
		except : 
			self.timerange = None 
			self.timerangepos = None

		self.shutdown = False

		self.ip = ip
		self.id = id
		self.passwd = passwd
		self.homeDir = homeDir

		self.filePat = filePat
		tmpList = self.filePat.split('/')
		if len(tmpList) == 1 :
			self.dirStr = ''
		else :
			self.dirStr = '/'.join(tmpList[:-1])
		self.fileStr = tmpList[-1]
		self.fileStrRe = re.sub( '\*', '\S+', self.fileStr )
		self.fileStrRe = re.sub( '\?', '.', self.fileStrRe )

		self.curFileName = curFileName
		self.prompt = self.UserPrompt
		self.nextFileBuf = []
		self.dataBuf = ''

		self.telnetLs = None
		self.telnetTail = None
		self.emptyCnt = 0
		self.forLsConnCnt = 0

		self.loginIncorrect = False
		self.lsConnFlag = False
		self.tailSock = None


		while True:
			if self.connectAll():
				break

			__LOG__.Trace("connect error\n")
			time.sleep(60)

		if self.curFileName == '0' :
			while 1 :
				if self.checkFirstFile() :
					break
				else :
					__LOG__.Trace( 'no search file=%s, lineNum=0, sleep 60' \
						% (self.curFileName) )
					time.sleep(60)

		elif self.curFileName == '-1' :
			while 1 :
				if self.checkLastFile() :
					break
				else :
					__LOG__.Trace( 'no search file=%s, lineNum=0, sleep 60' \
						% (self.curFileName) )
					time.sleep(60)

		elif self.existCurrentFile() == False :
			while 1 :
				if self.checkNextFile() :
					break
				else :
					__LOG__.Trace( 'no search file=%s, lineNum=0, sleep 60' \
						% (self.curFileName) )
					time.sleep(60)

		self.actTail()

	def connectPrepare(self, telnetObj) :
		return

	def connect(self) :

		if self.loginIncorrect == True:
			__LOG__.Trace("self.loginIncorrect == True")
			return

		while 1 :
			try :
				telnet = Telnet(self.ip, self.port)
				__LOG__.Trace( telnet.read_until('login:', self.timeout) )
		
				telnet.write(self.id + '\n')
				__LOG__.Trace( telnet.read_until('Password:', self.timeout) )
		
				telnet.write(self.passwd + '\n')
				time.sleep(5)
				line = telnet.read_until("\n", 3)
				line = telnet.read_until("\n", 3)
				if re.search("Login incorrect", line):
					__LOG__.Trace( 'Login incorrect' )
					self.loginIncorrect = True
					self.error('password fail')
					return None
				else:
					__LOG__.Trace( "passwd ok:[%s]" % line )

				self.connectPrepare(telnet)

				#telnet.write('csh\n')
				#telnet.write('set prompt="%"\n')

				telnet.write('sh\n')
				time.sleep(1)
				telnet.write('PS1="%s"\n' % self.UserPrompt)
				time.sleep(1)

				line = telnet.read_until(self.prompt, self.timeout)
				__LOG__.Trace( 'expect set prompt step1=[%s]' % (line) )

				if line[-2:] == '"%s' % self.UserPrompt :
					self.echo = True
					__LOG__.Trace( 'expect set prompt step2=[%s] ' % telnet.read_until(self.prompt, self.timeout) )
					__LOG__.Trace( '* echo mode' )
				else :
					self.echo = False
					__LOG__.Trace( '* no echo mode' )
	
				self.commandPrompt(telnet, 'stty intr "^C"\n')
				self.commandPrompt(telnet, 'set term=vt100\n')
				self.commandPrompt(telnet, 'unalias cd\n')
				self.commandPrompt(telnet, 'cd %s\n' % (self.homeDir) )

				for i in range(10) : telnet.read_until(self.prompt, 0.1)

				break

			except Exception, err:
				__LOG__.Trace( 'connection fail, retry' )
				__LOG__.Exception()
				try : telnet.close()
				except : pass

				self.error('connection fail')
				time.sleep(10)

		return telnet	

	def error(self, msg):
		__LOG__.Trace( 'error [%s]' % msg )
		pass

	def write(self, telObj, cmd) :
		try :
			telObj.write(cmd)
		except :
			telObj = self.connect()
			telObj.write(cmd)
		
	def commandPrompt(self, telObj, cmd) :
		telObj.write(cmd)
		__LOG__.Trace( 'cmd=[%s], res=[%s]' % (cmd.strip(), telObj.read_until(self.prompt, self.timeout).strip() ) )

	def commandNewLine(self, telObj, cmd) :
		self.write( telObj, cmd )
		if self.echo :
			__LOG__.Trace( telObj.read_until('\n', self.timeout) )

	def actTail(self, user_cmd_format=None) :
		for i in range(10) : self.telnetTail.read_until(self.prompt, 0.1)

		if(user_cmd_format) :
			# ?????? ???É¾? ????À» ?????Ò¶??? ??À½?? ??Àº ???É¾? ???Ú¿?À» ?????Ï¿??? ??
			# /usr/bin/tail +%sf       %s  
			#                FileLIne  FileName
			# user_cmd_format = '/usr/bin/tail +%sf %s'
			cmd = user_cmd_format % (self.curFileLine, self.curFileName)
		elif(self.UserTailFormat) :
			cmd = self.UserTailFormat % (self.curFileLine, self.curFileName)
		elif self.isamMode  :
			cmd = '/opt/ruc/bin/orgtail %s %s\n' % (self.curFileName, str(self.curFileLine))
		elif self.tailOpt :
			cmd = 'tail -n +%s -f %s\n' % (self.curFileLine, self.curFileName)
		else :
			cmd = 'tail +%sf %s\n' % (self.curFileLine, self.curFileName)

		self.commandNewLine(self.telnetTail, cmd)

	def connectAll(self) :
		self.telnetLs = self.connect()
		if self.telnetLs == None:
			__LOG__.Trace("self.telnetLs == None")
			return False

		self.lsConnFlag = True

		__LOG__.Trace("##################################################")
		__LOG__.Trace("## Tail Thread")
		self.telnetTail = self.connectTail()

		if self.telnetTail == None:
			__LOG__.Trace("self.telnetTail == None")
			return False

		return True

	def connectTail(self):

		if self.loginIncorrect == True:
			__LOG__.Trace("self.loginIncorrect == True")
			return None

		while self.lsConnFlag == False:
			if self.shutdown : break

			self.telnetLs = self.connect()
			if self.telnetLs == None:
				__LOG__.Trace("self.loginLs == None")
				return None
			break;
			
			__LOG__.Trace( 'wait ls connect socket....' )
			time.sleep(10)

		tail = self.connect()
		if tail:
			self.tailSock = tail.get_socket()
			self.tailSock.settimeout(self.timeout)
			self.tailfd = self.tailSock.makefile()
		return tail

	def next(self) :

		while True :
			if self.shutdown : break

			data = ""
			timeout = False
			try :
				#data = self.telnetTail.read_until('\n', 2)
				#data = self.telnetTail.read_until('\n', 2)
				data = self.tailSock.recv(40960)
				__LOG__.Trace('THIS : %s' % data)
				#data = self.tailfd.readline()
			except socket.timeout:
				#__LOG__.Trace( 'recv timeout ')
				timeout = True
			except :
				pass
				#__LOG__.Trace( 'tail disconnected, try reconnect' )
				#self.telnetTail = self.connectTail()
				#if self.telnetTail == None:
				#	raise Exception, 'connect error'

				#self.actTail()
				#continue

			if data == "" and timeout == False:
				__LOG__.Trace( 'tail disconnected, try reconnect' )

				time.sleep(10)

				self.telnetTail = self.connectTail()
				if self.telnetTail == None:
					raise Exception, 'connect error'


				self.actTail()

				continue


			### to avoid disconnecting ls connection ###
			self.forLsConnCnt += 1
			if self.forLsConnCnt > 100 :
				self.forLsConnCnt = 0
				self.commandPrompt( self.telnetLs, '\n' )

			### read data ###
			if len(data) > 0 :
				data  = re.sub('\r', '', data)

				### data='prompt', in case of tail terminated ###
				if self.PromptCheck and len(data) > 0 and \
					data[-1] == self.prompt :

					data = data + '\n'

				self.dataBuf += data
				self.emptyCnt = 0

				lineList = self.dataBuf.split('\n')

				if len(lineList) > 1 :
					if len( lineList[-1] ) == 0 :
						lineList.pop()
						self.dataBuf = ''
					else :
						self.dataBuf = lineList.pop()

					self.curFileLine += len(lineList)

					### data='prompt', in case of tail terminated ###
					if self.PromptCheck and len(lineList[-1]) > 0 and \
					  lineList[-1][-1] == self.prompt :
						lineList.pop() # only exclude prompt line
						self.curFileLine -= 2 
						# -1 = prompt line, -2 = 'Terminated' line (if exists)
						self.actTail()

					if len(lineList) :
						return lineList

			### no data to read ###
			else :
				if len(self.nextFileBuf) == 0 :
					#__LOG__.Trace( 'no data to read')
					self.emptyCnt += 1

					# 3min
					if self.emptyCnt >= 18 :
						self.emptyCnt = 0

						# search next file
						if self.checkNextFile() :
							__LOG__.Trace( 'search next file success' )
							self.switchNextFile()
						else:
							# no switch file 
							__LOG__.Trace( 'noDataRead')
							self.noDataRead()
				else :
					__LOG__.Trace( 'search next file in next file buf' )
					self.emptyCnt = 0
					self.setNextFile()
					self.switchNextFile()

				if self.nonBlock :
					raise Exception, 'no data to read.'
				# else :
				#   time.sleep(0.1)

	def noDataRead(self):
		__LOG__.Trace('noDataRead... ColTail')
		pass

	def getFileNameList(self) :
		try:
			for i in range(10) : self.telnetLs.read_until(self.prompt, 0.1)
		except:	
			__LOG__.Exception()

		self.commandNewLine( self.telnetLs, 
			'find ./%s -name "%s" -print | sort \n' % (self.dirStr, self.fileStr) )
		#	'find ./%s -name "%s" -print \n' % (self.dirStr, self.fileStr) )

		fileNameList = []
		lsTimeOutCnt = 0
		while 1 :
			try :
				line = self.telnetLs.read_until('\n', self.timeout)
				if re.search('^find ', line) : continue
				#print 'debug : line=[%s]' % line
			except :
				__LOG__.Trace( 'ls disconnect in getFileNameList, connect again' )
				self.lsConnFlag = False 
				self.telnetLs = self.connect()
				if self.telnetLs == None:
					return []

				self.lsConnFlag = True 

				time.sleep(10)
				continue

			if len(line) > 0 :
				lsTimeOutCnt = 0

				if line[-1] == self.prompt : break
				if line[-1] == '\n' : line = line[:-1]
				if line[-1] == '\r' : line = line[:-1]

				if re.search( self.fileStrRe, line) :
					__LOG__.Trace( 'fileNameList.append=[%s]' % (line) )
					fileNameList.append( line )

			else :
				lsTimeOutCnt += 1
				if lsTimeOutCnt > 100 :
					__LOG__.Trace( 'ls fail, no prompt exist' )
					break
				else :
					time.sleep(0.1)
		
		fileNameList.sort()
		return fileNameList

	def checkNextFile(self) :
		# homeDir = '.'
		# filePat = '*-121/*.db'
		# curFileName = '050906-121/050906-121.db'

		if len(self.nextFileBuf) == 0 :
			fileNameList = self.getFileNameList()

			for fileName in fileNameList :
				# print 'debug : fileName=%s' % (fileName)
				# print 'debug : curFileName=%s' % (self.curFileName)

				if fileName > self.curFileName :
					__LOG__.Trace( 'nextFileBuf.append=[%s]' % (fileName) )
					self.nextFileBuf.append(fileName)

			self.nextFileBuf.sort()

		return self.setNextFile()

	def existCurrentFile(self) :
		fileNameList = self.getFileNameList()
		for fileName in fileNameList :
			# print "debug : fileName", fileName
			# print "debug : cur", self.curFileName
			if fileName == self.curFileName :
				__LOG__.Trace( 'existCurrentFile=[%s]' % self.curFileName )
				return True

		__LOG__.Trace( 'no existCurrentFile=[%s]' % (self.curFileName) )
		return False

	def setNextFile(self) :
		if(self.timerange==None) :
			if len(self.nextFileBuf) == 0 :
				return False
			else :
				self.curFileName = self.nextFileBuf.pop(0)
				self.curFileLine = 0
				__LOG__.Trace( 'change curFileName = [%s]' % (self.curFileName) )
				return True
		else :
			while True :
				if len(self.nextFileBuf) == 0 :
					# ?????? ???? Data?? ?Ì¿??Ï¹Ç·? Ã³À½ ?Ñ¹??? File List?? ??Á®?À¸? ?È´?.
					raise FileNotFoundException

				self.curFileName = self.nextFileBuf.pop(0)
				self.curFileLine = 0

				__FILE_TIME_CHECK__ = self.curFileName
				exec("strTime = %s" % (self.maketime))
			#	__LOG__.Watch(strTime)

				if strTime < self.timerange[0] : continue
				if strTime > self.timerange[1] : raise TimeReachException

				return True

	def setLastFile(self) :
		if len(self.nextFileBuf) == 0 :
			return False
		else :
			self.curFileName = self.nextFileBuf.pop()
			self.nextFileBuf = []
			self.curFileLine = 0
			__LOG__.Trace( 'change curFileName = [%s]' % (self.curFileName) )
			return True

	def checkFirstFile(self) :
		fileNameList = self.getFileNameList()
		self.nextFileBuf = fileNameList[:]
		return self.setNextFile()

	def checkLastFile(self) :
		fileNameList = self.getFileNameList()
		self.nextFileBuf = fileNameList[:]
		return self.setLastFile()

	def switchNextFile(self) :
		self.commandPrompt( self.telnetTail, '\x03' + '\n')
		self.actTail()

	def close(self) :
		try : self.telnetLs.close()
		except : pass
		try : self.telnetTail.close()
		except : pass

	def __del__(self)  :
		self.close()

def main() :

	#rmtIp = '10.12.21.31'
	#rmtId = 'common'
	#rmtPasswd = 'web07.cc'
	#rmtHome = '/usr1/common/R8.1.0_PKG/DATA/MMI'
	#rmtPrompt = ']#'

#	rmtIp = '150.23.15.92'
#	rmtId = 'eva'
#	rmtPasswd = 'hello.mobigen'
#	rmtPrompt = '$'
#	rmtHome = '/home/eva/user/seory/DATA/BSM007'
#	rmtFilePat = 'S????.history'
#	rmtFileName = 'S0925.history'

#	rmtIp = '150.23.15.92'
#	rmtId = 'eva'
#	rmtPasswd = 'hello.mobigen'
#	rmtHome = '/home/eva/user/seory/DATA/BSM007'
#	rmtFilePat = 'S????.history'

#	rmtIp = '60.30.30.61'
#	rmtId = 'nms'
#	rmtPasswd = '0424w2cdma'
#	rmtHome = '/array1/umts/urmdata/history/MHD'
#	rmtFilePat = '[0-9][0-9]*/*.MHD'

	rmtIp = '60.30.26.61'
	rmtId = 'nms'
	rmtPasswd = '0424wcdma'
	rmtHome = '/array1/umts/urmdata/history/MHD'
	rmtFilePat = '20070521.MON/12.MHD'

	#obj = ColTail( rmtIp, rmtId, rmtPasswd, rmtHome, rmtFilePat, '0', TimeRange = "20060220100000,20060220110000", TimeRangeFormat = "25,37")
	obj = ColTail( rmtIp, rmtId, rmtPasswd, rmtHome, rmtFilePat, '0')

	while True :
		lineList = obj.next()
		for line in lineList :
			print line
			#__LOG__.Trace( 'res=[%s]' % (line) )

if __name__ == '__main__' : main()
