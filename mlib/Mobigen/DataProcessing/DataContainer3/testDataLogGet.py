#!/usr/bin/python
# -*- coding: cp949 -*-

from DataLog import *
import sys

def main() :
	if len(sys.argv) != 2 :
		print 'usage : %s dbFileName' % (sys.argv[0])
		sys.exit()

	dbFileName = sys.argv[1]

	rdl = DataLog( dbFileName )

	while 1 :
		key = raw_input('* key = ')
		key, val, msgTime, opt = rdl.get(key)
		print "key, val, msgTime, opt = %s, %s, %s, %s" % (key, val, msgTime, opt)
main()
