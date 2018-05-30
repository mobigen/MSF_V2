#!/bin/env python
# -*- coding: UTF-8 -*-

VERSION = "V1.92"

#-----------------------------------------------------
# version | date : writer : description
#-----------------------------------------------------
# V1.91   | 100323 : eek  : Broken pipe clear
#---------+-------------------------------------------
# V1.85   | 071126 : eek  : -l log option add
#---------+-------------------------------------------
# V1.84   | 071126 : eek  : BerkeleyDB DUMP + Clear Command 'DCK' Add
#-----------------------------------------------------
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
# V1.3    | 061108 : tesse : fix bug ascii read
#         | * add read timeout function
#         | * fix dump and load
#-----------------------------------------------------
# V1.4    | 061109 : tesse : add mpt mgt function
#         | * add dump load Ascii Binary
#-----------------------------------------------------
# V1.5    | 061110 : tesse : add app map function
#-----------------------------------------------------
# V1.6    | 061113 : tesse : change default PType1 to Type6
#-----------------------------------------------------
# V1.7    | 061115 : tesse : add PType option
#-----------------------------------------------------
# V1.71   | 061117 : tesse : add Rsv Field : #E
#-----------------------------------------------------
# V1.72   | 061120 : tesse : correct hlp about MGT
#-----------------------------------------------------
# V1.8    | 061128 : tesse : change log, use SFProtocol
#-----------------------------------------------------
# V1.81   | 070914 : jung jonghoon : change APP, MAP 
#-----------------------------------------------------
# V1.82   | 071010 : jung jonghoon : change MAP 393line Bug 
#-----------------------------------------------------
# V1.83   | 071015 : jung jonghoon : BerkeleyDB DUMP Method Add 
#-----------------------------------------------------

import Mobigen.Common.Log as Log; Log.Init()
#from SFProtocol import *

import os, sys, time, select, struct, getopt, copy, thread
from socket import *

try :
	import psyco
	psyco.full()
except :
	pass

try :
	from bsddb3 import db
except :
	try: from bsddb import db
	except: db = None



import signal
SHUTDOWN = False
DEBUG = False
DISCON_TIMEOUT = 10
MAX_PACKET_SIZE = 32768
#MAX_PACKET_SIZE = 1024

def shutdown(sigNum=0, frame=0) :
	global SHUTDOWN
	SHUTDOWN = True

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGHUP, shutdown)
signal.signal(signal.SIGPIPE, signal.SIG_IGN)

