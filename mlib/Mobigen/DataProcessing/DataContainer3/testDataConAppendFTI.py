#!/usr/bin/python
# -*- coding: cp949 -*-

from DataContainer import *
import sys

def main() :
	if len(sys.argv) != 2 :
		print 'usage : %s homeDir(testDataCon)' % (sys.argv[0])
		sys.exit()

	homeDir = sys.argv[1]

	db = DataContainer( homeDir, Mode='a', KeepHour=2400, FileTimeInterval=10 )

	while 1 :
		msgTime = raw_input('* msgTime(20050810000000) = ')

		recno = db.put(msgTime, 'val', 'opt')

		print "recno, msgTime inserted = %s, %s" % (recno, msgTime)

main()
