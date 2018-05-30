#!/usr/bin/python
# -*- coding: cp949 -*-

from DataLog import *
import sys

def main() :
	if len(sys.argv) != 4 :
		print 'usage : %s dbFileName loopCnt(100000) logCnt(1000)' % (sys.argv[0])
		sys.exit()

	dbFileName = sys.argv[1]
	loopCnt = int( sys.argv[2] )
	logCnt = int( sys.argv[3] )

	rdl = DataLog( dbFileName, ReadBlockTimeout=10 )
	stime = time.time()

	for i in range(0,loopCnt) :
		key, val, msgTime, opt = rdl.next()

		if i % logCnt == 0 :
			print "%s key -> %s val" % (key, val)
			# print "%s -> %s" % (key, val)
			# print key, val, msgTime, opt

	etime = time.time()
	print "* next time = %s" % (etime-stime)
	

main()