HELP_STR = '''
=============================================================================================
PType 1 (BINARY mode)
---------------------------------------------------------------------------------------------
cmd | description | send format                         | recv format
----+-------------+-------------------------------------+------------------------------------
    |             | header = 1#Ecccllllllllll : ccc(cmd), l..l(lenth ascii)
----+-------------+-------------------------------------+------------------------------------
PUT | put data    | header + keyLen(10) + key + value   | no answer
APP | append data | header + keyLen(10) + key + value   | no answer
MPT | multiple put| header + keyLen(10) + key + valLen(10) + val + ... | no answer
MAP | multiple app| header + keyLen(10) + key + valLen(10) + val + ... | no answer
GET | get data    | header + keyLen(10) + key           | header + value
MGT | multiple get| header + keyLen(10) + key ... | header + kLen(10) + k + vLen(10) + v ...
KYS | get keys    | header                              | header + keyLen(10) + key + ...
VLS | get values  | header                              | header + valLen(10) + val + ...
ITS | get items   | header                              | header + kLen(10)+k+vLen(10)+v ...
KIL | shutdown    | header                              | header
BYE | disconnect  | header                              | no answer
KEY | exists key? | header + keyLen(10) + key           | header
DEL | delete key  | header + keyLen(10) + key           | header
POP | get and del | header + keyLen(10) + key           | header + value
DPA | ASCII dump  | header + fileNameLen(10) + fileName | header
LDA | ASCII load  | header + fileNameLen(10) + fileName | header
DPB | Binary dump | header + fileNameLen(10) + fileName | header
LDB | Binary load | header + fileNameLen(10) + fileName | header
DPK | Bsddb dump  | header + fileNameLen(10) + fileName | header
LDK | Bsddb load  | header + fileNameLen(10) + fileName | header
DCK | DPK + CLR   | header + fileNameLen(10) + fileName | header
CLR | clear data  | header                              | header
LEN | count data  | header                              | header + value
CHP | change port | header + keyLen(10) + portNum       | header
#P6 | ASCII mode  | 1#E#P60000000000                    | 6,#E,OK ,description
=============================================================================================
PType 6 (ASCII mode)
---------------------------------------------------------------------------------------------
cmd | description | command format                      | answer format
---------------------------------------------------------------------------------------------
PUT | put data    | ,,put,key,value                     | no answer
APP | append data | ,,app,key,value                     | no answer
MPT | multiple put| ,,mpt,key,value, ...                | no answer
MAP | multiple app| ,,map,key,value, ...                | no answer
GET | get data    | ,,get,key                           | 6,#E,OK ,value
MGT | multiple get| ,,mgt,key, ...                      | 6,#E,OK ,key,val, ...
KYS | get keys    | ,,kys                               | 6,#E,OK ,key,key, ...
VLS | get values  | ,,vls                               | 6,#E,OK ,val,val, ...
ITS | get items   | ,,its                               | 6,#E,OK ,key,val,key,val, ...
KIL | shutdown    | ,,kil                               | 6,#E,OK ,
BYE | disconnect  | ,,bye                               | no answer
KEY | exists key? | ,,key,key                           | 6,#E,OK ,
DEL | delete key  | ,,del,key                           | 6,#E,OK ,
POP | get and del | ,,pop,key                           | 6,#E,OK ,value
DPA | ASCII dump  | ,,dpa,fileName                      | 6,#E,OK ,
LDA | ASCII load  | ,,lda,fileName                      | 6,#E,OK ,
DPB | Binary dump | ,,dpb,fileName                      | 6,#E,OK ,
LDB | Binary load | ,,ldb,fileName                      | 6,#E,OK ,
DPK | Bsddb dump  | ,,dpk,fileName                      | 6,#E,OK ,
LDK | Bsddb load  | ,,ldk,fileName                      | 6,#E,OK ,
DCK | DPK + CLR   | ,,dck,fileName                      | 6,#E,OK ,
CLR | clear data  | ,,clr                               | 6,#E,OK ,
LEN | count data  | ,,len                               | 6,#E,OK ,value
CHP | change port | ,,chp,portNum                       | 6,#E,OK ,
#P1 | binary mode | ,,#P1                               | header + description
=============================================================================================
ETC
---------------------------------------------------------------------------------------------
DUMP File Format
---------------------------------------------------------------------------------------------
4byte total len<------------------->
               4byte key len<->
                            key
                               value
---------------------------------------------------------------------------------------------
'''

def sendAnswer(cSock, pType, cmd, ans) :
	if pType == 1 :
		sendStr = '1#E%s%010d%s' % (cmd, len(ans), ans)

	elif pType == 6 :
		sendStr = '6,#E,%s,%s\n' % (cmd, ans)

	sIdx = 0
	while sIdx < len(sendStr) :
		cSock.sendall( sendStr[sIdx : sIdx+MAX_PACKET_SIZE] )
		sIdx += MAX_PACKET_SIZE

### DUMP Format ##############
# 4byte len<--------------->
#          4byte len<->
#                   key
#                      value
##############################
def dumpBinary(dict, fileName) :
	dumpFP = open( fileName, 'w' )
	for (k,v) in dict.items() :
		kLen = len(k)
		vLen = len(v)
		tLen = kLen + vLen + 4

		tLen = struct.pack('!I', tLen)
		kLen = struct.pack('!I', kLen)
		dumpFP.write( tLen + kLen + k + v )

	dumpFP.close()

