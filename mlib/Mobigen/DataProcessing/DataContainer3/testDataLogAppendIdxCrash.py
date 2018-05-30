#!/usr/bin/python
# -*- coding: cp949 -*-

import os, time, sys
from DataLog import *

def main() :
	if len(sys.argv) != 5 :
		print 'usage : %s dbFileName loopCnt(100000) logCnt(1000) dataSize(80)' % (sys.argv[0])
		sys.exit()

	dbFileName = sys.argv[1]
	loopCnt = int( sys.argv[2] )
	logCnt = int( sys.argv[3] )
	dataSize = int( sys.argv[4] )

	try : os.unlink( dbFileName + ".idx" )
	except : pass

	wdl = DataLog( dbFileName, Mode='a', BufSize=100 )

	stime = time.time()

	for i in range(0,loopCnt) :
		data = str(i)[-1:] * dataSize
		recNo = wdl.put( data, i, i )
		# wdl.put( value, msgTime, opt )

		if i % logCnt == 0 :
			print "put, serial=%s, recNo = %s" % (i, recNo)
			#print "%s put %s,%s,%s" % (i, data, i, i)

	wdl.close()
	etime = time.time()
	print "* write time = %s" % (etime-stime)

main()
