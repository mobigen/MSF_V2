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
		if len(args) != 6 : raise Exception
		opts = {}
		for optKey, optVal in optList : opts[optKey] = optVal
	except :
		print 'usage : %s [-options] serv1Ip serv1Port regId regKey serv2Ip serv2Port' % (sys.argv[0])
		print 'examp : %s 10.10.10.10 1234 sys1 alarm1 20.20.20.20 5678' % (sys.argv[0])
		sfp.prnOpt()
		print '        -t[sec]       : recv heart beat period, default=no recv'
		sys.exit()

	sf1 = sfp.SFProtocol(sfp.SFP_CH_T, **opts)
	sf2 = sfp.SFProtocol(sfp.SFP_CH_T, **opts)

	try : heartBeatSec = int( opts['-t'] )
	except : heartBeatSec = 0

	serv1Ip = args[0]
	serv1Port = int( args[1] )
	regId = args[2]
	regKey = args[3]
	serv2Ip = args[4]
	serv2Port = int( args[5] )

	rsv = ' '
	regStr = '%s,%s,%s' % (heartBeatSec, regId, regKey)

	sock1 = None
	sock2 = None

	__LOG__.Trace( 'started, serv1Ip=[%s], serv1Port=[%s], regStr=[%s]' % (serv1Ip, serv1Port, regStr) )

	while SHUTDOWN == False :
		try :
			sock1 = socket( AF_INET, SOCK_STREAM )
			sock1.connect( (serv1Ip, serv1Port) )
			sf1.setFD(sock1)
			__LOG__.Trace( 'connected, serv1Ip=[%s], serv1Port=[%s], regStr=[%s]' % (serv1Ip, serv1Port, regStr) )

			sf1.write( rsv, 'REG', regStr+"\n" )

		except Exception, err :
			__LOG__.Exception()
			sys.exit()

		try :
			sock2 = socket( AF_INET, SOCK_STREAM )
			sock2.connect( (serv2Ip, serv2Port) )
			sf2.setFD(sock2)
			print sf2.sock
			print sf2.fd
			__LOG__.Trace( 'connected, serv2Ip=[%s], serv2Port=[%s], regStr=[%s]' % (serv2Ip, serv2Port, regStr) )
			break

		except Exception, err :
			__LOG__.Exception()
			sys.exit()

	while SHUTDOWN == False :
		try :
			(pt, rsv, cmd, msg) = sf1.read()
			if msg != '':
				sf2.write('','NTI',msg)

		except Exception, err :
			__LOG__.Exception()
			break

	__LOG__.Trace( 'program closed' )

if __name__ == '__main__' :
	Log.Init(Log.CStandardLog())
	#   Log.Init(Log.CDummyLog())
	main()
