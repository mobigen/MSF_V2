#!/bin/env python

import os, time, signal, sys
import subprocess
signal.signal(signal.SIGTERM, signal.SIG_IGN)

def Main() :
	for i in range(3) :
		#os.system("/home/pas/user/tesse/Work/lib/SIOEventFlow/testChild.py %s >& /dev/null &" % i)
		#os.system("/home/pas/user/tesse/Work/lib/SIOEventFlow/testChild.py %s " % i)
		time.sleep(1)

	for i in xrange (100) :
		msg = "file://sv1%s.txt\n" % i
		sys.stdout.write(msg)
		sys.stdout.flush()

		sys.stderr.write(msg)
		sys.stderr.flush()
		time.sleep(1)
Main()
