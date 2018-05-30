#!/home/mobigen/bin/python
# -*- coding: UTF-8 -*-

#-----------------------------------------------------
# version | date : writer : description
#---------+-------------------------------------------
# V1.0    | 061023 : tesse : first edtion
#---------+-------------------------------------------
# V1.1    | 061027 : tesse : add dump load function
#---------+-------------------------------------------
# V1.2    | 061031 : tesse : add change server port command
#-----------------------------------------------------
# V1.21   | 061103 : tesse : add log when 10000 query
#-----------------------------------------------------
# V1.22   | 061107 : tesse : fix bug binary head read
#-----------------------------------------------------
# Deprecated : use select version
#-----------------------------------------------------

import os, sys, time, threading
from socket import *

try :
	import psyco
	psyco.full()
except :
	pass

import signal
SHUTDOWN = False
DEBUG = False

def shutdown(sigNum=0, frame=0) :
	#print sigNum
	global SHUTDOWN
	SHUTDOWN = True

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGHUP, shutdown)
signal.signal(signal.SIGPIPE, shutdown)

HELP_STR = '''
=============================================================================================
PType 1 (BINARY mode)
---------------------------------------------------------------------------------------------
cmd | description | send format                         | recv format
----+-------------+-------------------------------------+------------------------------------
PUT | put data    | header + keyLen(10) + key + value   | no answer
GET | get data    | header + keyLen(10) + key           | header + value
KYS | get keys    | header                              | header + keyLen(10) + key + ...
VLS | get values  | header                              | header + valLen(10) + val + ...
ITS | get items   | header                              | header + kLen(10)+k+vLen(10)+v ...
KIL | shutdown    | header                              | header
BYE | disconnect  | header                              | no answer
KEY | exists key? | header + keyLen(10) + key           | header
DEL | delete key  | header + keyLen(10) + key           | header
POP | get and del | header + keyLen(10) + key           | header + value
DMP | ASCII dump  | header + fileNameLen(10) + fileName | header
LDR | ASCII load  | header + fileNameLen(10) + fileName | header
CLR | clear data  | header                              | header
LEN | count data  | header                              | header + value
CHP | change port | header + keyLen(10) + portNum       | header
#P6 | ASCII mode  |    #P60000000000                    | ,,OK ,description
=============================================================================================
PType 6 (ASCII mode)
---------------------------------------------------------------------------------------------
cmd | description | command format                      | answer format
---------------------------------------------------------------------------------------------
PUT | put data    | ,,put,key,value                     | no answer
GET | get data    | ,,get,key                           | ,,OK ,value
KYS | get keys    | ,,kys                               | ,,OK ,key,key, ...
VLS | get values  | ,,vls                               | ,,OK ,val,val, ...
ITS | get items   | ,,its                               | ,,OK ,key,val,key,val, ...
KIL | shutdown    | ,,kil                               | ,,OK ,
BYE | disconnect  | ,,bye                               | no answer
KEY | exists key? | ,,key,key                           | ,,OK ,
DEL | delete key  | ,,del,key                           | ,,OK ,
POP | get and del | ,,pop,key                           | ,,OK ,value
DMP | ASCII dump  | ,,dmp,fileName                      | ,,OK ,
LDR | ASCII load  | ,,ldr,fileName                      | ,,OK ,
CLR | clear data  | ,,clr                               | ,,OK ,
LEN | count data  | ,,cnt                               | ,,OK ,value
CHP | change port | ,,chp,portNum                       | ,,OK ,
#P1 | binary mode | ,,#P1                               | header + description
---------------------------------------------------------------------------------------------
'''

def logger( header, id, errStr ) :
	sys.stderr.write( "%s [%s] : %s\n" % (header, id, errStr ) )
	sys.stderr.flush()

def logErr( id, errStr ) :
	logger( '--', id, errStr )

def logStr( id, errStr ) :
	logger( '++', id, errStr )

class Env :
	def __init__(self) :
		self.dict = {}
		self.ipRev = None
		self.portRev = None
		self.thServShutdown = False
		self.qryCnt = 0

