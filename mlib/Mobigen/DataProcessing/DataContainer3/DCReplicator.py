#!/usr/bin/python

VERSION = '2.0'

import Mobigen.Common.Log as Log; Log.Init()

import sys, getopt, time, os
import DCReceiver
import DataContainer
import struct

import signal
SHUTDOWN = False
def handler(sigNum, frame) :
	global SHUTDOWN
	SHUTDOWN = True
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

class DCReplicator(DCReceiver.DCReceiver) :
	def __init__(self, ip, id, passwd, recvIp, \
			recvPort, rmtDir, localDir, **args) :

		self.db = DataContainer.DataContainer(localDir, **args)
		self.rmtIdxFileName = '%s/dcrecv.info' % localDir

		self.rmtFileTime = "-1"
		self.rmtRecno = 0

		if args.has_key('LastRecordFlag') and args['LastRecordFlag'] : pass
		else : self.loadRmtIdx()

		args['Recno'] = self.rmtRecno

		__LOG__.Trace('* start fileTime=[%s], recno=[%s]' % (self.rmtFileTime, self.rmtRecno) )

		DCReceiver.DCReceiver.__init__(self, ip, id, passwd, recvIp, \
			recvPort, rmtDir, self.rmtFileTime, **args)

	def loadRmtIdx(self) :
		fh = open(self.rmtIdxFileName)
		self.rmtFileTime, self.rmtRecno = fh.readline().split(',')
		self.rmtRecno = int(self.rmtRecno)
		fh.close()
		__LOG__.Trace( 'load : fileTime=[%s], recno=[%s]' % (self.rmtFileTime, self.rmtRecno) )

	def dumpRmtIdx(self) :
		fh = open(self.rmtIdxFileName + '.tmp', 'w')
		fh.write('%s,%s' % (self.rmtFileTime, self.rmtRecno + 1) )
		fh.close()
		os.rename( self.rmtIdxFileName + '.tmp', self.rmtIdxFileName )
		__LOG__.Trace( 'dump : fileTime=[%s], recno=[%s]' % (self.rmtFileTime, self.rmtRecno+1) )
	
	def close(self) :
		DCReceiver.DCReceiver.close(self)
		self.dumpRmtIdx()
		self.db.close()

if __name__ == '__main__' : main()
