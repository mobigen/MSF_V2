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

	stime = time.time()
	for i in range(100000) :
		data = str(i)
		key = data
		keyLen = '%010d' % len(key)

		packet = keyLen + key + data
		packetLen = '%010d' % len(packet)

		allPacket = '000put' + packetLen + packet
		if DEBUG :
			print allPacket
			time.sleep(1)

		sock.send( allPacket )

		if i % 10000 == 0 :
			print '%s processed' % i

	etime = time.time()
	print 'time = %s' % (etime-stime)
main()
