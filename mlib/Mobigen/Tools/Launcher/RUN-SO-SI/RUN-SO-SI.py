#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: eek eek@mobigen.com
# @Date: 2006/08/08

import os, sys, time, re, getopt, socket, fcntl
import select
import threading
import subprocess as SP
from socket import *
import signal
import ConfigParser

import Mobigen.Common.Log as Log; Log.Init()

SHUTDOWN = False

# 순차적으로 프로세서를 종료할지를 결정함.
g_sequence = False
g_sequence_timeout = 5

# 순서대로 종료시킨후 기다리는 시간.
g_wait_time = 0

g_isFile = False

def shutdown(sigNum=0, frame=0) :
	global SHUTDOWN
	if (sigNum > 0):
		__LOG__.Trace("signal: %d" % sigNum)
	SHUTDOWN = True
	signal.signal(signal.SIGTERM, shutdown)
	signal.signal(signal.SIGINT, shutdown)
	signal.signal(signal.SIGHUP, shutdown)
	signal.signal(signal.SIGPIPE, shutdown)
	signal.signal(signal.SIGCHLD, signal.SIG_IGN)

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGHUP, shutdown)
signal.signal(signal.SIGPIPE, shutdown)
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

def error(val) :

	__LOG__.Trace( val )

	"""
	try:
		sys.stderr.write( "--- error : %s\n" % val )
		sys.stderr.flush()
	except:
		pass
	"""

def debug(val) :

	__LOG__.Trace( val )
	"""
	try:
		sys.stderr.write( "*** debug : %s\n" % val )
		sys.stderr.flush()
	except:
		pass
	"""
	pass

def log(val) :
	__LOG__.Trace( val )
	"""
	try:
		sys.stderr.write( "+++ log   : %s\n" % val )
		sys.stderr.flush()
	except:
		pass
	"""

class LogThread(threading.Thread):

	def __init__(self, logsock, errHash):
		threading.Thread.__init__(self)

		self.shutdown = False
		self.errHash = errHash
		self.logSock = logsock
		self.sendSock = socket(AF_UNIX, SOCK_DGRAM)

		self.process = None
		self.cmd = "LogThread"

	def make_nonblocking(self, fd):
		flags = fcntl.fcntl(fd, fcntl.F_GETFL)
		#if flags & ~os.O_NONBLOCK:
		fcntl.fcntl(fd, fcntl.F_SETFL, flags & os.O_NONBLOCK)

	def setNonBlock(self):
		for fd in self.errHash.keys():
			self.make_nonblocking(fd)

	def write(self, msg):

		global g_isFile
		if g_isFile:
			__LOG__.Trace( msg )
			return 

		try:
			udp_msg = "%6s%010d%s" % ("", len(msg), msg)
			self.sendSock.sendto(udp_msg, self.logSock)
		except:
			# UUDP가 없는 경우 stderr로 출력한다.
			__LOG__.Trace("LogThread.write(%s)" % msg)

	def kill(self) :
		self.shutdown = True
		__LOG__.Trace( 'LogThread.kill : called kill method')
		#del self.process.stdout
		#self.process.stdout = None

	def run(self):

		self.setNonBlock()

		r = self.errHash.keys()   
		e = self.errHash.keys()
		w = []

		first_read = {}

		while True :
			if self.shutdown  : break 

			r1,w1,e1 = select.select(r,w,e,1.0)

			for e_socket in e1:
				__LOG__.Trace( 'stderr error ')
				#self.shutdown = True
				shutdown()
				#break

			for fd in r1:
				msg = os.read(fd, 1024)
				if msg:
					if first_read.has_key(fd) == False:
						first_read[fd] = True
						# 첫번째 stderr 메시지가 command not found인경우 
						# 프로그램이 존재하지 않는 경우임.
						if re.search("command not found", msg) != None:
							__LOG__.Trace( 'command not found')
							self.shutdown = True
							break
					self.write("%s:%s" % (self.errHash[fd], msg))
				else:
					#__LOG__.Trace( 'stderr read error ')
					#self.shutdown = True
					shutdown()
					#break
		shutdown()

