#!/usr/bin/python

#---------------------------------------------------------------------
# version | date : writer : description
#---------+-----------------------------------------------------------
# V2.0    | 070424 : cdssw : final
#---------------------------------------------------------------------

import Mobigen.Common.Log as Log; Log.Init()
import Mobigen.Common.SFProtocol.SFProtocol as sfp

import os, sys, getopt
from socket import *

import signal
SHUTDOWN = False

def shutdown(sigNum=0, frame=0) :
	global SHUTDOWN
	SHUTDOWN = True

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGHUP, shutdown)

def main() :
	global SHUTDOWN

	try :
		optStr = sfp.getOptStr()
		optList, args = getopt.getopt(sys.argv[1:], optStr+'t:')
		if len(args) != 2 : raise Exception
		opts = {}
		for optKey, optVal in optList : opts[optKey] = optVal
	except :
		print 'usage : %s [-options] servIp servPort' % (sys.argv[0])
		sfp.prnOpt()
		sys.exit()

	sf = sfp.SFProtocol(sfp.SFP_CH_T, **opts)

	servIp = args[0]
	servPort = int( args[1] )

	__LOG__.Trace( 'started, servIp=[%s], servPort=[%s]' % (servIp, servPort))

	try :
		sock = socket( AF_INET, SOCK_STREAM )
		sock.connect( (servIp, servPort) )
		sf.setFD(sock)
		__LOG__.Trace( 'connected, servIp=[%s], servPort=[%s]' % (servIp, servPort))

	except Exception, err :
		__LOG__.Exception()

	sf.write( '', 'NTI', 'key1,key2,  2-key 4 time\n')
	sf.write( '', 'NTI', 'key1,abcd,  A-key 2 time\n')
	sf.write( '', 'NTI', 'abcd,key2,  B-key 2 time\n')
	sf.write( '', 'NTI', 'abcd,1234,  0-key 1 time\n')

	__LOG__.Trace( 'program closed' )

if __name__ == '__main__' :
	Log.Init(Log.CStandardLog())
	#   Log.Init(Log.CDummyLog())
	main()
