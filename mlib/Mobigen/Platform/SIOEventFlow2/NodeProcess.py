#!/bin/env python
#coding: utf-8

import threading
import time
import subprocess
import collections
import sys
import select
import signal
import os
import shlex
from datetime import datetime
import __main__

import Mobigen.Common.Log as Log; Log.Init()


SHUTDOWN = False

def sigHandler(sigNum, f) :
	global SHUTDOWN
	sys.stderr.write( ">>>>> sigHandler : signal received = %s\n" % sigNum )
	SHUTDOWN = True

### signal handler ###
#signal.signal(signal.SIGCHLD, sigHandler)
signal.signal(signal.SIGINT, sigHandler)
#signal.signal(signal.SIGTERM, sigHandler)
#signal.signal(signal.SIGPIPE, sigHandler)


def stdLog( msg ) :
	if __main__.DEBUG_MODE : __LOG__.Trace( msg )
	else : pass


class NodeStdinTh(threading.Thread):

	def __init__(self, node):

		threading.Thread.__init__(self)
		self.node = node


	def putProsStdin(self, putMsg):

		self.node.pros.stdin.write(putMsg) # raise IOError if process killed
		self.node.pros.stdin.flush()
		self.node.lastInEvent = '%s - %s' % (datetime.now(), putMsg)
		self.node.efClass.monDeq.append((str(datetime.now()), " IN -> %s" % (self.node.nodeName), repr(putMsg)))
		self.node.efClass.saveDeq.append( '[%s] %s  IN : %s' % ( datetime.now(), self.node.nodeName, putMsg.strip() ) )
		stdLog( "[%s] stdin  : %s" % (self.node.nodeName, repr(putMsg)) )

		while True :
			try : readReady, tmp, tmp = select.select( [self.node.pros.stderr], [], [], 1)	# UNIX
			except : readReady = ['']	# Windows

			if len(readReady) > 0 :
				msg = self.node.pros.stderr.readline()

				if msg == "" :
					raise IOError, 'Process Killed'

				self.node.efClass.monDeq.append((str(datetime.now()), "ERR <- %s" % (self.node.nodeName), repr(msg)))
				self.node.efClass.saveDeq.append( '[%s] %s ERR : %s' % ( datetime.now(), self.node.nodeName, msg.strip() ) )
				self.node.lastErrEvent = '%s - %s' % (datetime.now(), msg)
				stdLog( "[%s] stderr : %s" % ( self.node.nodeName, repr(msg) ) )

				if self.node.system == 'win' :
					msg = msg.strip()
					putMsg = putMsg.strip()

				if msg == "\n" or msg == putMsg :
					return msg
				else :
					__LOG__.Trace( "[%s] stderr : %s" % ( self.node.nodeName, repr(msg) ) )
			else :
				pass

			if self.node.shutdown :
				raise IOError, 'Process Shutdown'


	def run(self) :

		while self.node.shutdown == False :
			#- ACT
			if self.node.stat == "ACT" :
				processMsgCnt = 0

				try :
					for deq in self.node.stdinDeqList :
						try :
							msg = deq.popleft()
							processMsgCnt += 1
						except :
							continue

						self.putProsStdin(msg)
						break

					if processMsgCnt == 0 :

						while self.node.shutdown == False :
							try : 
								readReady, tmp, tmp = select.select( [self.node.pros.stderr], [], [], 1 )
							except :
								break

							if len(readReady) > 0 :
								errMsg = self.node.pros.stderr.readline()

								if errMsg == '' :
									raise IOError, 'Process Killed'

								self.node.efClass.monDeq.append((str(datetime.now()), "ERR <- %s" % (self.node.nodeName), repr(errMsg)))
								self.node.efClass.saveDeq.append( '[%s] %s ERR : %s' % ( datetime.now(), self.node.nodeName, errMsg.strip() ) )
								self.node.lastErrEvent = '%s - %s' % (datetime.now(), errMsg)
								__LOG__.Trace( "[%s] stderr : %s" % ( self.node.nodeName, repr(errMsg) ) )

							else :
								break

				except IOError, err :
					if processMsgCnt != 0 and self.node.efClass.errorDataFileSkipFlag == False :
						__LOG__.Trace("[%s] stdinThread : %s  rollback : %s" % ( self.node.nodeName, err, repr(msg) ))
						deq.appendleft(msg)
					else :
						__LOG__.Trace("[%s] stdinThread : %s" % ( self.node.nodeName, err ))
					time.sleep(1)

				except :	# need for confirmation
					__LOG__.Exception()
					if processMsgCnt != 0 and self.node.efClass.errorDataFileSkipFlag :
						__LOG__.Trace("[%s] stdinThread rollback : %s" % ( self.node.nodeName, repr(msg) ))
						deq.appendleft(msg)
					time.sleep(1)

				finally :
					if self.node.shutdown :
						break

			#- TRM
			else :
				time.sleep(1)