def loadBinary(dict, fileName) :
	dumpFP = open( fileName )
	while 1 :
		tLen = dumpFP.read(4)
		if tLen == '' : break

		tLen = struct.unpack('!I', tLen)[0]
		if tLen > os.path.getsize(fileName) : raise Exception, 'loadBinary : bad file format'

		data = dumpFP.read(tLen)
		if data == '' : break

		kLen = struct.unpack('!I', data[:4])[0]
		if tLen > os.path.getsize(fileName) : raise Exception, 'loadBinary : bad file format'

		k = data[4:4+kLen]
		v = data[4+kLen:]
		dict[k] = v
	
	dumpFP.close()

def dumpAscii(dict, fileName) :
	dumpFP = open( fileName, 'w' )
	for (k,v) in dict.items() :
		kLen = len(k)
		dumpFP.write( "%010d%s%s\n" % (kLen,k,v) )
	dumpFP.close()

def loadAscii(dict, fileName) :
	dumpFP = open( fileName )
	fileSize = os.path.getsize(fileName)

	for line in dumpFP :
		try : kLen = int( line[:10] )
		except : raise Exception, 'loadAscii : bad file format'

		if kLen > fileSize : raise Exception, 'loadAscii : bad file format'

		k = line[10: 10+kLen]
		v = line[10+kLen: -1]
		dict[k] = v
	dumpFP.close()

def dumpBerkeley(dict, fileName) :
	if not db: return

	dumpFP = db.DB()
	dumpFP.open(fileName, dbtype=db.DB_BTREE, flags=db.DB_CREATE)
	for (k,v) in dict.items() :
		dumpFP.put(k,v)
	dumpFP.close()

def loadBerkeley(dict, fileName) :
	if not db: return
	dumpFP = db.DB()
	dumpFP.open(fileName, dbtype=db.DB_BTREE, flags=db.DB_RDONLY)
	cur = dumpFP.cursor()
	while 1:
		try :
			(k,v) = cur.get(db.DB_NEXT)
			dict[k] = v
		except :
			break
	cur.close()
	dumpFP.close()

def dumpAndClr(dict, fileName) :
	backupDict = copy.copy(dict)
	dict.clear()
	thread.start_new_thread(dumpBerkeley, (backupDict, fileName,))