class SocketServer(threading.Thread) :

	def __init__(self, argEnv) :
		threading.Thread.__init__(self)
		self.env = argEnv
		self.env.thServShutdown = False

		self.sock = socket( AF_INET, SOCK_STREAM )
		self.sock.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1)
		self.sock.bind((str( self.env.ipRev),int( self.env.portRev)))
		self.sock.listen(10)
		self.sock.settimeout(1) # timeout 처리함. signal을 받은 경우 정상종료하기 위해서.. eek

	def run(self) :
		global SHUTDOWN
		global DEBUG

		logPrnSec = 0
		while 1 :
			try :
				childSocket, addr = ('', '')
				try:
					childSocket, addr = self.sock.accept()
				except timeout :
					if SHUTDOWN :
						logStr( '%s:%s' % (self.env.ipRev, self.env.portRev), 'Shutdown' )
						break

					elif self.env.thServShutdown :
						logStr( '%s:%s' % (self.env.ipRev, self.env.portRev), 'Port Changed' )
						break

					else :
						if logPrnSec % 60 == 0 :
							logStr( "IP:%s, PORT:%s" % (self.env.ipRev, self.env.portRev), 'server thread alive' )
						logPrnSec += 1
						continue
	
				thClient = ThClient(childSocket, str(addr), self.env)
				thClient.setDaemon(1)
				thClient.start()

			except Exception, err :
				logErr( '%s:%s' % (self.env.ipRev, self.env.portRev), err.__str__() )
				break

		try : 
			self.sock.close()
		except :
			pass