class NodeStdoutTh(threading.Thread) :

	def __init__(self, node) :

		threading.Thread.__init__(self)
		self.node = node


	def getProsStdout(self) :

		while True :
			try : readReady, tmp, tmp = select.select( [self.node.pros.stdout], [], [], 1)	# UNIX
			except : readReady = ['']	# Windows

			if len(readReady) > 0 :
				msg = self.node.pros.stdout.readline()

				if msg == "" :
					raise IOError, 'Process Killed'
				else :
					stdLog( "[%s] stdout : %s" % (self.node.nodeName, repr(msg)) )
					return msg
			else :
				pass

			if self.node.shutdown :
				raise IOError, 'Process Shutdown'


	def run(self):

		while self.node.shutdown == False :
			#- ACT
			if self.node.stat == "ACT" :
				try :
					msg = self.getProsStdout()

					self.node.lastOutEvent = '%s - %s' % (datetime.now(), msg)
					self.node.efClass.monDeq.append((str(datetime.now()), "%s -> OUT" % (self.node.nodeName), repr(msg)))
					self.node.efClass.saveDeq.append( '[%s] %s OUT : %s' % ( datetime.now(), self.node.nodeName, msg.strip() ) )

					for deq in self.node.stdoutDeqList :
						while True :
							if len(deq) < self.node.efClass.maxCmdQSize :
								deq.append(msg)
								break
							else :
								if self.node.shutdown or self.node.stat == "TRM" :
									deq.append(msg)
									break
								else:
									__LOG__.Trace( "[%s] Queue Full Flush Event : %s" % ( self.node.nodeName, repr(deq.popleft()) ) )

					if self.node.shutdown :
						break

				except IOError, err :
					__LOG__.Trace("[%s] stdoutThread : %s" % ( self.node.nodeName, err ))
					time.sleep(1)

				except Exception, err :
					__LOG__.Exception()
					time.sleep(1)

				finally :
					if self.node.shutdown :
						break

			#- TRM
			else :
				time.sleep(1)



