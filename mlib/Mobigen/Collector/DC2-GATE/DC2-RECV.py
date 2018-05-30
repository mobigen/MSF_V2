#!/bin/env python
# coding: iso-8859-1

try : import psyco; psyco.full()
except : pass

import sys
import getopt
import time
import os
import struct

import Mobigen.Common.Log as Log; Log.Init()
import Mobigen.DataProcessing.DataContainer2.DCReplicator as DCReplicator

import signal; SHUTDOWN = False
def handler(sigNum, frame) :
	global SHUTDOWN; SHUTDOWN = True
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

class DCRecv(DCReplicator.DCReplicator) :
	def __init__(self, ip, id, passwd, rmtDir, recvIp, recvPort, localDir, **args) :

		DCReplicator.DCReplicator.__init__(self, ip, id, passwd, recvIp, recvPort, rmtDir, localDir, **args)
		self.localDataCnt = 0

	def action(self, fileTime, msgTime, opt, key, val) :
		self.rmtRecno = key
		self.rmtFileTime = fileTime
		self.db.put( msgTime, val, opt )
	#	__LOG__.Watch((msgTime, opt))

		self.localDataCnt += 1

		if self.localDataCnt % 1000 == 0 :
			self.dumpRmtIdx()

def Usage() :
	print 'Usage : %s [option] rmtIP rmtID rmtPass rmtDir recvIP recvPort recvDir' % (sys.argv[0])
	print 
	print 'option :'
	print '  -l, --last         last data'
	print '  -b, --buffer       buffer size'
	print '  -f, --filter       filter pattern string'
	print '  -d, --debug        debug mode'
	print '  -s, --sendcmd      send process'
	print '  -v[2|3]     dc version default 2'
	sys.exit()
	
def Main() :
	global SHUTDOWN

	try : opts, args = getopt.getopt(sys.argv[1:], 'b:dlf:v:s:', ["buffer=", "filter=", "last", "debug", "sendcmd="])
	except : Usage()
	if len(args) !=7 : Usage()

	try : os.makedirs(args[6])
	except : pass

	options = {}
	options['Mode'] = 'a' # for DataContainer

	for o, v in opts:
		if o in ('-f', '--filter') : options['Filter'] = v
		if o in ('-l', '--last') : options['LastRecordFlag'] = True
		if o in ('-b', '--buffer') : options['BufSize'] = int(v)
		if o in ('-d', '--debug') : options['-d'] = None
		if o in ('-s', '--sendcmd') : options['SendCMD'] = v
		if o in ('-v') : options['Version'] = int( v )

	obj = DCRecv(args[0], args[1], args[2], args[3], args[4], args[5], args[6], **options)
	__LOG__.Trace("DCRecv start")
	obj.start()
	time.sleep(10) # obj  Á¤»ó¼öÇàÀÌÀü¿¡ While·Î µé¾î°¡´Â ½Ã°£Â÷ ¼³Á¤  

	while True :
		if SHUTDOWN : break

		if obj.alive() == False:
			__LOG__.Trace("DCRecv dead detected, so join")
			obj.join()
			obj.close()
			for i in range(10) :
				__LOG__.Trace("sleep")
				time.sleep(1)

			try :
				obj = DCRecv(args[0], args[1], args[2], args[3], args[4], args[5], args[6], **options)
				obj.start()
				__LOG__.Trace("*** DCRecv restart")
			except :
				__LOG__.Exception()

		time.sleep(2)

	obj.close()
	__LOG__.Trace("--- DCRecv shutdown")

if __name__ == '__main__' :
	Log.Init(Log.CStandardErrorLog())
	Main()
