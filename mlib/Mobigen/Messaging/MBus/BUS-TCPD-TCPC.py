#!/usr/bin/python
# -*- coding: UTF-8 -*-

VERSION = "V2.3.2"

#---------------------------------------------------------------
# version | date : writer : description
#---------------------------------------------------------------
# V1.0    | 061203 : tesse : begin
# V2.0    | 070423 : tesse : final
# V2.1    | 070523 : jjiny : Add Function 'STI' (Single Noti)
#                  		   : notification value don't strip
#				   		   : putNoti() , add (rsv,cmd) - loopback
# V2.2    | 070619 : jjiny : readData() function, socket nonblock 
# V2.3    | 070621 : jjiny : deregister, self.sf.close() 
# V2.4    | 080103 : eek   : host deny 
#---------------------------------------------------------------

import Mobigen.Common.Log as Log; Log.Init()
#import Mobigen.Common.SFProtocol.SFProtocol as sfp
import Mobigen2.Common.SFProtocol.SFProtocol as sfp

import time, sys, select, getopt
from socket import *

import signal,exceptions
##### psyco #####
try:
    import psyco
    psyco.full()
except ImportError:
    pass
#################

SHUTDOWN = False

def shutdown(sigNum=0, frame=0) :
	global SHUTDOWN
	__LOG__.Trace( 'signal detected' )
	SHUTDOWN = True

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGHUP, shutdown)

inSockList = None
sockConnectorHash = None

class Connector :
	
	def __init__(self, cSock, addr, key1Hash, key2Hash, keyBothHash, conList, **opts) :
		self.sf = sfp.SFProtocol( sfp.SFP_CH_T, **opts)
		self.sf.setFD(cSock)

		self.cSock = cSock
		self.addr = addr
		self.key1Hash = key1Hash
		self.key2Hash = key2Hash
		self.keyBothHash = keyBothHash
		self.heartBeatSec = 0
		self.startSec = time.time()

		self.deregiBothList = []
		self.deregiKey1List = []
		self.deregiKey2List = []

		self.conList = conList

	def ansNOK(self, reason) :
		self.sf.write( '#E', 'NOK', reason + '\n' )

	def ansOK(self, reason) :
		self.sf.write( '', 'OK', reason + '\n' )

	def ansHeart(self) :
		aliveSec = time.time() - self.startSec

		if aliveSec >= self.heartBeatSec :
			try :
				self.sf.write( '', 'NOP', 'heart beat\n' )
				__LOG__.Trace('%s : send heart beat, [%s] sec' % (self.addr, aliveSec) )

			except Exception, err :
				__LOG__.Exception()
				__LOG__.Trace('%s : SFPDiscon'%(self.addr) )
				self.deregister()

			self.startSec = time.time()

	def regiNotiKeyList(self, notiKeyList) :
		if len(notiKeyList) % 2 != 0 :
			err = 'invalid register format, msg=[%s]' % str( notiKeyList)
			raise Exception, err

		for i in range( len(notiKeyList) / 2 ) :
			key1 = notiKeyList[i*2].strip()
			key2 = notiKeyList[i*2 + 1].strip()

			if key1 == '' or key2 == '' :
				err = 'empty key'
				raise Exception, err

			if key1 == '*' and key2 == '*' :
				self.regiNotiKey( self.keyBothHash, '*,*', self.deregiBothList )

			elif key1 == '*' :
				self.regiNotiKey( self.key2Hash, key2, self.deregiKey2List )

			elif key2 == '*' :
				self.regiNotiKey( self.key1Hash, key1, self.deregiKey1List )

			else :
				self.regiNotiKey( self.keyBothHash, '%s,%s' % (key1, key2), self.deregiBothList )

	### add self reference to notiKeyHash
	def regiNotiKey(self, notiKeyHash, notiKey, deregiKeyList) :
		if not notiKeyHash.has_key(notiKey) : notiKeyHash[notiKey] = []

		try :
			notiKeyHash[notiKey].index(self)
			__LOG__.Trace( '%s : regiNoti, %s, already registered' % (self.addr, notiKey) )
		except :
			notiKeyHash[notiKey].append(self)
			__LOG__.Trace( '%s : regiNoti, %s, OK' % (self.addr, notiKey) )

		try :
			deregiKeyList.index(notiKey)
		except :
			deregiKeyList.append(notiKey)

	### remove self reference from notiKeyHash
	def deregiNotiKey(self, notiKeyHash, deregiKeyList ) :
		for notiKey in deregiKeyList :
			if notiKeyHash.has_key(notiKey) :

				connectors = notiKeyHash[notiKey]

				for conn in connectors :
					__LOG__.Trace( '%s : deregiNoti: all [%s]' % (notiKey, conn.sf.sock.fileno()  ) )

				try : 
					notiKeyHash[notiKey].remove(self)
					__LOG__.Trace( '%s : deregiNoti : self remove [%s] fd:[%d]' % (self.addr, notiKey, self.sf.sock.fileno() ) )
				except : pass

	
				if notiKey != '*,*' and len( notiKeyHash[notiKey] ) == 0 :
					try : del( notiKeyHash[notiKey] )
					except : pass
					__LOG__.Trace( '%s : deregiNoti and pop key, [%s]' % (self.addr, notiKey) )

	def deregister(self, key=None) :

		try : self.sf.flush()
		except : pass

		if not key:
			# 종료되는 경우

			self.deregiNotiKey( self.key1Hash, self.deregiKey1List )
			self.deregiNotiKey( self.key2Hash, self.deregiKey2List )
			self.deregiNotiKey( self.keyBothHash, self.deregiBothList )
			self.deregiNotiKey( self.keyBothHash, ['*,*'] )

			try : 
				self.sf.close()
			except : 
				__LOG__.Exception()

			try : self.conList.remove(self)
			except : pass

			__LOG__.Trace("%s : deregister completed"%(self.addr) )
		else:

			# DEREG 함수 구현 

			deRegiKeyList = None
			try :
				deRegiKeyList = key.split(',')
			except :
				deRegiKeyList = None
				pass

			if not deRegiKeyList or len(deRegiKeyList) != 2: 
				self.ansNOK('deregistration error[%s]' % key)
				return

			k1 = deRegiKeyList[ 0 ].strip()
			k2 = deRegiKeyList[ 1 ].strip()

			deregiKey = []
			if k1 == "*" and k2 == "*":
				deregiKey.append("*,*")
			if k1 == "*":
				deregiKey.append( k2 )
				self.deregiNotiKey( self.key2Hash, deregiKey )
			elif k2 == "*":
				deregiKey.append( k1 )
				self.deregiNotiKey( self.key1Hash, deregiKey )
			else:
				deregiKey.append( "%s,%s" % (k1, k2))
				self.deregiNotiKey( self.keyBothHash, deregiKey )

			self.ansOK('deregistration completed')

	def register(self, msg) :
		try :
			regiKeyList = msg.split(',')
			self.heartBeatSec = int( regiKeyList.pop(0) )
		except :
			# self.ansNOK('bad heart beat sec value')
			# continue
			pass # make default self.heartBeatSec 0

		self.regiNotiKeyList( regiKeyList )
		self.ansOK('registration completed')

		try :
			self.conList.index(self)
		except :
			self.conList.append(self)