def actClient(cSock, cSockFD, dict, addr, clientPType) :
	cAddress = addr
	disconTimeoutCnt = 0
	global SHUTDOWN
	global DEBUG

	cmd = ''
	key = ''
	val = ''

	if clientPType[cSock] == 1 :
		dataHead = ''
		tmp = ''
		remainLen = 16
		while 1 :
			try :
				tmp = cSock.recv(remainLen)
			except timeout :
				if SHUTDOWN :
					__LOG__.Trace( '%s : Shutdown detected while read message header' % cAddress )
					return False
				else :
					disconTimeoutCnt += 1
					if disconTimeoutCnt > DISCON_TIMEOUT :
						__LOG__.Trace( '%s : Connection Timeout while read message header' % cAddress )
						return False
					continue
			
			if tmp == '' :
				__LOG__.Trace( '%s : Disconnected at read binary header' % cAddress )
				return False

			dataHead += tmp
			remainLen -= len(tmp)
			if len(dataHead) == 16 : break
			
		### tesse in case of not 16 byte ###

		cmd = dataHead[3:6]
		dataSize = dataHead[6:]
		try : dataSize = int(dataSize)
		except : 
			__LOG__.Trace( '%s : Disconnected because bad binary header' % cAddress )
			return False
		# print 'debug : cmd=%s, dataSize=%s' % (cmd, dataSize)

		res			= ''
		resList	 	= []
		remainLen 	= dataSize

		while 1 :
			if remainLen <= 0 :
				res = ''.join(resList)
				break

			readData = ''
			try:
				readData 	= cSock.recv( remainLen )
			except timeout :
				if SHUTDOWN : break
				else : 
					disconTimeoutCnt += 1
					if disconTimeoutCnt > DISCON_TIMEOUT :
						__LOG__.Trace( '%s : Connection Timeout while read message body' % cAddress )
						return False
					continue
				
			if readData == '' :
				__LOG__.Trace( '%s : Disconnected while read message body' % cAddress )
				return False

			elif len(readData) == dataSize :
				res = readData
				break

			else :
				resList.append(readData)
				remainLen	-= len( readData)

		if SHUTDOWN :
			__LOG__.Trace( '%s : Shutdown detected while read message body' % cAddress )
			return False

		### 0 : 10 : key : val
		if res != '' :
			keyLen = int( res[:10] )
			key = res[10:10+keyLen]
			val = res[10+keyLen:]
			#print 'debug : keyLen=%s, key=%s, val=%s' % (keyLen, key, val)
			#__LOG__.Trace('debug : keyLen=%s, key=%s, val=%s' % (keyLen, key, val) )

	elif clientPType[cSock] == 6 :
		res = ''
		readData = ''
		while 1 :
			try:
				readData = cSockFD.readline()
				break
			except timeout:
				if SHUTDOWN : break
				else : 
					disconTimeoutCnt += 1
					if disconTimeoutCnt > DISCON_TIMEOUT :
						__LOG__.Trace( '%s : Connection Timeout while read message body' % cAddress )
						return False
					continue

		if readData == '' :
			__LOG__.Trace( '%s : Disconnected at read ascii data' % cAddress )
			return False
		
		if SHUTDOWN :
			__LOG__.Trace( '%s : Shutdown detected while read ascii data' % cAddress )
			return False

		res = readData.strip()
		if res == '' : return True

		dataList = res.split( ',', 4 )
		if len(dataList) == 3 :
			(cmd) = dataList[2]
		elif len(dataList) == 4 :
			(cmd, key) = dataList[2:4]
		elif len(dataList) == 5 :
			(cmd, key, val) = dataList[2:5]

	else :
		__LOG__.Trace( '%s : Invalid PType : PType=[%s]' % (cAddress, clientPType[cSock]) )
		return False

	cmd = cmd.upper()
	if DEBUG : __LOG__.Trace( '%s : cmd=[%s] key=[%s] val=[%s]' % (cAddress, cmd, key, val) )


	if cmd == '#P6' :
		clientPType[cSock] = 6
		sendAnswer( cSock, clientPType[cSock], 'OK ', 'protocol type changed to TYPE6' )
	
	elif cmd == '#P1' :
		clientPType[cSock] = 1
		sendAnswer( cSock, clientPType[cSock], 'OK ', 'protocol type changed to TYPE1' )

	elif cmd == 'PUT' : ### no answer for performance
		dict[key] = val

	elif cmd == 'APP' : ### no answer for performance
		try :
			dict[key] += val
		except :
			dict[key] = val

	elif cmd == 'MPT' or cmd == 'MAP' : ### no answer for performance
		if clientPType[cSock] == 1 :
			tmpValLen = int( val[:10] )
			sIdx = 10

			tmpKey = key
			tmpVal = val[sIdx : sIdx+tmpValLen]

			if cmd == 'MPT' : dict[tmpKey] = tmpVal
			else : 
				try :
					dict[tmpKey] += tmpVal
				except :
					dict[tmpKey] = tmpVal

			#print 'debug : %s -> %s' % (tmpKey, tmpVal)
			sIdx += tmpValLen

			while sIdx < len(val) :
				tmpKeyLen = int( val[sIdx : sIdx+10] )
				sIdx += 10

				tmpKey = val[sIdx : sIdx + tmpKeyLen]
				sIdx += tmpKeyLen

				tmpValLen = int( val[sIdx : sIdx+10] )
				sIdx += 10

				tmpVal = val[sIdx : sIdx + tmpValLen]
				#sIdx += tmpKeyLen
				sIdx += tmpValLen

				if cmd == 'MPT' : dict[tmpKey] = tmpVal
				else : 
					try :
						dict[tmpKey] += tmpVal
					except :
						dict[tmpKey] = tmpVal
				#print 'debug : %s -> %s' % (tmpKey, tmpVal)

		elif clientPType[cSock] == 6 :
			valList = val.split(',')
			tmpKey = key
			tmpVal = valList.pop(0)

			if cmd == 'MPT' : dict[tmpKey] = tmpVal
			else : 
				try :
					dict[tmpKey] += tmpVal
				except :
					dict[tmpKey] = tmpVal

			for i in range( int( len(valList)/2 ) ) :
				tmpKey = valList[ i*2 ]
				tmpVal = valList[ i*2 + 1 ]

				if cmd == 'MPT' : dict[tmpKey] = tmpVal
				else : 
					try :
						dict[tmpKey] += tmpVal
					except :
						dict[tmpKey] = tmpVal

				
	elif cmd == 'GET' :
		if dict.has_key(key) :
			sendAnswer( cSock, clientPType[cSock], 'OK ', dict[key] )
		else :
			sendAnswer( cSock, clientPType[cSock], 'NOK', 'no key exists : [%s]' % key )

	elif cmd == 'MGT' :
		if clientPType[cSock] == 1 :
			dataList = []
			tmpKey = key

			if dict.has_key(tmpKey) :
				dataList.append( '%010d' % len(tmpKey) + tmpKey)
				dataList.append( '%010d' % len(dict[tmpKey]) + dict[tmpKey] )

			sIdx = 0
			while sIdx < len(val) :
				tmpKeyLen = int( val[sIdx : sIdx+10] )
				sIdx += 10

				tmpKey = val[sIdx : sIdx+tmpKeyLen]
				sIdx += tmpKeyLen

				if dict.has_key(tmpKey) :
					dataList.append( '%010d' % len(tmpKey) + tmpKey)
					dataList.append( '%010d' % len(dict[tmpKey]) + dict[tmpKey] )

			sendAnswer( cSock, clientPType[cSock], 'OK ', ''.join(dataList) )

		elif clientPType[cSock] == 6 :
			dataList = []
			keyList = val.split(',')
			keyList.insert(0, key)

			for tmpKey in (keyList) :
				if dict.has_key(tmpKey) :
					tmpVal = dict[tmpKey]
					dataList.append( '%s,%s' % (tmpKey, tmpVal) )

			sendAnswer( cSock, clientPType[cSock], 'OK ', ','.join(dataList) )
				
	elif cmd == 'KYS' :
		keyList = []

		if clientPType[cSock] == 1 :
			for tmp in dict.keys() :
				tmpLen = "%010d" % len(tmp)
				keyList.append(tmpLen)
				keyList.append(tmp)
			sendAnswer( cSock, clientPType[cSock], 'OK ', ''.join(keyList) )

		elif clientPType[cSock] == 6 :
			for tmp in dict.keys() :
				keyList.append(tmp)
			sendAnswer( cSock, clientPType[cSock], 'OK ', ','.join(keyList) )

	elif cmd == 'VLS' :
		valList = []

		if clientPType[cSock] == 1 :
			for tmp in dict.values() :
				tmpLen = "%010d" % len(tmp)
				valList.append(tmpLen)
				valList.append(tmp)
			sendAnswer( cSock, clientPType[cSock], 'OK ', ''.join(valList) )

		elif clientPType[cSock] == 6 :
			for tmp in dict.values() :
				valList.append(tmp)
			sendAnswer( cSock, clientPType[cSock], 'OK ', ','.join(valList) )

	elif cmd == 'ITS' :
		valList = []

		if clientPType[cSock] == 1 :
			for (k,v) in dict.items() :
				kLen = "%010d" % len(k)
				valList.append(kLen)
				valList.append(k)

				vLen = "%010d" % len(v)
				valList.append(vLen)
				valList.append(v)
			sendAnswer( cSock, clientPType[cSock], 'OK ', ''.join(valList) )

		elif clientPType[cSock] == 6 :
			for (k,v) in dict.items() :
				valList.append(k)
				valList.append(v)
			sendAnswer( cSock, clientPType[cSock], 'OK ', ','.join(valList) )

	elif cmd == 'LEN' :
		sendAnswer( cSock, clientPType[cSock], 'OK ', str(len(dict)) )

	elif cmd == 'KIL' :
		__LOG__.Trace( '%s : Caution: cmd=[%s] key=[%s] val=[%s] executed' % (cAddress,cmd,key,val) )
		SHUTDOWN = True
		sendAnswer( cSock, clientPType[cSock], 'OK ', '' )

	elif cmd == 'KEY' :
		if dict.has_key(key) :
			sendAnswer( cSock, clientPType[cSock], 'OK ', key )
		else :
			sendAnswer( cSock, clientPType[cSock], 'NOK', 'no key exists : [%s]' % key )

	elif cmd == 'DEL' :
		if dict.has_key(key) :
			del dict[key]
			sendAnswer( cSock, clientPType[cSock], 'OK ', '' )
		else :
			sendAnswer( cSock, clientPType[cSock], 'NOK', 'no key exists : [%s]' % key )

	elif cmd == 'POP' :
		if dict.has_key(key) :
			sendAnswer( cSock, clientPType[cSock], 'OK ', dict.pop(key) )
		else :
			sendAnswer( cSock, clientPType[cSock], 'NOK', 'no key exists : [%s]' % key )

	elif cmd == 'DPA' or cmd == 'LDA' or cmd == 'DPB' or cmd == 'LDB' or cmd == 'DPK' or cmd == 'LDK' or cmd == 'DCK':
		__LOG__.Trace( '%s : Caution: cmd=[%s] key=[%s] val=[%s] executed' % (cAddress,cmd,key,val) )
		fileName = key
		try :
			if   cmd == 'DPA' : dumpAscii(dict, fileName)
			elif cmd == 'LDA' : loadAscii(dict, fileName)
			elif cmd == 'DPB' : dumpBinary(dict, fileName)
			elif cmd == 'LDB' : loadBinary(dict, fileName)
			elif cmd == 'DPK' : dumpBerkeley(dict, fileName)
			elif cmd == 'LDK' : loadBerkeley(dict, fileName)
			elif cmd == 'DCK' : 
				# DPK + CLR command
				dumpAndClr(dict, fileName)

			sendAnswer( cSock, clientPType[cSock], 'OK ', '' )
		except Exception, err :
			sendAnswer( cSock, clientPType[cSock], 'NOK', err.__str__() )

	elif cmd == 'CLR' :
		__LOG__.Trace( '%s : Caution: cmd=[%s] key=[%s] val=[%s] executed' % (cAddress,cmd,key,val) )
		dict.clear()
		sendAnswer( cSock, clientPType[cSock], 'OK ', '' )

	elif cmd == 'HLP' :
		sendAnswer( cSock, clientPType[cSock], 'OK ', HELP_STR )

	elif cmd == 'CHP' :
		__LOG__.Trace( '%s : Caution: cmd=[%s] key=[%s] val=[%s] executed' % (cAddress,cmd,key,val) )
		sendAnswer( cSock, clientPType[cSock], 'OK ', '' )
		portNum = key
		return int(portNum)
	
	elif cmd == 'BYE' :
		__LOG__.Trace( '%s : Caution: cmd=[%s] key=[%s] val=[%s] executed' % (cAddress, cmd,key,val) )
		return False
	else:
		sendAnswer( cSock, clientPType[cSock], 'NOK', "Command not found.." )


	return True

