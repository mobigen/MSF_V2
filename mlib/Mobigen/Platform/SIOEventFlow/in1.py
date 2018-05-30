#!/usr/bin/env python

import sys

fd = open("in1.txt", "w")

while (True) :
	line = sys.stdin.readline()
#	print line
	fd.write(line)
	fd.flush()

	sys.stdout.write(line)
	sys.stdout.flush()

	sys.stderr.write(line)
	sys.stderr.flush()

fd.close()
