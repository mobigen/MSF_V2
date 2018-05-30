#!/usr/bin/python

import subprocess, time

pros = subprocess.Popen( ["read.py"], shell=True, bufsize=1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)

for i in xrange(10) :
	try :
		pros.stdin.write( "%s\n" % i )
		time.sleep(1)
	except IndexError :
		print "tesse : IndexError"
	except IOError :
		print "tesse : IOError"
