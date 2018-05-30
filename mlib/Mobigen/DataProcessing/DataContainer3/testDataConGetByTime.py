#!/usr/bin/python
# -*- coding: cp949 -*-

from DataContainer import *
import sys

def main() :
	if len(sys.argv) != 2 :
		print 'usage : %s homeDir(testDataCon)' % (sys.argv[0])
		sys.exit()

	homeDir = sys.argv[1]

	db = DataContainer( homeDir )

	while 1 :
		fileTime = raw_input('* fileTime(20050802000000) = ')
		msgTime = raw_input('* msgTime(20050802010101) = ')
	
		curFileTime, msgTime, opt, key, value = db.getByTime(fileTime, msgTime)
		print "curFileTime, msgTime, opt, key, value = %s, %s, %s, %s, %s" % (curFileTime, msgTime, opt, key, value)

main()
