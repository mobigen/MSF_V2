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
		
	def run(self) :
		self.sock.send( '   #P60000000000' )
		data = self.sockFD.readline()

		startNum = self.loopCnt
		for i in range(self.loopCnt) :
			sdata = str(i)
			self.sock.send(',,get,%s\n' % i )
			data = self.sockFD.readline()
			data = data.strip()
			dataList = data.split(',')
			rdata = dataList[3]
	
			if sdata != rdata :
				print 'error : id=%s, sdata=%s, rdata=%s' % (self.id, sdata, rdata)
	
			if i % 10000 == 0 :
				print '%s : %s processed' % (self.id, i)

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