def mkServer(ip, port) :
	server = socket( AF_INET, SOCK_STREAM )
	server.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1)
	server.bind( (ip, port) )
	server.listen(10)
	return server

def main() :
	global SHUTDOWN

	try :
		### 뒤에 인수가 올경우 : 붙이고, 아닐경우 안붙인다
		### : 에 상관없이 optList 는 튜플의 리스트로 반환된다.
		# optList, args = getopt.getopt(sys.argv[1:], 'p:f:t:w:n:i:')

		optList, args = getopt.getopt(sys.argv[1:], 'p:m:l:')
		if len(args) != 2 : raise Exception
		optDict = {}
		for optKey, optVal in optList : optDict[optKey] = optVal

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

		print 'VERSION: ' + VERSION
		print 'usage : %s [-p] serviceIP servicePort' % (sys.argv[0])
		print '        -p[1] : protocol type, default:6'
		print '        -l /home/eva/log/dict.log : logfile full path '
		print '        -m[bufsize] : socket read buffer size, only use in pType >= 6, default = 0'
		sys.exit()

	### Env ###	
	dict = {}
	servIP = args[0]
	servPort = int(args[1])
	qryCnt = 0
	logPrnCnt = 0

	defaultPType = 6
	if '-p' in optDict : defaultPType = int( optDict['-p'] )
	if '-l' in optDict :
		Log.Init( Log.CRotatingLog( optDict['-l'], 10000000, 2 ) )

	makeFileBufSize = 0
	if '-m' in optDict : makeFileBufSize = int( optDict['-m'] )

	### Socket Create ###
	server = mkServer( servIP, servPort )
	sockList = [server]
	childPType = {}
	childAddr = {}
	childSockFD = {}

	global SHUTDOWN
	global DEBUG

	while SHUTDOWN == False :
		try :
			inputReady,outputReady,exceptReady = select.select(sockList,[],[], 1)
		except Exception, err :
			__LOG__.Exception()
			break

		if len(inputReady) == 0 :
			logPrnCnt += 1
			if logPrnCnt % 10 == 0 :
				__LOG__.Trace( "[%s:%s] ready, connections=[%s], qryCnt=[%s]" 
				% (servIP, servPort, len(sockList), qryCnt) )
			continue

		for sock in inputReady :
			qryCnt += 1
			if qryCnt % 10000 == 0 :
				__LOG__.Trace( "[%s:%s] ready, connections=[%s], qryCnt=[%s]" 
				% (servIP, servPort, len(sockList), qryCnt) )

			if sock == server :
				childSock, addr = server.accept()
				childSock.settimeout(1) # no use for select
				sockList.append(childSock)

				addr = str(addr)
				childAddr[childSock] = addr
				childPType[childSock] = defaultPType
				childSockFD[childSock] = childSock.makefile(bufsize=makeFileBufSize)
				__LOG__.Trace( 'Connected : %s' % addr)

			else :
				try :
					res = False
					try: res = actClient(sock, childSockFD[sock], dict, childAddr[sock], childPType)
					except: res = False
					if res == False :
						sockList.remove(sock)
						sock.close()
						__LOG__.Trace( 'Removed : %s ' % childAddr[sock] )
						del( childPType[sock] )
						del( childAddr[sock] )
						del( childSockFD[sock] )
	
					elif type(res) == int :
						server.close()
						sockList.remove(server)
	
						server = mkServer( servIP, res )
						sockList.append(server)
						servPort = res

				except Exception, err :
					__LOG__.Exception()
					continue

	for sock in sockList :
		try : sock.close()
		except : pass

	__LOG__.Trace( 'All Socket Closed, and Shutdown' )

if __name__ == '__main__' :
	Log.Init(Log.CStandardErrorLog())
	main()