#class SFModule(threading.Thread):
class SFModule(object):

	def __init__(self, cmd, process):
		#threading.Thread.__init__(self)
		object.__init__(self)

		self.shutdown = False

		self.cmd = cmd
		self.pid = process.pid
		self.stdout = process.stdout
		self.stdin = None
		self.process = process

	def setStdin(self, stdin):
		self.stdin = stdin

	def isPoll(self):

		try:
			os.kill(self.pid, 0)
		except:
			return False

		return True

	def kill(self) :
		self.shutdown = True
		__LOG__.Trace( 'SFModule.kill : called kill method (%s)' % self.cmd)
		try:
			os.kill(self.pid, signal.SIGTERM)
		except:
			__LOG__.Trace( 'called kill method error (%s)' % self.cmd)
			pass

	def start(self):
		pass

	def run(self):

		while True:
			if self.shutdown  : break
			#__LOG__.Trace( "read(%s)" % self.cmd )
			if self.process.poll():
				break
			#time.sleep(1)
			select.select([],[],[],1.0)
			

			#try:
			#	overHead, val = self.recvFast()
			#	#log ( "write(%s)" % self.cmd)
			#	self.write(overHead, val)
			#except:
			#	__LOG__.Trace( 'except: %s' % self.cmd)
			#	shutdown()
			#	break
		del self.process 
		self.process = None

	def readLen(self, lenNum) :
		remain = lenNum
		res = ''

		while True : 
			try :
				if self.shutdown : break
				data = self.stdout.read(remain)
				if not data : raise Exception, 'disconnected (%s)' % self.cmd

				res += data
				remain -= len(data)

			except IOError :
				#time.sleep(0.1)
				select.select([],[],[],0.1)
				continue

			if remain == 0 : break
		return res

	def recvFast(self) :
		overHead = self.readLen(16)
		valLen = int(overHead[6:])
		val = self.readLen(valLen)
		return overHead, val

	def write(self, overHead, recvData):
		if self.stdin:
			data = overHead + recvData

			self.stdin.write(data)
			self.stdin.flush()
		else:
			__LOG__.Trace("self.stdin == None")


class SFLauncher(threading.Thread) :

	def __init__(self, cmdList, send_port) :
		threading.Thread.__init__(self)

		self.cmdList = cmdList
		self.processList = []
		self.errHash = {}
		self.send_port = send_port

		self.shutdown = False

	def waitProcess(self, p):
		__LOG__.Trace( 'SFLauncher.waitProcess [%s]' % p.cmd)
		global g_sequence, g_sequence_timeout, g_wait_time

		sleep_count = 0
		while g_sequence == True and p.process != None:
			#r = p.process.poll()
			r = p.isPoll()
			#__LOG__.Trace('pool[%s][%s][%s][%s]' % (r, p.cmd, sleep_count, g_sequence_timeout))
			if not r:
				break
			if sleep_count >= g_sequence_timeout:
				break
			sleep_count = sleep_count + 1
			#time.sleep(1)
			select.select([],[],[],1.0)
			p.kill()

		while g_wait_time > 0:
			#time.sleep(g_wait_time)
			select.select([],[],[],g_wait_time)
			break

	def kill(self) :
		__LOG__.Trace( 'SFLauncher.kill : called kill method')
		self.shutdown = True
		for process in self.processList:
			process.kill()
			self.waitProcess(process)

		try:
			for process in self.processList:
				# 모두종료하고 sigkill르 보내다.
				try: os.kill(process.pid, signal.SIGKILL)
				except: pass
		except: pass

	def popenProcess(self, cmd, after_stdout):
		#__LOG__.Trace( 'process start ')
		#return SP.Popen(cmd, shell=True, bufsize=100, \
		#	stdin=SP.PIPE, stdout=SP.PIPE, stderr=SP.PIPE, close_fds=True)

		if not after_stdout:
			after_stdout = SP.PIPE

		__LOG__.Trace( 'process start [%s]' % cmd)

		return SP.Popen(cmd, stdin=after_stdout, stdout=SP.PIPE, stderr=SP.PIPE)

	def cmdSplit(self, cmd):

		cmd = cmd.strip()
		cmd = cmd.replace('\t', ' ')
		pipe_cmd = []
		argList = []

		isQuotaion = False
		isAposterophe = False
		for i in range(len(cmd)):
			c = cmd[i]
			if c == ' ' and isQuotaion == False and isAposterophe == False:
				if argList:
					# ARG에 처음에 나오는 '이나 "를 제거함.
					if argList[0] == "'" or argList[0] == '"':
						del argList[0]
						del argList[-1]
					pipe_cmd.append( "".join(argList))
					argList = []
				continue

			if c == "'":
				if isAposterophe:
					isAposterophe = False
				else:
					isAposterophe = True
			if c == '"':
				if isQuotaion:
					isQuotaion = False
				else:
					isQuotaion = True

			argList.append(c)

		if argList:
			# ARG에 처음에 나오는 '이나 "를 제거함.
			if argList[0] == "'" or argList[0] == '"':
				del argList[0]
				del argList[-1]
			pipe_cmd.append( "".join(argList))

		return pipe_cmd



	def runProcess(self):
		"""  사용자가 정의한 모듈을 실행 """

		after_process = None
		after_stdout = None

		for cmd in self.cmdList:
			#__LOG__.Trace("process: %s" % cmd)
			cmd = cmd.strip()

			pipe_cmd = []

			#m = re.split("\s+", cmd)
			#if m :
			#	for arg in m:
			#		pipe_cmd.append(arg)
			#else:
			#	pipe_cmd.append(cmd)

			pipe_cmd = self.cmdSplit(cmd)

			#__LOG__.Trace("cmd: %s " % str(pipe_cmd))
			#process = self.popenProcess(cmd, after_stdout)
			#process = self.popenProcess(pipe_cmd, after_stdout)
			try:
				process = self.popenProcess(pipe_cmd, after_stdout)
			except:
				__LOG__.Trace("run error")
				shutdown()
				return False 


			sfmodule = SFModule(cmd, process)
			#if after_process:
			#	after_process.setStdin(process.stdin)

			after_process = sfmodule
			after_stdout = process.stdout

			self.processList.append(sfmodule)

			self.errHash[process.stderr.fileno()] = "%s|%s|||" % \
				(process.pid, cmd)

			__LOG__.Trace("process: pid[%s]: cmd[%s]: fileno[%s]" % \
				( process.pid, cmd, process.stderr.fileno()))


		for process in self.processList:
			process.start()

		return True

	def run(self) :
		__LOG__.Trace( 'SFLanuncher.run : started' )

		if True:
		#try :
			r = self.runProcess()

			if r:
				logThread = LogThread(self.send_port, self.errHash)
				logThread.setDaemon(True)
				logThread.start()
				self.processList.append(logThread)

			while r :
				if self.shutdown  : break 
				#time.sleep(3)
				select.select([],[],[], 3)

		#except Exception, err :
		else:
			if self.shutdown : pass

			else :
				__LOG__.Trace( "SFLauncher.run : error")
		
		__LOG__.Trace( 'shutdown()')

		shutdown()

		#self.kill()

		#for th in self.processList:
		#	th.join()

		__LOG__.Trace( 'SFLauncher.run : thread closed' )