class ThClient(threading.Thread) :

	def __init__(self, childSocket, addr, env) :
		threading.Thread.__init__(self)
		self.cSocket = childSocket
		self.cAddress = addr
		logStr( self.cAddress, 'Connected' )
		self.cSocket.settimeout(1) # timeout 처리함. signal을 받은 경우 정상종료하기 위해서.. eek

		self.env = env
		self.pType = 1

	def run(self) :
		global SHUTDOWN
		global DEBUG

		while 1 :
			try :
				cmd = ''
				key = ''
				val = ''
	
				if self.pType == 1 :
					dataHead = ''
					tmp = ''
					remainLen = 16
					while 1 :
						try:
							tmp = self.cSocket.recv(remainLen)
						except timeout:
							if SHUTDOWN: break
							else : continue

						if tmp == '' : break

						dataHead += tmp
						remainLen -= len(tmp)
						if len(dataHead) == 16 : break

					if SHUTDOWN :
						logStr( self.cAddress, 'Shutdown Detected while read binary header' )
						break

					if tmp == '' :
						logStr( cAddress, 'Disconnected at read binary header' )
						break

					self.env.qryCnt += 1
					if self.env.qryCnt % 10000 == 0 :
						logStr( self.cAddress, 'qryCnt = [%s] : %s' % (self.env.qryCnt, time.ctime()) )
						self.env.qryCnt = 0
						

					### tesse in case of not 16 byte ###

					cmd = dataHead[3:6]
					dataSize = dataHead[6:]
					try : dataSize = int(dataSize)
					except :
						logStr( self.cAddress, 'Disconnected because bad binary header' )
						break

					res			= ''
					resList	 	= []
					remainLen 	= dataSize
		
					while 1 :
						if remainLen <= 0 :
							res = ''.join(resList)
							break
		
						readData = ''
						try:
							readData 	= self.cSocket.recv( remainLen )
						except timeout :
							if SHUTDOWN :
								logStr( self.cAddress, 'Shutdown' )
								break
							else :
								continue
							
						if readData == '' :
							logStr( self.cAddress, 'Disconnected at read body' )
							break
		
						else :
							resList.append(readData)
							remainLen	-= len( readData)
		
					if SHUTDOWN : break
	
					### 0 : 10 : key : val
					if res != '' :
						keyLen = int( res[:10] )
						key = res[10:10+keyLen]
						val = res[10+keyLen:]
	
				else : ### ptype == 6
					dataList = []
					res = ''
	
					readData = ''
					while 1 :
						try:
							readData = self.cSocket.recv(1024)
						except timeout:
							if SHUTDOWN :
								logStr( self.cAddress, 'Shutdown' )
								break
							else :
								continue
		
						if readData == '' :
							logStr( self.cAddress, 'Disconnected at read ascii data' )
							break
					
						dataList.append(readData)
	
						if readData[-1] == '\n' :
							res = ''.join( dataList )
							res = res.strip()
							break
	
					self.env.qryCnt += 1
					if self.env.qryCnt % 10000 == 0 :
						logStr( self.cAddress, 'qryCnt = [%s] : %s' % (self.env.qryCnt, time.ctime()) )
						self.env.qryCnt = 0

					if SHUTDOWN : break
					if readData == '' : break

					dataList = res.split( ',', 4 )
					if len(dataList) == 3 :
						(cmd) = dataList[2]
					elif len(dataList) == 4 :
						(cmd, key) = dataList[2:4]
					elif len(dataList) == 5 :
						(cmd, key, val) = dataList[2:5]
	
				cmd = cmd.upper()
				if DEBUG : logStr( self.cAddress, 'cmd=[%s] key=[%s] val=[%s]' % (cmd, key, val) )

				if cmd == '#P6' :
					self.pType = 6
					self.sendAnswer( 'OK ', 'protocol type changed to TYPE6' )
				
				elif cmd == '#P1' :
					self.pType = 1
					self.sendAnswer( 'OK ', 'protocol type changed to TYPE1' )
	
				elif cmd == 'PUT' : ### no answer for performance
					self.env.dict[key] = val
	
				elif cmd == 'GET' :
					if self.env.dict.has_key(key) :
						self.sendAnswer( 'OK ', self.env.dict[key] )
					else :
						self.sendAnswer( 'NOK', 'no key exists : [%s]' % key )
	
				elif cmd == 'KYS' :
					keyList = []

					if self.pType == 1 :
						for tmp in self.env.dict.keys() :
							tmpLen = "%010d" % len(tmp)
							keyList.append(tmpLen)
							keyList.append(tmp)
						self.sendAnswer( 'OK ', ''.join(keyList) )

					elif self.pType == 6 :
						for tmp in self.env.dict.keys() :
							keyList.append(tmp)
						self.sendAnswer( 'OK ', ','.join(keyList) )
	
				elif cmd == 'VLS' :
					valList = []

					if self.pType == 1 :
						for tmp in self.env.dict.values() :
							tmpLen = "%010d" % len(tmp)
							valList.append(tmpLen)
							valList.append(tmp)
						self.sendAnswer( 'OK ', ''.join(valList) )

					elif self.pType == 6 :
						for tmp in self.env.dict.values() :
							valList.append(tmp)
						self.sendAnswer( 'OK ', ','.join(valList) )
	
				elif cmd == 'ITS' :
					valList = []

					if self.pType == 1 :
						for (k,v) in self.env.dict.items() :
							kLen = "%010d" % len(k)
							valList.append(kLen)
							valList.append(k)

							vLen = "%010d" % len(v)
							valList.append(vLen)
							valList.append(v)
						self.sendAnswer( 'OK ', ''.join(valList) )

					elif self.pType == 6 :
						for (k,v) in self.env.dict.items() :
							valList.append(k)
							valList.append(v)
						self.sendAnswer( 'OK ', ','.join(valList) )
	
				elif cmd == 'LEN' :
					self.sendAnswer( 'OK ', len(self.env.dict) )

				elif cmd == 'KIL' :
					logStr( self.cAddress, 'Caution: cmd=[%s] key=[%s] val=[%s] executed' % (cmd,key,val) )
					SHUTDOWN = True
					self.sendAnswer( 'OK ', '' )
					break
	
				elif cmd == 'BYE' :
					logStr( self.cAddress, 'Caution: cmd=[%s] key=[%s] val=[%s] executed' % (cmd,key,val) )
					break
	
				elif cmd == 'KEY' :
					if self.env.dict.has_key(key) :
						self.sendAnswer( 'OK ', key )
					else :
						self.sendAnswer( 'NOK', 'no key exists : [%s]' % key )
	
				elif cmd == 'DEL' :
					if self.env.dict.has_key(key) :
						del self.env.dict[key]
						self.sendAnswer( 'OK ', '' )
					else :
						self.sendAnswer( 'NOK', 'no key exists : [%s]' % key )
	
				elif cmd == 'POP' :
					if self.env.dict.has_key(key) :
						self.sendAnswer( 'OK ', self.env.dict.pop(key) )
					else :
						self.sendAnswer( 'NOK', 'no key exists : [%s]' % key )
	
				elif cmd == 'DMP' :
					logStr( self.cAddress, 'Caution: cmd=[%s] key=[%s] val=[%s] executed' % (cmd,key,val) )
					fileName = key
					try :
						self.dump(fileName)
						self.sendAnswer( 'OK ', '' )
					except Exception, err :
						self.sendAnswer( 'NOK', err.__str__() )
		
				elif cmd == 'LDR' :
					logStr( self.cAddress, 'Caution: cmd=[%s] key=[%s] val=[%s] executed' % (cmd,key,val) )
					fileName = key
					try :
						self.load(fileName)
						self.sendAnswer( 'OK ', '' )
					except Exception, err :
						self.sendAnswer( 'NOK', err.__str__() )
				
				elif cmd == 'CLR' :
					logStr( self.cAddress, 'Caution: cmd=[%s] key=[%s] val=[%s] executed' % (cmd,key,val) )
					self.env.dict.clear()
					self.sendAnswer( 'OK ', '' )
	
				elif cmd == 'CHP' :
					logStr( self.cAddress, 'Caution: cmd=[%s] key=[%s] val=[%s] executed' % (cmd,key,val) )
					portNum = key
					try :
						self.env.portRev = portNum
						self.env.thServShutdown = True
						self.sendAnswer( 'OK ', '' )
					except Exception, err :
						self.sendAnswer( 'NOK', err.__str__() )
				
				elif cmd == 'HLP' :
					self.sendAnswer( 'OK ', HELP_STR )

			except Exception, err :
				logErr( self.cAddress, err.__str__() )

		try : 
			self.cSocket.close()
			logStr( self.cAddress, 'Disconnected at close' )
		except :
			pass

	def sendAnswer(self, cmd, ans) :
		if self.pType == 1 :
			sendStr = '100%s%010d%s' % (cmd, len(ans), ans)

		elif self.pType == 6 :
			sendStr = ',,%s,%s\n' % (cmd, ans)

		self.cSocket.send( sendStr )

	def dump(self, fileName) :
		dumpFP = open( fileName, 'w' )
		for (k,v) in self.env.dict.items() :
			kLen = len(k)
			dumpFP.write( "%010d%s%s\n" % (kLen,k,v) )
		dumpFP.close()

	def load(self, fileName) :
		dumpFP = open( fileName )
		for line in dumpFP :
			kLen = int( line[:10] )
			k = line[10: 10+kLen]
			v = line[10+kLen: -1]
			self.env.dict[k] = v
		dumpFP.close()

	def __del__(self) :
		try : 
			self.cSocket.close()
			logStr( self.cAddress, 'Closed' )
		except : pass
	
