#!/home/mobigen/bin/python
# -*- coding: cp949 -*-

VERSION = '1.4'
# 	V1.3 (051107) :	memory leak ����
#	V1.4 (051114) : -f option, -b option, log add

import time, os, sys, threading, struct, cPickle, getopt, collections
import SockIPC
from socket import *

class EventQueueClient(SockIPC.SockIPC) :

	def __init__(self, sendPort, **args) :
		args["SendPort"] = sendPort
		SockIPC.SockIPC.__init__(self, **args)

		self.sendPort = '%s/%s' % (self.tmpDir, sendPort)
	
	def appendleft(self, val) :
		self.sendFast( self.sendPort, 'appendleft', '', val )

	def pop(self) :
		port, cmd, key, ans = self.recvFast()

class EventQueueServer(threading.Thread) :

	def __init__(self, sendPort, eqcList, **args) :
		threading.Thread.__init__(self)
		self.eqcList = eqcList
		self.sendPort = sendPort
		self.mode = args['Mode']

		svrsock = socket(AF_INET, SOCK_STREAM)
		svrsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		svrsock.settimeout(1)
		svrsock.bind(('', sendPort))
		svrsock.listen(100)
		self.svrsock = svrsock
		self.shutdown = False

	def run(self) :
		__LOG__.Trace( '+++ EventQueueServer start : sendPort=[%s]'  % (self.sendPort) )
		try :
			while 1 :
				if self.shutdown : break

				try :
					(conn, addr) = self.svrsock.accept()	
				except timeout :
					continue

				eqc = EventQueueChild(conn, Mode=self.mode)
				eqc.daemon = True
				self.eqcList.append(eqc)
				eqc.start()
		except :
			__LOG__.Exception()
	
		try : svrsock.close()
		except : pass

		__LOG__.Trace( '--- EventQueueServer thread closed' )
	
class EventQueueChild(threading.Thread) :

	def __init__(self, conn, **args) :

		threading.Thread.__init__(self)

		self.conn = conn
		self.deq = collections.deque()
		self.shutdown = False
		self.mode = args['Mode']

	def run(self) :
		__LOG__.Trace( '+++ EventQueueChild start : mode=[%s]'  % (self.mode) )

		try :
			while 1 :
				if self.shutdown : break

				if len(self.deq) == 0 :
					time.sleep(0.1)
					continue
				else :
					val = self.deq.pop()

					if self.mode == 'b' :
						valLenBin = struct.pack( '!I', len(val) )
						self.conn.sendall(valLenBin + val)
					else :
						self.conn.sendall(val)

		except :
			__LOG__.Exception()

		try : self.conn.close()
		except : pass

		self.deq = None
		__LOG__.Trace( '--- EventQueueChild thread closed' )
	
class EventQueueDist(threading.Thread, SockIPC.SockIPC) :

	def __init__(self, eqcList, **args) :

		threading.Thread.__init__(self)
		SockIPC.SockIPC.__init__(self, **args)

		self.eqcList = eqcList
		self.shutdown = False

	def actionAppendLeft(self, val) :
		return val

	def run(self) :
		__LOG__.Trace( '+++ EventQueueDist start' )

		try :
			while 1 :
				if self.shutdown : break

				try :
					port, cmd, key, val = self.recvFast()
				#	print '*** debug : ',port,cmd,key,val
				except SockIPC.NoDataException :
					time.sleep(1)
					continue

				if cmd == 'appendleft' :
					val = self.actionAppendLeft(val)

					idx = 0
					while 1 :
						try :
							self.eqcList[idx].deq.appendleft(val)
							idx += 1
						except IndexError :
							break
						except :
							self.eqcList.pop(idx)

				elif cmd == 'kill' :
					break
	
		except :
			__LOG__.Exception()

		SockIPC.SockIPC.close(self)
		__LOG__.Trace( '--- EventQueueDist thread closed' )

def main() :
	try :
		optList, args = getopt.getopt(sys.argv[1:], 'fbdp')
		if len(args) < 2 : raise Exception
		optDict = {}
		for optKey, optVal in optList : optDict[optKey] = optVal
	except :
		print 'usage : %s [-p:NamedPipe] [-f:rmRecvPort] [-b:binMode] recvPort sendPort' % (sys.argv[0])
		sys.exit()

	if '-f' in optDict :
		try : os.unlink( '/tmp/mobigen/%s' % args[0] )
		except : pass

	if '-b' in optDict : mode = 'b'
	else : mode = 'a'

	if '-p' in optDict :
		socketType = "NAMED_PIPE"
	else :
		socketType = "UNIX_DOMAIN_SOCKET"

	recvPort = args[0]
	sendPort = int(args[1])

	__LOG__.Trace( '+++ main start : recvPort=[%s], sendPort=[%s], mode=[%s]' \
		% (recvPort, sendPort, mode) )
	try :
		eqcList = []

		eqs =  EventQueueServer(sendPort, eqcList, Mode=mode)
		eqs.daemon = True
		eqs.start()

		server = EventQueueDist( eqcList, RecvType=socketType, RecvPort=recvPort, Mode=mode )
		server.daemon = True
		server.start()

		while 1 :
			### need to hand signal ###
			time.sleep(1)

		for eqc in eqcList : eqc.shutdown = True
		eqs.shutdown = True
		server.shutdown = True
		time.sleep(3)

	except :
		__LOG__.Exception()

	__LOG__.Trace( '--- main end' )

if __name__ == '__main__' :
	import Mobigen.Common.Log as Log;
	import sys, os, getopt; OPT, ARGS = getopt.getopt(sys.argv[1:], 'dfbp')
	try : LOG_NAME = '~/log/%s.%s.log' % (os.path.basename(sys.argv[0]), ARGS[0])
	except : LOG_NAME = '~/log/%s.log' % (os.path.basename(sys.argv[0]))
	try : OPT.index(('-d', '')); Log.Init()
	except : Log.Init(Log.CRotatingLog(os.path.expanduser(LOG_NAME), 1000000, 10))
	#sys.argv = [sys.argv[0]] + ARGS
	main()
