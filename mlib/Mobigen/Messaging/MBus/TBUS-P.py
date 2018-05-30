#!/usr/bin/python

#---------------------------------------------------------------------
# version | date : writer : description
#---------+-----------------------------------------------------------
# V2.0    | 070423 : cdssw : final
#---------------------------------------------------------------------

import Mobigen.Common.Log as Log; Log.Init()
import Mobigen.Common.SFProtocol.SFProtocol as sfp

import os, sys, getopt
from socket import *

def main() :
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

	msg = 'key1,key2,test string'
	for count in range(10001):
		try:
			sf.write( '', 'NTI', msg+'\n')
		except Exception, err :
			__LOG__.Exception()

	__LOG__.Trace( 'program closed' )

if __name__ == '__main__' :
	Log.Init(Log.CStandardLog())
	#   Log.Init(Log.CDummyLog())
	main()
