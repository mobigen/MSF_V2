#!/usr/bin/python
# -*- coding: cp949 -*-

# should do dump lock code and test

VERSION = '1.6'

try : import psyco; psyco.full()
except : pass

import time, os, sys, threading, struct, cPickle, getopt, collections
import SockIPC

import signal
SHUTDOWN = False
def handler(sigNum, frame) :
	global SHUTDOWN
	SHUTDOWN = True
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

class SockDictClient(SockIPC.SockIPC) :

	def __init__(self, sendPort, **args) :
		SockIPC.SockIPC.__init__(self, **args)

		self.sendPort = '%s/%s' % (self.tmpDir, sendPort)

	def put(self, key, val) :
		self.sendFast( self.sendPort, 'put', str(key), val )

	def get(self, key) :
		self.sendFast( self.sendPort, 'get', str(key), '' )
		port, cmd, key, ans = self.recvFast()

		if ans == '' : raise Exception, 'no data to read'
		else : return ans
	
	def pop(self, key) :
		self.sendFast( self.sendPort, 'pop', str(key), '' )
		port, cmd, key, ans = self.recvFast()

		if ans == '' : raise Exception, 'no data to read'
		else : return ans
	
	def keys(self) :
		self.sendFast( self.sendPort, 'keys','', '' )

		tmpList = []
		while 1 :
			port, cmd, key, ans = self.recvFast()
			if key == '<begin>' : continue
			if key == '<end>' : break

			tmpList.append(key)
		return tmpList
	
	def has_key(self, key) :
		self.sendFast( self.sendPort, 'has_key', str(key), '' )
		port, cmd, key, ans = self.recvFast()

		if ans == 'True' : return True
		else : return False
	
	def del_key(self, key) :
		self.sendFast( self.sendPort, 'del_key', str(key), '' )

	def clear(self) :
		self.sendFast( self.sendPort, 'clear', '', '' )

	def dump(self, fileName) :
		if fileName :
			self.sendFast( self.sendPort, 'dump', fileName, '' )

	def load(self, fileName) :
		if fileName :
			self.sendFast( self.sendPort, 'load', fileName, '' )

	def kill(self) :
		self.sendFast( self.sendPort, 'kill', '', '' )

class SockDict(threading.Thread, SockIPC.SockIPC) :

	def __init__(self, **args) :

		threading.Thread.__init__(self)
		SockIPC.SockIPC.__init__(self, **args)

		self.dict = {}
		self.dumpLock = True

	def run(self) :
		global SHUTDOWN
			
		while 1 :
			try :
				if SHUTDOWN : break

				self.dumpLock = False
				port, cmd, key, val = self.recvFast()
				self.dumpLock = True
				# print '*** debug : ',port,cmd,key,val
	
				if cmd == 'put' :
					self.dict[key] = val
	
				elif cmd == 'get' :
					if self.dict.has_key(key) :
						self.sendFast( port, cmd, key, self.dict[key] )
					else :
						self.sendFast( port, cmd, key, '' )
	
				elif cmd == 'keys' :
					self.sendFast( port, cmd, '<begin>', '' )
	
					for line in self.dict.keys() :
						self.sendFast( port, cmd, line, '' )
	
					self.sendFast( port, cmd, '<end>', '' )
	
				elif cmd == 'kill' :
					SHUTDOWN = True
					break
	
				elif cmd == 'has_key' :
					if self.dict.has_key(key) :
						self.sendFast( port, cmd, key, 'True' )
					else :
						self.sendFast( port, cmd, key, 'False' )
	
				elif cmd == 'del_key' :
					if self.dict.has_key(key) :
						del self.dict[key]
	
				elif cmd == 'pop' :
					if self.dict.has_key(key) :
						self.sendFast( port, cmd, key, self.dict.pop(key) )
					else :
						self.sendFast( port, cmd, key, '' )
	
				elif cmd == 'dump' :
					self.dump(self.dict, key)

				elif cmd == 'load' :
					self.dict = self.load(key)
				
				elif cmd == 'clear' :
					self.dict = {}

			except Exception, err :
				__LOG__.Exception()

		self.close()

