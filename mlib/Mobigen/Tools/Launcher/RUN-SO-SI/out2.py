#!/usr/bin/python

import sys, time, signal

SHUTDOWN = False

def shutdown(sigNum=0, frame=0) :
	global SHUTDOWN
	print "signal"
	SHUTDOWN = True

signal.signal(signal.SIGTERM, shutdown)

def readLen(lenNum) :
	remain = lenNum
	res = ''

	while 1 : 
		try :
			data = sys.stdin.read(remain)
			if not data : raise Exception, 'disconnected'

			res += data
			remain -= len(data)

		except IOError :
			time.sleep(0.1)
			continue

		if remain == 0 : break
	return res

def recvFast() :
	overHead = readLen(16)
	valLen = int(overHead[6:])
	val = readLen(valLen)
	return overHead, val

f = open ("out.txt", "w")

while True:
	
	overHead, val = ('', '')

	if SHUTDOWN == True:
		break
	try:
		overHead, val = recvFast()
	except:
		break
		#time.sleep(1)
		#continue

	if val:
		#f.write(val)
		#f.flush()
		#sys.stderr.write(val)
		#sys.stderr.flush()
		
		#print val
		pass
	else:
		break