class Node(threading.Thread) :

	def __init__(self, nodeName, progName, efClass, **opt):

		threading.Thread.__init__(self)

		self.nodeName = nodeName
		self.progName = progName
		self.efClass = efClass

		self.lastInEvent = '-'
		self.lastOutEvent = '-'
		self.lastErrEvent = '-'

		self.prosPid = '-'
		self.stat = "TRM"
		self.actStat = 'ABN'
		self.shutdown = False
		self.actCnt = 1
		self.actTime = time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime( time.time() ) )
		self.system = 'win' if 'win' in sys.platform else 'linux'

		self.popenPros()

		self.broadcastDeq = collections.deque()
		self.sharingDeq = collections.deque()

		self.broadcastNodeList = []
		self.sharingNodeList = []

		self.stdinDeqList = [ self.broadcastDeq ]
		self.stdoutDeqList = []

		self.outDeq = False

		self.nodeStdinTh = NodeStdinTh(self)
		self.nodeStdoutTh = NodeStdoutTh(self)


	def nodeStatus(self) :
		retStr  = "[ %s = %s ]\n" % ( self.nodeName, self.progName )
		retStr += " NODE STATUS = { node status    : %s ,\n" % ( self.stat )
		retStr += "                 process pid    : %s ,\n" % ( self.pros.pid if self.stat == "ACT" else "-" )
		retStr += "                 last  in event : %s ,\n" % ( repr(self.lastInEvent) )
		retStr += "                 last out msg   : %s ,\n" % ( repr(self.lastOutEvent) )
		retStr += "                 last err msg   : %s ,\n" % ( repr(self.lastErrEvent) )
		retStr += "                 in  queue len  : %s ,\n" % ( len(self.broadcastDeq) )
		retStr += "                 out queue len  : %s }\n" % ( len(self.sharingDeq) )
		return retStr + "\n"


	def shutdownSet(self) :
		self.shutdown = True
		__LOG__.Trace("[%s] shutdownSet Called.." % self.nodeName)


	def act(self, autoAct=False) :

		if self.pros.poll() == None :
			__LOG__.Trace("-NOK : %s=%s : Already Alive" % (self.nodeName, self.progName))
			return ["-NOK : %s=%s : Already Alive\n" % (self.nodeName, self.progName)]
		else :
			self.actCnt += 1
			self.popenPros()

			self.actTime = time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime( time.time() ) )

			if autoAct :
				__LOG__.Trace("+OK ACT(auto react) : %s, %s=%s" % (self.prosPid, self.nodeName, self.progName))
			else :
				__LOG__.Trace("+OK ACT : %s, %s=%s" % (self.prosPid, self.nodeName, self.progName))
			return ["+OK ACT : %s=%s\n" % (self.nodeName, self.progName)]


	def term(self, autoTerm=False) :

		self.prosPid = '-'
		retList = []
		try :
			p = os.popen("ps --ppid %s | awk '{ print $1 }' | grep -v PID" % self.pros.pid).readlines()
		except :
			try :
				p = os.popen("""ps -ef | awk '{ if ($3 == %s) print $2 }'""" % self.pros.pid).readlines()	# has not --ppid option in Solaris
			except :
				p = []
			
		try :
			self.pros.terminate()
			__LOG__.Trace("[%s] terminate, autoTerminate : %s" % (self.nodeName, autoTerm))

			if self.pros.poll() == None :
				for sec in xrange(self.efClass.killWaitTime * 10) :
					if self.pros.poll() != None :
						break
					if sec+1 == self.efClass.killWaitTime * 10 : 
						self.pros.kill()
						__LOG__.Trace("[%s] kill -9 %s" % (self.nodeName, self.pros.pid))
						retList.append("[%s] kill -9 %s\n" % (self.nodeName, self.pros.pid))
						
						while self.pros.poll == None :
							time.sleep(0.1)
					time.sleep(0.1)

			__LOG__.Trace("+OK TRM : pid %s : %s=%s" % (self.pros.pid, self.nodeName, self.progName))
			retList.append("+OK TRM : %s=%s\n" % (self.nodeName, self.progName))

			for pid in p :
				try :
					os.kill(int(pid.strip()), 9)
					__LOG__.Trace("[%s] child PID Kill : %s" % (self.nodeName, pid.strip()))
					retList.append("[%s] child PID Kill : %s" % (self.nodeName, pid.strip()))
				except :
					pass
		
		except OSError, err :
			retList.append('-NOK : %s : Process Already Terminate\n' % self.nodeName)
			__LOG__.Trace('-NOK : %s : Process Already Terminate\n' % self.nodeName)

		except Exception, err :	# need for confirmation
			__LOG__.Trace( "[%s] Node Term Exception : %s" % ( self.nodeName, err ) )
			__LOG__.Exception()

		__LOG__.Trace("[%s] Process Exit Code : %s" % (self.nodeName, self.pros.poll()))

		return retList


	def popenPros(self) :
		try :
			if self.system != 'win' :
				self.pros = subprocess.Popen( self.progName, shell=True, bufsize=0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True )
			else :
				progNameList = shlex.split(self.progName)
				self.pros = subprocess.Popen( progNameList, shell=True, bufsize=0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

			self.prosPid = self.pros.pid

		except :
			__LOG__.Exception()
			while True :
				try :
					if self.pros.poll() == None :
						self.pros.terminate()
						sys.stderr.write("debug : Node : %s: popenPros term itself... \n" % self.nodeName)
						time.sleep(1)
						self.pros.kill()
						sys.stderr.write("debug : Node : %s: popenPros kill itself... \n" % self.nodeName)
						if self.shutdown or self.stat == "TRM" :
							break
					else :
						break
				except :
					break

			sys.stderr.write("[%s] : popenPros fail\n " % self.nodeName)


	def loadQueue(self) :

		retList = list()
		self.inputDumpFile = os.path.join( self.efClass.dumpDir, "%s_%s_input.dump" % ( self.efClass.dumpConfFile, self.nodeName ) )
		self.outputDumpFile = os.path.join( self.efClass.dumpDir, "%s_%s_output.dump" % ( self.efClass.dumpConfFile, self.nodeName ) )

		if os.path.exists(self.inputDumpFile) :
			fd = open(self.inputDumpFile, "r")
			cnt = 0
			for line in fd :
				self.broadcastDeq.append(line)
				cnt += 1
			fd.close()
			retList.append('+OK : %3s : %4s Events Loading : %s\n' % (self.nodeName, cnt, self.inputDumpFile))
		else :
			retList.append('-NOK : %3s : InputDump File Not Exists : %s\n' % (self.nodeName, self.inputDumpFile))

		if os.path.exists(self.outputDumpFile) :
			fd = open(self.outputDumpFile, "r")
			cnt = 0
			for line in fd :
				self.sharingDeq.append(line)
				cnt += 1
			fd.close()
			retList.append('+OK : %3s : %4s Events Loading : %s\n' % (self.nodeName, cnt, self.outputDumpFile))
		else :
			retList.append('-NOK : %3s : OutputDump File Not Exists : %s\n' % (self.nodeName, self.outputDumpFile))

		return retList


	def saveQueue(self) :

		retList = list()
		self.inputDumpFile = os.path.join( self.efClass.dumpDir, "%s_%s_input.dump" % ( self.efClass.dumpConfFile, self.nodeName ) )
		self.outputDumpFile = os.path.join( self.efClass.dumpDir, "%s_%s_output.dump" % ( self.efClass.dumpConfFile, self.nodeName ) )

		try :
			fd = open(self.inputDumpFile, "w")
			cnt = 0
			for line in self.broadcastDeq :
				fd.write(line)
				cnt += 1
			fd.close()
			retList.append('+OK : %3s : %4s Events Save : %s\n' % (self.nodeName, cnt, self.inputDumpFile))
		except : 
			retList.append('-NOK : %3s : Bad DumpFile Path : %s\n' % (self.nodeName, self.inputDumpFile))

		try :
			fd = open(self.outputDumpFile, "w")
			cnt = 0
			for line in self.sharingDeq :
				fd.write(line)
				cnt += 1
			fd.close()
			retList.append('+OK : %3s : %4s Events Save : %s\n' % (self.nodeName, cnt, self.outputDumpFile))
		except :
			retList.append('-NOK : %3s : Bad DumpFile Path : %s\n' % (self.nodeName, self.outputDumpFile))

		return retList


	def clearQueue(self) :

		evtCnt = 0
		try :
			while True :
				self.broadcastDeq.pop()
				evtCnt += 1
		except : pass
		try :
			while True :
				self.sharingDeq.pop()
				evtCnt += 1
		except : pass
		return "+OK : [%s] Node Queue Clear : %s events\n" % (self.nodeName, evtCnt)


	def put(self, msg) :
		self.broadcastDeq.append(msg)
		__LOG__.Trace("+OK : Put message [ %s <- %s ]" % (self.nodeName, repr(msg)))


	def setFlow(self) :	

		self.stdinDeqList = [ self.broadcastDeq ]
		self.stdoutDeqList = []

		for node in self.sharingNodeList :
			self.stdinDeqList.append( node.sharingDeq )

		if self.outDeq :
			self.stdoutDeqList.append( self.sharingDeq )
		for node in self.broadcastNodeList :
			self.stdoutDeqList.append( node.broadcastDeq )


	def run(self):

		try :
			self.loadQueue()
		except :
			__LOG__.Exception()
		self.setFlow()

		self.nodeStdinTh.start()
		self.nodeStdoutTh.start()

		self.stat = "ACT"

		while self.shutdown == False :

			if self.shutdown :
				break

			if self.pros.poll() != None and self.stat == "ACT" and self.shutdown == False :
				self.actStat = 'ABN'
				self.term(autoTerm=True)
				self.act(autoAct=True)
			else :
				self.actStat = 'OK'

			if self.shutdown :
				break

			time.sleep(1)

		self.stat = "TRM"
		self.term(autoTerm=True)
		self.nodeStdinTh.join()
		self.nodeStdoutTh.join()
		try :
			self.saveQueue()
		except :
			__LOG__.Exception()


	def waitClose(self) :
		self.join()



if __name__ == "__main__":
	node1 = Node("node1", "python ./ev1.py send")
	node2 = Node("node2", "python ./ev2.py recv-send")
	node3 = Node("node3", "python ./ev3.py recv1")
	node4 = Node("node4", "python ./ev4.py recv2")

	# node1 -B-> node2, node3
	node1.broadcastNodeList.append(node2)

	# node1 -S-> node2, node3
	node3.sharingNodeList.append(node2)
	node4.sharingNodeList.append(node2)

	node1.start()
	node2.start()
#	node3.start()
#	node4.start()

	print "THIS :", node1.stdinDeqList
	time.sleep(3)
	print node1.broadcastDeq
	print node1.sharingDeq
	print node2.broadcastDeq
	print node2.sharingDeq
#	node2.term()
	time.sleep(5)

	print "THIS :", node1.stdinDeqList
	print node1.broadcastDeq
	print node1.sharingDeq
	print node2.broadcastDeq
	print node2.sharingDeq
#	node2.act()

#	pdb.set_trace()

	time.sleep(10000)



	node1.join()
	node2.join()
	node3.join()
	node4.join()
