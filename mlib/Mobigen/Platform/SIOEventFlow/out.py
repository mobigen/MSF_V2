#!/usr/bin/env python

import sys
import time

for i in range(0, 100000) :
	sys.stdout.write("fisrt_%010d\n" % i)
	sys.stdout.flush()

	sys.stderr.write("first_%010d\n" % i)
	sys.stderr.flush()

	time.sleep(0.1)
