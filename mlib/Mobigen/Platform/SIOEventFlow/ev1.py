#!/bin/env python

import time, sys, signal

signal.signal(signal.SIGTERM, signal.SIG_IGN)

for i in xrange (100) :
	msg = "file://%s.txt\n" % i
	sys.stdout.write(msg)
	sys.stdout.flush()

	sys.stderr.write(msg)
	sys.stderr.flush()

	time.sleep(1)
time.sleep(100)
