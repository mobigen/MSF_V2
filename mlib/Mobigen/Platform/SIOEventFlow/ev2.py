#!/bin/env python

import time, sys

while 1 :
	line = sys.stdin.readline()
	sys.stderr.write( line )
	sys.stderr.flush()
	sys.stdout.write( line )
	sys.stdout.flush()
	time.sleep(1)
