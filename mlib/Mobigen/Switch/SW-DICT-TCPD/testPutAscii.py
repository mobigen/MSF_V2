#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys, time
from socket import *

DEBUG = False

def main() :
	if len(sys.argv) != 3 :
		print 'usage : %s ip port' % sys.argv[0]
		sys.exit()
	
	ip = sys.argv[1]
	port = int(sys.argv[2])

	sock = socket( AF_INET, SOCK_STREAM )
	sock.connect((ip, port))
	sock.send( '   #P60000000000')

	while 1 :
		readByte = sock.recv(1)
		if readByte == '\n' : break

	stime = time.time()
	for i in range(100000) :
		sock.send(',,put,%s,%s\n' % (i,i) )
		if i % 10000 == 0 :
			print '%s processed' % i

	sock.close()
	etime = time.time()
	print 'time = %s' % (etime-stime)
main()