def putNoti(rsv, cmd, connectorList, notiKey, val) :
	for connector in connectorList :

		#msg = '%s,%s\n' % (notiKey, val)
		msg = '%s,%s' % (notiKey, val)
		#__LOG__.Trace('fd:[%d] - %s ' % (connector.sf.sock.fileno(), notiKey ))

		try :
			#connector.sf.sock.settimeout(None)
			#connector.sf.sock.settimeout(0)

			connector.sf.sock.settimeout(10)
			connector.sf.write( rsv, cmd, msg )
			connector.sf.sock.settimeout(None)
		except  timeout, e:
			__LOG__.Trace('sock timeout ')

			sock = connector.cSock

			global inSockList, sockConnectorHash
			
			try : inSockList.remove(sock)
			except : pass

			try : del(sockConnectorHash[sock])
			except : pass

			connector.deregister()

			pass
		except sfp.SFPBadChType:
			connector.sf.sock.settimeout(None)
		except Exception:
			__LOG__.Exception()
			connector.sf.sock.settimeout(None)
			continue


def readData(sock, key1Hash, key2Hash, keyBothHash, isBuf=False ) :

	#{

	global sockConnectorHash
	connector = sockConnectorHash[sock]

	try :
		connector.sf.sock.settimeout(0.0001)
		
		if isBuf :
	
			#__LOG__.Trace('readBuf')
			(pt, rsv, cmd, msg) = connector.sf.readBuf()
		else:
			#__LOG__.Trace('read')
			(pt, rsv, cmd, msg) = connector.sf.read()

		__LOG__.Trace('client input : %s %s %s [%s]' % (pt, rsv, cmd, msg[:10]))
		connector.sf.sock.settimeout(None)

	except timeout, e:
		#connector.sf.sock.settimeout(None)
		__LOG__.Trace('sock timeout ')
		return False

	except sfp.SFPBadPType, err:
		connector.sf.sock.settimeout(None)
		__LOG__.Exception()
		return True
	except sfp.SFPBadFormat	, err:
		__LOG__.Exception()
		connector.sf.sock.settimeout(None)
		return True

	except sfp.SFPDiscon :
		__LOG__.Exception()
		raise sfp.SFPDiscon
	
	if cmd == 'REG' :
		connector.register( msg )
	elif cmd == 'DRG' :
		connector.deregister( msg )
	elif cmd == 'NOP' : # heartBeat 070707
		pass
	elif cmd == 'DIS' : # Key Display 070619
		__LOG__.Trace( "DIS total:[%d] ==================================" % \
			(len(sockConnectorHash) ) )

		for keys, value in key1Hash.iteritems() : # keys, value : connector list
			__LOG__.Trace( "DIS [key1   ]	[%s]#[%s]" % (keys, len(value) ) )
					
		for keys, value in key2Hash.iteritems() :
			__LOG__.Trace( "DIS [key2   ]	[%s]#[%s]" % (keys, len(value) ) )
						
		for keys, value in keyBothHash.iteritems() :
			__LOG__.Trace( "DIS [keyBoth]	[%s]#[%s]" % (keys, len(value) ) )


	elif cmd == 'NTI' or cmd == 'STI' :

		tmpList = []

		if cmd == 'NTI' :
			tmpList = msg.split(',')
		elif cmd == 'STI': # Single Noti
			tmpList = msg.split(',', 2)

		#__LOG__.Trace('notification = %s [%s]' % (cmd , msg) )

		### -- DEBUG
		#__LOG__.Trace( "DIS total:[%d] ==================================" % \
		#	(len(sockConnectorHash) ) )

		#for keys, value in key1Hash.iteritems() :# keys, value : connector list
		#	__LOG__.Trace( "DIS [key1   ]	[%s]#[%s]" % (keys, len(value) ) )
