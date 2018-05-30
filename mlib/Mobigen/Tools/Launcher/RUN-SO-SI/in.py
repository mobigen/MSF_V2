#!/usr/bin/python

import sys, time, signal

def shutdown(sigNum=0, frame=0) :
	global SHUTDOWN
	time.sleep(20)

signal.signal(signal.SIGTERM, shutdown)

cnt = 0
while True:
	cnt = cnt + 1
	#line = "%d" % cnt
	#ptype1 = "%6s%010d%s" % ('', len(line), line)
	ptype1 = "      0000000080aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
	sys.stdout.write(ptype1)
	sys.stdout.flush()
	sys.stderr.write("error\n")
	sys.stderr.flush()

	if cnt > 1000000:
		break
	#sys.stdout.flush()
	#time.sleep(3)