def main() :
	global SHUTDOWN

	try :
		### 뒤에 인수가 올경우 : 붙이고, 아닐경우 안붙인다
		### : 에 상관없이 optList 는 튜플의 리스트로 반환된다.
		# optList, args = getopt.getopt(sys.argv[1:], 'p:f:t:w:n:i:')

		args = sys.argv[1:]
		if len(args) != 2 : raise Exception
		optDict = {}

		# for optKey, optVal in optList : optDict[optKey] = optVal

	except :
		#print 'usage : %s [-pftwni] homeDir infoFileName' % (sys.argv[0])
		#print '        -p[11] : protocol type, default:1'
		#print '        -f[okd|kd|d] : okd : message format = option(16byte) key(10byte) data'
		#print '                        kd : message format = key(10byte) data'
		#print '                         d : message format = data'
		#print '                           : default format = fileTime(yyyymmddhhmmss) option(16byte) key(10byte) data'
		#print '        -t[Num] : read block timeout second, default is 1, for signal process'
		#print '        -w[Num] : if no date to read, wait this second, default is 0.1'
		#print '        -n[Num] : if no data to read, list up next file for this second interval, default is 10'
		#print '        -i[Num] : info file update period record count, default is 10'
		#sys.exit()

		print 'usage : %s serviceIP servicePort' % (sys.argv[0])
		sys.exit()

	argEnv = Env()
	argEnv.ipRev = args[0]
	argEnv.portRev = args[1]

	svrTh = SocketServer( argEnv )
	svrTh.start()

	while 1 :
		if not svrTh.isAlive() :
			svrTh = SocketServer( argEnv )
			svrTh.setDaemon(1)
			svrTh.start()

		time.sleep(1)
		if SHUTDOWN : break

if __name__ == '__main__' :
	#print os.getpid()
	main()