#
#		for keys, value in key2Hash.iteritems() :
#			__LOG__.Trace( "DIS [key2   ]	[%s]#[%s]" % (keys, len(value) ) )
#						
##		for keys, value in keyBothHash.iteritems() :
#			__LOG__.Trace( "DIS [keyBoth]	[%s]#[%s]" % (keys, len(value) ) )

	
		if len(tmpList) % 3 == 0 :
		#{
			for i in range( len(tmpList)/3 ) :
				key1 = tmpList[i*3].strip()
				key2 = tmpList[i*3 + 1].strip()
				bothKey = '%s,%s' % (key1, key2)

				#notiVal = tmpList[i*3 + 2].strip()
				#notiVal = tmpList[i*3 + 2].strip('\n')
				notiVal = tmpList[i*3 + 2]
	
				if key1 == '*' or key2 == '*' :
					__LOG__.Trace('bad notification format = %s [%s]' % \
						(cmd , msg) )
					continue
	
				if key1 != '' and key1Hash.has_key(key1) :
					putNoti( rsv, cmd, key1Hash[key1], bothKey, notiVal )
					#__LOG__.Trace('noti key1Key = %s [%s]' % (key1 , notiVal) )

				if key2 != '' and key2Hash.has_key(key2) :
					putNoti( rsv, cmd, key2Hash[key2], bothKey, notiVal )
					#__LOG__.Trace('noti key2Key = %s [%s]' % (key2 , notiVal) )
	
				if bothKey != ',' and keyBothHash.has_key(bothKey) :
					putNoti( rsv, cmd, keyBothHash[bothKey], bothKey, notiVal )
					#__LOG__.Trace('noti bothKey = %s [%s] ' % (bothKey , notiVal) )

				if len( keyBothHash['*,*'] ) > 0 :
					putNoti( rsv, cmd, keyBothHash['*,*'], bothKey, notiVal )
	
		#}
		else :
		#{
			__LOG__.Trace('bad format = %s [%s]' % (cmd , msg[:10]) )
			return True

			##continue
		#}
	
	else :
		err = 'invalid command [%s]' % cmd
		raise Exception, err
	#}

	return True

def readDenyFile(fileName, denyHash):
	""" 접속 거부 IP """

	try:
		f = open(fileName)

		for line in f.readlines():
			line = line.strip()
			denyHash[ line ] = 1

		f.close()
	except:
		pass


