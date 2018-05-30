#!/usr/bin/python

#---------------------------------------------------------------------
# version | date : writer : description
#---------+-----------------------------------------------------------
# V2.0    | 070423 : cdssw : final
#---------------------------------------------------------------------

import Mobigen.Common.Log as Log; Log.Init()
import Mobigen.SF.lib.SFProtocol as sfp

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
		if len(args) != 4 : raise Exception
		opts = {}
		for optKey, optVal in optList : opts[optKey] = optVal
	except :
		print 'usage : %s [-options] servIp servPort regId regKey' % (sys.argv[0])
		print 'examp : %s 10.10.10.10 1234 sys1 alarm1' % (sys.argv[0])
		sfp.prnOpt()
		print '        -t[sec]       : recv heart beat period, default=no recv'
		sys.exit()

	sf = sfp.SFProtocol(sfp.SFP_CH_T, **opts)

	try : heartBeatSec = int( opts['-t'] )
	except : heartBeatSec = 0

	servIp = args[0]
	servPort = int( args[1] )
	regId = args[2]
	regKey = args[3]

	rsv = ' '
	regStr = '%s,%s,%s' % (heartBeatSec, regId, regKey)

	sock = None

	__LOG__.Trace( 'started, servIp=[%s], servPort=[%s], regStr=[%s]' % (servIp, servPort, regStr) )

	while SHUTDOWN == False :
		try :
			sock = socket( AF_INET, SOCK_STREAM )
			sock.connect( (servIp, servPort) )
			sf.setFD(sock)
			__LOG__.Trace( 'connected, servIp=[%s], servPort=[%s], regStr=[%s]' % (servIp, servPort, regStr) )

			sf.write( rsv, 'REG', regStr+"\n" )
			break

		except Exception, err :
			__LOG__.Exception()
			sys.exit()

	sf.read()
	while SHUTDOWN == False :
		try :
			(pt, rsv, cmd, msg) = sf.read()
			if msg != '':
				msg = msg.strip('\n')
				msg = msg.split(',')
				msg = msg[2] + ' &'
				os.system(msg)

		except Exception, err :
			__LOG__.Exception()
			break

	__LOG__.Trace( 'program closed' )

if __name__ == '__main__' :
	Log.Init(Log.CStandardLog())
	#   Log.Init(Log.CDummyLog())
	main()