def readIniFile(iniFileName, sections):
	conf = ConfigParser.ConfigParser()
	conf.read(iniFileName)

	log_port = None
	cmdlist = []

	s = ""
	keys = []
	for section in sections:
		s = section
		for(paramKey, paramVal) in conf.items(section):

			if paramKey == "logport":
				log_port = paramVal.strip()
				continue
			keys.append(paramKey)

	keys.sort()
	for k in keys:
		paramVal =  conf.get(s, k)
		__LOG__.Trace("---> %s:%s" % (k, paramVal))
		cmdlist.append(paramVal.strip())

	return (cmdlist, log_port)


def usage():
	print 'usage : %s [-h] [-s] [-w] [-c] [-t] P1 P2 [P3...Pn] send_sock' % (sys.argv[0])
	print '         -s : kill process in sequence'
	print '         -w[time] : kill process wait time default: 5(sec)'
	print '         -t[time]  :  process term wait time default: 0(sec)'
	print '         -c : configure file read '
	print '         -f        : send_sock to logfile' 
	print '         -n[fileNum,fileSize]  : logfile num and file Size  '
	print '            defalut 4, 10000000'
	print 'example: %s -h' % sys.argv[0]
	print '         %s out1.py out2.py out3.py log_send' % sys.argv[0]
	print '         %s -s -w10 out1.py out2.py out3.py log_send' % sys.argv[0]
	print '         %s -c PROC sample.ini' % sys.argv[0]
	print '         %s -f -c PROC sample.ini' % sys.argv[0]
	print '         %s -f -n2,50000 -c PROC sample.ini' % sys.argv[0]

def main() :

	global g_sequence, g_sequence_timeout, g_wait_time, g_isFile

	if len(sys.argv) < 3 :
		usage()
		sys.exit()

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hsw:ct:fn:", ["help", "waittime"])
	except :
		# print help information and exit:
		usage()
		sys.exit(2)

	iniFile = False

	g_wait_time = 0
	
	logSize = 10000000
	logFileNum = 3
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		if o in ("-s"):
			g_sequence = True
		if o in ("-w", "--waittime"):
			g_sequence_timeout = int(a)
		if o in ("-c"):
			iniFile = True
		if o in ("-t"):
			g_wait_time = int(a)
		if o in ("-f"):
			g_isFile = True
		if o in ("-n"):
			try:
				(logFileNum, logSize) = map(int, a.split(","))
			except:
				logSize = 10000000
				logFileNum = 3

	if iniFile == False and  len(args) < 2:
		usage()
		sys.exit()

	log_port = None

	if iniFile :
		iniFileName = args.pop()
		(args, log_port) = readIniFile(iniFileName, args)
	else :
		log_port = args.pop()


	if not log_port:
		__LOG__.Trace( "log_port error" )
		usage()
		sys.exit()


	if g_isFile:
		# -f 옵션인 경우 파일에 저장함.
		Log.Init( Log.CRotatingLog( log_port, logSize, logFileNum ) )
	

	__LOG__.Trace( "log_port: [%s]" % log_port)

	
	countProcess = SFLauncher(args, log_port)
	countProcess.setDaemon(True)
	countProcess.start()

	global SHUTDOWN

	while 1 :
		try:
			if SHUTDOWN : break
			#else : time.sleep(1)
			else : select.select([],[],[], 1)
		except:
			if SHUTDOWN : break
			pass

	__LOG__.Trace('MAIN : kill()')
	countProcess.kill()
	countProcess.join()

	__LOG__.Trace('MAIN : closed')

if __name__ == "__main__":

	main()
