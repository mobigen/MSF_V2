import sys,os
from SM import SM

import Mobigen.Common.Log as Log; Log.Init()

def Main(argv) :

	if len(argv) < 3:
		print "Usage: %s ip port node_id " % sys.argv[0]
		print "       %s 10.0.0.1 1234 1 " % sys.argv[0]
		print 
		sys.exit()

	logFile = "SM_%s_%s_%s.log" % (argv[0], argv[1], argv[2])
	Log.Init(Log.CRotatingLog(logFile, 10000000, 2))
	#Log.Init( )
	#Log.Init(Log.CUDPLog2( 9999 ))

	s = SM(argv[0], argv[1], argv[2])
	s.start()
