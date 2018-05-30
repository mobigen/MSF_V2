#!/usr/bin/python
# -*- coding: cp949 -*-

import os, time
from DataContainer import *

def main() :
	if len(sys.argv) != 4 :
		print 'usage : %s homeDir(testDataCon) day(2) keepHour(240)' % (sys.argv[0])
		sys.exit()

	homeDir = sys.argv[1]
	day = int( sys.argv[2] ) + 1
	hour = 24
	if os.path.exists(homeDir) == False : os.mkdir(homeDir)
	keepHour = int( sys.argv[3] )

	db = DataContainer( homeDir, Mode='a', KeepHour=keepHour, BufSize=100 )

	stime = time.time()
	cnt = 0
	for dd in range( 3, day + 2 ) :
		dd = '%02i' % (dd)
		for hh in range(hour) :
			hh = '%02i' % (hh)
			for mm in range(60) :
				mm = '%02i' % (mm)
				for ss in range(60) :
					ss = '%02i' % (ss)
					msgTime = '200508%s%s%s%s' % (dd,hh,mm,ss)
					opt = 'opt'
					val = 'val'
					db.put(msgTime, val, opt)
					cnt += 1

					# print "msgTime, val, opt = %s, %s, %s" % (msgTime, val, opt)
					# time.sleep(1)

	db.close()

	etime = time.time()

	print '*** time = %s, cnt = %s' % (etime-stime, cnt)

main()
