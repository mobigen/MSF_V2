#!/usr/bin/python

import sys, time, signal

f = open ("out.txt", "w")

while True:
	line = sys.stdin.readline()
	if line:
		f.write(line)
		print line
	else:
		break
