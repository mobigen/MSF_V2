#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys, time, threading
from socket import *

DEBUG = False

class ThClient(threading.Thread) :

	def __init__(self, id, ip, port, loopCnt) :
		threading.Thread.__init__(self)
		self.id = id
		self.loopCnt = loopCnt
		self.sock = socket( AF_INET, SOCK_STREAM )
		self.sock.connect((ip, port))
		self.sockFD = self.sock.makefile()
		
	def send(self, data) :
		sIdx = 0
		while sIdx < len(data) :
			self.sock.send( data[sIdx : sIdx+65536] )
			sIdx += 65536

	def run(self) :
		startNum = self.loopCnt

		if(1) :
			keyList = []
			for i in range(self.loopCnt) :
				key = str(i)
				keyLen = '%010d' % len(key)
				keyList.append( keyLen + key )
		
			val = ''.join(keyList)
			valLen = '%010d' % len(val)
			packet = '   MGT' + valLen + val
			self.send( packet )
		
			header = self.sock.recv(16)
			bodyLen = int( header[6:] )

			remain = bodyLen
			bodyList = []
			while remain > 0 :
				tmp = self.sock.recv(remain)
				if tmp == '' : break
				bodyList.append(tmp)
				remain -= len(tmp)

			body = ''.join(bodyList)

			dataCnt = 0
			sIdx = 0
			while sIdx < len(body) :
				keyLen = int( body[sIdx : sIdx+10] )
				sIdx += 10

				key = body[sIdx : sIdx+keyLen]
				sIdx += keyLen

				valLen = int( body[sIdx : sIdx+10] )
				sIdx += 10

				val = body[sIdx : sIdx+valLen]
				sIdx += valLen

				dataCnt += 1

			print 'dataCnt = %s' % dataCnt
		
		if(1) :
			self.send( '   #P60000000000' )
			line = self.sockFD.readline()

			keyList = []
			for i in range(self.loopCnt) :
				key = str(i)
				keyList.append( key )
		
			packet = ',,MGT,' + ','.join(keyList) + '\n'
			self.send( packet )
		
			line = self.sockFD.readline()

			dataList = line.split(',')
			pType = dataList.pop(0)
			rsv = dataList.pop(0)
			res = dataList.pop(0)

			dataCnt = 0
			for i in range( int( len(dataList)/2 ) ) :
				tmpKey = dataList[i*2]
				tmpVal = dataList[i*2+1]
				dataCnt += 1

			print 'dataCnt = %s' % dataCnt

		self.sock.close()

def main() :
	if len(sys.argv) != 5 :
		print 'usage : %s ip port thCnt loopCnt' % sys.argv[0]
		sys.exit()
	
	ip = sys.argv[1]
	port = int(sys.argv[2])
	thCnt = int(sys.argv[3])
	loopCnt = int(sys.argv[4])

	thList = []
	stime = time.time()
	for i in range(thCnt) :
		th = ThClient(i, ip, port, loopCnt)
		th.start()
		thList.append(th)

	for i in range(thCnt) :
		thList[i].join()

	etime = time.time()
	print 'time = %s' % (etime-stime)
	
main()
