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
		fileTime = raw_input('* msgTime(20050810000000) = ')
		key = int( raw_input('* key(0) = ') )

		try :
			curFileTime, msgTime, opt, key, value = db.get(fileTime, key)
			print "curFileTime, msgTime, opt, key, value = %s, %s, %s, %s, %s" % (curFileTime, msgTime, opt, key, value)
		except Exception, err :
			print err.__str__()

main()
