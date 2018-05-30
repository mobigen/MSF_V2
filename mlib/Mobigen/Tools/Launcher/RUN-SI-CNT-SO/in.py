#!/usr/bin/python

import sys, time, signal


while True:
	line = sys.stdin.readline()
	ptype1 = "%6s%010d%s" % ('', len(line), line)
	sys.stdout.write(ptype1)
	sys.stdout.flush()