def main() :
	global SHUTDOWN

	try :
		optStr = sfp.getOptStr()
		optStr += "f:"
		optList, args = getopt.getopt(sys.argv[1:], optStr, ["deny=",])
		if len(args) != 2 : raise Exception
		opts = {}
		for optKey, optVal in optList : opts[optKey] = optVal
	except :
		print 'VERSION: %s' % VERSION
		print 'usage : %s [-options] servIP servPort' % (sys.argv[0])
		sfp.prnOpt()
		print "        -f[logfilePath]  : logfilePath"
		print "        --deny=host.deny  : host deny ip"
		sys.exit()

	key1Hash = {}
	key2Hash = {}
	keyBothHash = { '*,*':[] }

	if opts.has_key("-f"):
		# -f logfilePath 
		fileName = opts[ "-f" ]
		Log.Init( Log.CRotatingLog( fileName, 10000000, 3 ))
	else:
		# opts
		Log.Init(Log.CStandardErrorLog())


	pType = 1 # default protocol type 1
	if opts.has_key("-p"):
		try: pType = int(opts[ "-p" ]) ;
		except: pType = 1


	denyIpHash = {}
	if opts.has_key("--deny"):
		fileName = opts[ "--deny" ]
		readDenyFile(fileName, denyIpHash)

	servIP = args[0]
	servPort = int(args[1])

	servsock = socket( AF_INET, SOCK_STREAM )
	servsock.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1)
	servsock.bind( ('', int(servPort)) )
	servsock.listen(10)

	#servsock.setblocking(False) # non block

	global inSockList, sockConnectorHash

	inSockList = [servsock]
	sockConnectorHash = {}
	conList = []

	__LOG__.Trace( "[%s:%s] Start ---" % (servIP, servPort) )

	startSec = time.time()
	qryCnt = 1
	while SHUTDOWN == False :
		try : #{
			try :
				inputReady,outputReady,exceptReady = \
					select.select(inSockList,[],[], 0.1)
			except Exception, err :
				__LOG__.Exception()
				raise sfp.SFPDiscon, err

					
			if len(inputReady) == 0 :
				aliveSec = time.time() - startSec
				
				if aliveSec >= 60 :
					__LOG__.Trace( "[%s:%s] ready, conList=[%s], qryCnt=[%s]" \
					% (servIP, servPort, len(conList), qryCnt) )
					startSec = time.time()

				for th in conList :
					if th.heartBeatSec != 0 :
						th.ansHeart()
	
			if qryCnt % 100 == 0 :
				for th in conList :
					if th.heartBeatSec != 0 :
						th.ansHeart()

				if qryCnt % 10000 == 0 :
					__LOG__.Trace( "[%s:%s] ready, conList=[%s], qryCnt=[%s]" \
					% (servIP, servPort, len(conList), qryCnt) )

			idx = 0
			for sock in inputReady : #{

				idx += 1
				__LOG__.Trace("inputReady, [%d/%d]" % ( idx,len(inputReady) ) )

				qryCnt += 1

				if sock == servsock :
					cSock, addr = servsock.accept()

					# 접속 거부
					if denyIpHash.has_key( addr[0] ) :
						cSock.close()
						__LOG__.Trace( "deny ip [%s]" % addr[0] )
						continue

					inSockList.append(cSock)

					addr = str(addr)
					connector = Connector(cSock, addr, key1Hash, key2Hash, keyBothHash, conList, **opts)
					sockConnectorHash[cSock] = connector

					__LOG__.Trace("connected, addr=%s" % addr )

				else :
					connector = sockConnectorHash[sock]


					try : # try

						idx = 0
						readData(sock, key1Hash, key2Hash, keyBothHash )

						while pType == 6:
							if (not readData(sock, key1Hash, key2Hash, keyBothHash, True )):
								__LOG__.Trace("+++++ readData END TIMEOUT ++++++ %s,fd:[%d]" % ( addr,sock.fileno() ) )
								break

							idx += 1

							if idx >= 100 : 
								__LOG__.Trace("+++++ readData END 100 ++++++ %s,fd:[%d]" % ( addr,sock.fileno() ) )
				
								break

					except Exception, err :

						__LOG__.Exception()

						try : inSockList.remove(sock)
						except : pass

						try : del(sockConnectorHash[sock])
						except : pass

						connector.deregister()
						sock.close()

						continue
			#} for
		#} try
		except Exception, err :
			__LOG__.Exception()
			__LOG__.Trace('interrupted when accept')
			SHUTDOWN = True
			break

	__LOG__.Trace("END")

if __name__ == '__main__' :
	Log.Init(Log.CStandardErrorLog())
	#   Log.Init(Log.CDummyLog())
	main()
