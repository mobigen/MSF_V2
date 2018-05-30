#!/usr/bin/python

#---------------------------------------------------------------------
# version | date : writer : description
#---------+-----------------------------------------------------------
# V2.0    | 070423 : cdssw : final
#---------------------------------------------------------------------

import Mobigen.Common.Log as Log; Log.Init()
import Mobigen.Common.SFProtocol.SFProtocol as sfp

import os, sys, getopt, select
from socket import *

import signal
SHUTDOWN = False

##### psyco #####
try:
    import psyco
    psyco.full()
except ImportError:
    pass
#################

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
	sf1 = sfp.SFProtocol(sfp.SFP_CH_S, **opts)

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

	outputList = [sock]
	sf1.setFD(sys.stdin)
	while SHUTDOWN == False :
		try:
			(pt, rsv, cmd, msg) = sf1.read()
			__LOG__.Trace( 'PA INPUT : %s,%s,%s,%s...'%(pt, rsv, cmd, msg[:10]))

			"""
			while 1:
				try:
					inputReady, outputReady, execptReady = select.select([], outputList, [], 1)
					if len(outputList) != 0:
						sf.write( '', 'STI', msg)
						break
				except Exception, err:
					__LOG__.Exception()
					break
			"""
			#msg = msg.strip('\n')
			#sf.write( '', 'STI', msg+'\n')
			sf.write( '', 'STI', msg)

		except sfp.SFPBadPType, err:
			__LOG__.Exception()
			continue
		except sfp.SFPBadFormat	, err:
			__LOG__.Exception()
			continue
		except Exception, err :
			__LOG__.Exception()
			SHUTDOWN = True

	__LOG__.Trace( 'program closed' )

if __name__ == '__main__' :
	Log.Init(Log.CStandardErrorLog())
	main()
