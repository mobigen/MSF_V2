#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys, time
from socket import *

DEBUG = False

def send(sock, data) :
	sIdx = 0
	while sIdx < len(data) :
		sock.send( data[sIdx : sIdx+65536] )
		sIdx += 65536

def main() :
	if len(sys.argv) != 3 :
		print 'usage : %s ip port' % sys.argv[0]
		sys.exit()
	
	ip = sys.argv[1]
	port = int(sys.argv[2])

	sock = socket( AF_INET, SOCK_STREAM )
	sock.connect((ip, port))

	if(1) :
		stime = time.time()
		dataList = []
		for i in range(100000) :
			key = str(i)
			keyLen = '%010d' % len(key)
	
			data = str(i)
			dataLen = '%010d' % len(data)
	
			dataList.append( keyLen + key + dataLen + data )
	
		data = ''.join(dataList)
		dataLen = '%010d' % len(data)
		allPacket = '000mpt' + dataLen + data
	
		send( sock, allPacket )
	
		etime = time.time()
		print 'time = %s' % (etime-stime)
	
	if(0) :
		send( sock, '   #P60000000000' )

		stime = time.time()
		dataList = []
		for i in range(1000) :
			data = '%s,%s' % (i,i)
			dataList.append( data )
	
		data = ','.join(dataList)
		allPacket = ',,mpt,' + data + '\n'
	
		send( sock, allPacket )
	
		etime = time.time()
		print 'time = %s' % (etime-stime)
main()
