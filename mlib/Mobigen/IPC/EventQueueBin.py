#!/usr/bin/python
# -*- coding: cp949 -*-

VERSION = '1.2'

import signal
SHUTDOWN = False
def handler(sigNum, frame) :
	global SHUTDOWN
	SHUTDOWN = True
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

import time, os, sys, threading, struct, cPickle, getopt, collections, struct, types 
import SockIPC
from socket import *

class EventQueueClient(SockIPC.SockIPC) :

	def __init__(self, sendPort, **args) :
		SockIPC.SockIPC.__init__(self, **args)

		if(type(sendPort)==types.DictType) :
			args = sendPort
			sendPort = args['SendPort']

		self.sendPort = '%s/%s' % (self.tmpDir, sendPort)
	
	def appendleft(self, val) :
		self.sendFast( self.sendPort, 'appendleft', '', val )

	def pop(self) :
		port, cmd, key, ans = self.recvFast()

class EventQueueServer(threading.Thread) :

	def __init__(self, sendPort, eqcList, **args) :
		threading.Thread.__init__(self)
		self.eqcList = eqcList

		svrsock = socket(AF_INET, SOCK_STREAM)
		svrsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		svrsock.bind(('', sendPort))
		svrsock.listen(100)
		self.svrsock = svrsock

	def run(self) :
		while 1 :
			(conn, addr) = self.svrsock.accept()	
			eqc = EventQueueChild(conn)
			eqc.daemon = True
			self.eqcList.append(eqc)
			eqc.start()
	
	def close(self) :
		try : svrsock.close()
		except : pass
		print 'EventQueueServer thread closed'

class EventQueueChild(threading.Thread) :

	def __init__(self, conn, **args) :

		threading.Thread.__init__(self)

		self.conn = conn
		self.deq = collections.deque()

	def run(self) :
		try :
			while 1 :
				if len(self.deq) == 0 :
					time.sleep(0.01)
					continue
				else :
					val = self.deq.pop()
					valLenBin = struct.pack( '!I', len(val) )
					self.conn.sendall(valLenBin + val)

		except Exception, err:
			print err

		try : self.conn.close()
		except : pass
		self.conn = None

class EventQueueDist(threading.Thread, SockIPC.SockIPC) :

	def __init__(self, sendPort, **args) :

		threading.Thread.__init__(self)
		SockIPC.SockIPC.__init__(self, **args)

		self.eqcList = []
		self.eqs =  EventQueueServer(sendPort, self.eqcList, **args)
		self.eqs.daemon = True

	def actionAppendLeft(self, val) :
		return val

	def run(self) :
		self.eqs.start()

		try :
			while 1 :
				port, cmd, key, val = self.recvFast()
				# print '*** debug : ',port,cmd,key,val
	
				if cmd == 'appendleft' :
					val = self.actionAppendLeft(val)

					#tmpList = []
					for eqc in self.eqcList :
						if eqc.conn :
							eqc.deq.appendleft(val)
					#		tmpList.append(eqc)

					#self.eqcList = tmpList

				elif cmd == 'kill' :
					break
	
		except Exception, err:
			print err
		self.close()
	
	def close(self) :
		for eqc in self.eqcList :
			eqc.close()
		SockIPC.SockIPC.close(self)
		self.eqs.close()

		print 'EventQueueDist thread closed'

def main() :
	global SHUTDOWN

	try :
		optList, args = getopt.getopt(sys.argv[1:], 'd:l:')
		if len(args) < 2 : raise Exception
		optDict = {}
		for optKey, optVal in optList : optDict[optKey] = optVal
	except :
		print 'usage : %s [-ddumpFileName] [-lloadFileName] recvPort sendPort' % (sys.argv[0])
		sys.exit()

	server = EventQueueDist( int(args[1]), RecvPort=args[0] )
	server.daemon = True
	server.start()

	while 1 :
		if SHUTDOWN : break
		time.sleep(1)

	server.close()

if __name__ == "__main__": main()