class SockQueueClient(SockIPC.SockIPC) :

	def __init__(self, sendPort, **args) :
		SockIPC.SockIPC.__init__(self, **args)

		self.sendPort = '%s/%s' % (self.tmpDir, sendPort)
	
	def appendleft(self, val) :
		self.sendFast( self.sendPort, 'appendleft', '', val )

	def append(self, val) :
		self.sendFast( self.sendPort, 'append', '', val )

	def clear(self) :
		self.sendFast( self.sendPort, 'clear', '', '' )

	def kill(self) :
		self.sendFast( self.sendPort, 'kill', '', '' )

	def pop(self) :
		self.sendFast( self.sendPort, 'pop', '', '' )
		port, cmd, key, ans = self.recvFast()

		if ans == '' : raise Exception, 'no data to read'
		else : return ans

	def popleft(self) :
		self.sendFast( self.sendPort, 'popleft', '', '' )
		port, cmd, key, ans = self.recvFast()

		if ans == '' : raise Exception, 'no data to read'
		else : return ans

	def len(self) :
		self.sendFast( self.sendPort, 'len', '', '' )
		port, cmd, key, ans = self.recvFast()
		return ans

	def peep(self, key) :
		key = str(key)
		self.sendFast( self.sendPort, 'peep', key, '' )
		port, cmd, key, ans = self.recvFast()

		if ans == '' : raise Exception, 'no data to read'
		else : return ans
	
	def dump(self, fileName) :
		print 'debug : %s dump 1' % fileName
		if fileName :
			self.sendFast( self.sendPort, 'dump', fileName, '' )

	def load(self, fileName) :
		if fileName :
			self.sendFast( self.sendPort, 'load', fileName, '' )

	def __del__(self) :
		os.unlink(self.recvPort)

class SockQueue(threading.Thread, SockIPC.SockIPC) :

	def __init__(self, **args) :

		threading.Thread.__init__(self)
		SockIPC.SockIPC.__init__(self, **args)

		self.deq = collections.deque()

	def run(self) :
		global SHUTDOWN
		
		while 1 :
			try :
				port, cmd, key, val = self.recvFast()
				#print '*** debug : ',port,cmd,key,val
	
				if cmd == 'appendleft' :
					self.deq.appendleft(val)
	
				elif cmd == 'append' :
					self.deq.append(val)
	
				elif cmd == 'clear' :
					self.deq.clear()
	
				elif cmd == 'kill' :
					SHUTDOWN = True
					break
	
				elif cmd == 'pop' :
					if len(self.deq) == 0 : ans = ''
					else : ans = self.deq.pop()
					self.sendFast( port, cmd, '', ans )
	
				elif cmd == 'popleft' :
					if len(self.deq) == 0 : ans = ''
					else : ans = self.deq.popleft()
					self.sendFast( port, cmd, '', ans )
	
				elif cmd == 'len' :
					ans = str( len(self.deq) )
					self.sendFast( port, cmd, '', ans )
					
				elif cmd == 'peep' : # peep
					if len(self.deq) > int(key) : ans = self.deq[ int(key) ]
					else : ans = ''
					self.sendFast( port, cmd, key, ans )

				elif cmd == 'dump' :
					self.dump(self.deq, key)

				elif cmd == 'load' :
					self.deq = self.load(key)

			except Exception, err:
				__LOG__.Exception()

		self.close()

def main() :
	global SHUTDOWN
	try :
		optList, args = getopt.getopt(sys.argv[1:], 'dp:l:')
		if len(args) < 2 : raise Exception
		optDict = {}
		for optKey, optVal in optList : optDict[optKey] = optVal
	except :
		print 'usage : %s [-pdumpFileName] [-lloadFileName] port d|q' % (sys.argv[0])
		sys.exit()

	server = None
	if args[1] == 'd' :
		server = SockDict( RecvPort=args[0], SendFailIGN=True )
		print 'dict mode'
	else :
		server = SockQueue( RecvPort=args[0], SendFailIGN=True )
		print 'queue mode'

	if '-l' in optDict :
		try :
			server.load( optDict['-l'] )
			print 'load completed'
		except :
			print 'load fail'

	server.start()

	while 1 :
		if SHUTDOWN : break
		time.sleep(1)

	if '-p' in optDict :
		server.dump(optDict['-p'])
	server.join()

if __name__ == '__main__' :
    import Mobigen.Common.Log as Log;
    import sys, os, getopt; OPT, ARGS = getopt.getopt(sys.argv[1:], 'd')
    try : LOG_NAME = '~/log/%s.%s.log' % (os.path.basename(sys.argv[0]), ARGS[0])
    except : LOG_NAME = '~/log/%s.log' % (os.path.basename(sys.argv[0]))
    try : OPT.index(('-d', '')); Log.Init()
    except : Log.Init(Log.CRotatingLog(os.path.expanduser(LOG_NAME), 1000000, 10))
    main()

