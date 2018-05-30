#!/home/mobigen/bin/python
# -*- coding: cp949 -*-

try : import psyco; psyco.full()
except : pass

import os
import sys
import time
import getopt
import select
import threading
from socket import *
from telnetlib import Telnet

import Mobigen.DataProcessing.CSV as CSV
import Mobigen.Common.Log as Log; Log.Init()

import signal; SHUTDOWN = False
def handler(sigNum, frame) :
	global SHUTDOWN; SHUTDOWN = True
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

class Recv(threading.Thread) :
	def __init__(self, ip, id, passwd, rmtDir, recvIp, recvPort, localDir, **args) :
		threading.Thread.__init__(self)
		self.rmtIp = ip
		self.rmtId = id
		self.rmtPasswd = passwd
		self.rmtDir = rmtDir
		self.ip = recvIp
		self.port = int(recvPort)
		self.localDir = localDir
		self.alive = False

	def Release(self) :
		pass	

	def _StartDaemon(self) :
		sock = socket( AF_INET, SOCK_STREAM )
		sock.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1)
		sock.bind( (self.ip, self.port) )
		sock.listen(1)

		self.sock = sock

	def _RemoteStart(self) :
		telnet = Telnet(self.rmtIp)

		__LOG__.Trace("Remote Connect %s " % self.rmtIp)

		telnet.read_until('login:')
		telnet.write(self.rmtId+'\r')
		time.sleep(1)

		telnet.read_until('Password:')
		telnet.write(self.rmtPasswd+'\r')
		time.sleep(1)

		__LOG__.Trace("Remote Login")

		telnet.read_until('>')
		telnet.write('csh\r')
		time.sleep(1)

		telnet.read_until('%')
		telnet.write('bin\r')
		time.sleep(1)

		telnet.read_until('%')
		cmd = 'CSV-SEND %s %s %s >& /dev/null & \r' % (self.ip, self.port, self.rmtDir)
		telnet.write(cmd)
		time.sleep(1)
		__LOG__.Trace("Remote Command Execute : %s" % cmd)

		telnet.read_until('%')
		telnet.write('exit\r')

	def run(self) :
		self.alive = True

		try :
			while 1 : 
				self._StartDaemon()
				sockDaemon = [self.sock]
				__LOG__.Trace("CSV-RECV-DAEMON Start")


				while True :
					inSockList,outSockList,exceptSockList = select.select(sockDaemon,[],[], 1)
					if(len(inSockList)) : break 

					__LOG__.Trace("Ready")
					time.sleep(2)
					self._RemoteStart()
					continue

				sock, addr = self.sock.accept()
				__LOG__.Watch("Client Connect %s" % str(addr))

				sockFD = sock.makefile()
				self.sock.close() # Daemon Socket close

				CSVWriter = CSV.Writer(self.localDir, CSV.PARTITION, Mode="w", lineNum=1000000)

				cnt = 0
				while True : 
					inSockList,outSockList,exceptSockList = select.select([sock],[],[], 1)
					if(len(inSockList)==0) : 
						time.sleep(1)
						continue

					line = sockFD.readline()
					if(not line) : 
						__LOG__.Trace("Client sock fail")
						break

					CSVWriter.putEx(line)
					cnt = cnt + 1
					if(cnt%100000==0) :
						__LOG__.Watch(line)
						cnt = 0

				sockFD.close()
				__LOG__.Trace("Client disconnect")

		except :
			__LOG__.Exception()

		self.alive = False

	def IsAlive(self) :
		return self.alive

def Usage() :
	print 'Usage : %s [option] rmtIP rmtID rmtPass rmtDir recvIP recvPort recvDir' % (sys.argv[0])
	print 
	print 'option :'
	print '  -l, --last         last data'
	print '  -d, --debug        debug mode'
	sys.exit()
	
def Main() :
	global SHUTDOWN

	try : opts, args = getopt.getopt(sys.argv[1:], 'dl', ["last", "debug"])
	except : Usage()
	if len(args) !=7 : Usage()


	try : os.makedirs(args[6])
	except : pass

	options = {}

	for o, v in opts:
		if o in ('-l', '--last') : options['LastRecordFlag'] = True
		if o in ('-d', '--debug') : options['Debug'] = None

	if(not options.has_key("Debug")) : 
		logPath = args[6]
		logPath = logPath.replace('/', '_')
		logPath = "../LOG/CSV-RECV%s.log" % logPath
		Log.Init(Log.CRotatingLog(logPath, 1000000, 10))

	obj = Recv(args[0], args[1], args[2], args[3], args[4], args[5], args[6], **options)
	__LOG__.Trace("Recv start")
	obj.setDaemon(1)
	obj.start()
	time.sleep(10) # obj  정상수행이전에 While로 들어가는 시간차 설정  

	while True :
		if SHUTDOWN : break

		if obj.IsAlive() == False:
			__LOG__.Trace("Recv dead detected, so join")
			obj.Release()

			try :
				obj = Recv(args[0], args[1], args[2], args[3], args[4], args[5], args[6], **options)
				obj.start()
				__LOG__.Trace("*** Recv restart")
			except :
				__LOG__.Exception()

		time.sleep(2)

	obj.Release()

	__LOG__.Trace("--- Recv shutdown")

if __name__ == '__main__' :
	Main()
