#!/home/mobigen/bin/python

VERSION = '2.3'

# VERSION 2.3 by sunghoon : ADD FileTimeInterval Option

try : import psyco; psyco.full()
except : pass

import sys, getopt, time, os
import DCReplicator
import DataContainer
import struct

import signal; SHUTDOWN = False
def handler(sigNum, frame) :
	global SHUTDOWN; SHUTDOWN = True
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

class DCRecv(DCReplicator.DCReplicator) :

	def __init__(self, ip, id, passwd, recvIp, \
		recvPort, rmtDir, localDir, **args) :

		DCReplicator.DCReplicator.__init__(self, ip, id, passwd, recvIp, \
			recvPort, rmtDir, localDir, **args)

		self.localDataCnt = 0

	def action(self, fileTime, msgTime, opt, key, val) :
		self.rmtRecno = key
		self.rmtFileTime = fileTime
		self.db.put( msgTime, val, opt )
	#	__LOG__.Watch((msgTime, opt))

		self.localDataCnt += 1

		if self.localDataCnt % 1000 == 0 :
			self.dumpRmtIdx()
	
def main() :
	global SHUTDOWN

	try :
		optList, args = getopt.getopt(sys.argv[1:], 'k:i:f:t:c:b:v:dl')
		if len(args) < 8 : raise Exception
		optDict = {}
		for optKey, optVal in optList : optDict[optKey] = optVal

	except Exception, err:
		print 'usage : %s [-k<KeepHour>] [-i[FileTimeInterval] [-l] [-f<Filter>] [-t<MsgType>] [-c<SendCMD>] [-b<BufSize>] [-d] [-v<dc version>] msgName ip id passwd recvIp recvPort rmtDir localDir' % (sys.argv[0])
		print '        -d : debug mode'
		sys.exit()
		# if '-l' in optDict : server.load( optDict['-l'] )

	options = {}
	if '-i' in optDict : options['FileTimeInterval'] = int(optDict['-i'])
	if '-k' in optDict : options['KeepHour'] = int(optDict['-k'])
	if '-f' in optDict : options['Filter'] = optDict['-f']
	if '-t' in optDict : options['MsgType'] = optDict['-t']
	if '-c' in optDict : options['SendCMD'] = optDict['-c']
	if '-l' in optDict : options['LastRecordFlag'] = True
	if '-b' in optDict : options['BufSize'] = int(optDict['-b'])
	if '-v' in optDict : options['Version'] = int(optDict['-v'])

	options['Mode'] = 'a' # for DataContainer
	options['MsgName'] = args[0]

	obj = DCRecv(args[1], args[2], args[3], args[4], args[5], \
		args[6], args[7], **options)
	obj.start()
	__LOG__.Trace("+++ DCRecv start")

	while True :
		if SHUTDOWN : break

		if not obj.alive() :
			__LOG__.Trace("*** DCRecv dead detected, so join")
			obj.join()
			obj.close()
			time.sleep(5)
			obj = DCRecv(args[1], args[2], args[3], args[4], args[5], \
				args[6], args[7], **options)
			obj.start()
			__LOG__.Trace("*** DCRecv restart")
			__LOG__.Trace("*** DCRecv restart")
			__LOG__.Trace("*** DCRecv restart")
			__LOG__.Trace("*** DCRecv restart")
			__LOG__.Trace("*** DCRecv restart")

		time.sleep(1)

	obj.close()
	__LOG__.Trace("--- DCRecv shutdown")

if __name__ == '__main__' :
	import Mobigen.Common.Log as Log;
	import sys, os, getopt; OPT, ARGS = getopt.getopt(sys.argv[1:], 'k:i:f:t:c:b:dl')
	try : LOG_NAME = '~/log/%s.%s.log' % (os.path.basename(sys.argv[0]), ARGS[0])
	except : LOG_NAME = '~/log/%s.log' % (os.path.basename(sys.argv[0]))
	try : OPT.index(('-d', '')); Log.Init()
	except : Log.Init(Log.CRotatingLog(os.path.expanduser(LOG_NAME), 1000000, 10))
	# sys.argv = [sys.argv[0]] + ARGS
	main()
