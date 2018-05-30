#!/bin/env python
#coding: utf-8

import threading
import os
import time
import collections
import sys
import select
import re
from datetime import datetime

import Mobigen.Common.Log as Log; Log.Init()

from NodeProcess import Node as NodeProcess


def stdLog( msg ) :
	__LOG__.Trace( msg )



class NodeStdinTh(threading.Thread):

	def __init__(self, node) :

		threading.Thread.__init__(self)
		self.node = node
		self.lastDeq = None


	def stdout(self) :

		while self.node.shutdown == False :

			if self.node.stat == "ACT" :
				try :
					processMsgCnt = 0

					for deq in self.node.stdinDeqList :
						self.lastDeq = deq
						try:
							putMsg = deq.popleft()
							processMsgCnt += 1

							self.node.lastInMsg = putMsg
							self.node.efClass.monDeq.append((str(datetime.now()), " IN -> %s" % (self.node.nodeName), repr(putMsg)))
							self.node.efClass.saveDeq.append( '%s %s  IN : %s' % ( datetime.now(), self.node.nodeName, repr(putMsg) ) )
							stdLog( "[%s] StdIN  = %s" % (self.node.nodeName, repr(putMsg)) )

							yield putMsg
						except:
							pass
	
						if self.node.shutdown :
							raise Exception
				except :
					break

				if processMsgCnt == 0:
					time.sleep(1)

			else :
				break


	def run(self) :

		while self.node.shutdown == False :
			#- ACT
			if self.node.stat == "ACT" :
				try :
					for msg in self.node.pros.stdio( self.stdout() ) :

						try :
							self.node.lastOutMsg = msg.strip()
							self.node.efClass.monDeq.append((str(datetime.now()), "%s -> OUT" % (self.node.nodeName), repr(msg)))
							self.node.efClass.saveDeq.append( '%s %s OUT : %s' % ( datetime.now(), self.node.nodeName, repr(msg) ) )
							stdLog( "[%s] StdOUT = %s" % (self.node.nodeName, repr(msg)) )

							self.node.prosQ.append(msg)

							if self.node.shutdown or self.node.stat == "TRM" :
								break

						except :
							__LOG__.Exception()
							pass

					if self.node.shutdown == False  and  self.node.stat == "ACT" :	# Stop Thread.sfio() Iteration
						__LOG__.Trace( "[%s] Thread.sfio() Stop Iteration" % (self.node.nodeName) )
						self.node.pros.poll = 1
						time.sleep(1)

				except Exception, err : # Exception Catch : thread.sfio()
					__LOG__.Trace( "[%s] Thread.sfio() Exception : %s" % (self.node.nodeName, err) )
					self.node.pros.poll = 1
					time.sleep(1)
			#- TERM
			else :
				time.sleep(1)



class NodeStdoutTh(threading.Thread) :

	def __init__(self, node):

		threading.Thread.__init__(self)
		self.node = node


	def run(self):

		while self.node.shutdown == False :
			#- ACT
			if self.node.stat == "ACT" :

				try :
					msg = self.node.prosQ.popleft()

					for deq in self.node.stdoutDeqList :
						while True :
							if len(deq) < self.node.efClass.maxCmdQSize or self.node.shutdown or self.node.stat == "TRM" :
								deq.append(msg)
								break
							else :
								__LOG__.Trace( "[%s] Queue Full Flush Event : %s" % ( self.node.nodeName, repr(deq.popleft()) ) )
				except :
					if self.node.shutdown :
						break
					time.sleep(1)
			#- TERM
			else :
				time.sleep(1)



class Node(NodeProcess, threading.Thread) :

	def __init__(self, nodeName, progName, efClass, **opt):
		threading.Thread.__init__(self)

		self.nodeName = nodeName
		self.progName = progName
		self.efClass = efClass

		self.lastInMsg = "-"
		self.lastOutMsg = "-"

		self.stat = "TRM"
		self.actStat = 'ABN'
		self.actTime = time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime( time.time() ) )
		self.shutdown = False
		self.actCnt = 1
		self.prosPid = '-'
		self.system = 'win' if 'win' in sys.platform else 'linux'

#		try    : self.maxCmdQSize = opt['maxQSize']
#		except : self.maxCmdQSize = 100000
#		try    : self.killWaitTime = opt["killWaitTime"]
#		except : self.killWaitTime = 9
#		try    : self.errorDataFileSkip = opt["errorDataFileSkip"]
#		except : self.errorDataFileSkip = False


#		self.monDeq = opt["monDeq"]
#		self.saveDeq = opt["saveDeq"]

#		self.inputDumpFile = os.path.join(opt["dumpDir"], "%s_%s_input.dump" % (opt["dumpConfFile"], self.nodeName))
#		self.outputDumpFile = os.path.join(opt["dumpDir"], "%s_%s_output.dump" % (opt["dumpConfFile"], self.nodeName))

		self.pros = None
		self.prosQ = collections.deque() # save queue if shutdown

		moduleName, self.constructStr = re.split("\s+", progName, 1)

		(libPath, classFileName) = os.path.split(moduleName)
		self.classFileName = os.path.splitext(classFileName)[0]

		if libPath not in sys.path :
			sys.path.append(libPath)

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

		retStr  = "[ %s=%s ]\n" % ( self.nodeName, self.progName )
		retStr += " NODE STATUS = { node status   : %s ,\n" % ( self.stat )
		retStr += "                 last  in msg  : %s ,\n" % ( self.lastInMsg.strip() )
		retStr += "                 last out msg  : %s ,\n" % ( self.lastOutMsg.strip() )
		retStr += "                 in queue len  : %s ,\n" % ( len(self.broadcastDeq) )
		retStr += "                 out queue len : %s }\n" % ( len(self.sharingDeq) )
		return retStr + "\n"


	def evaluation(self, type) :
		
		if type :
			exec "import %s " % self.classFileName 
			exec "reload( %s )" % self.classFileName 
			exec "self.pros = %s.%s" % ( self.classFileName, self.constructStr )
		else :
			exec( "from %s import *" % self.classFileName )	# How to reload module???
			exec( "self.pros = %s" % ( self.constructStr ) )

		self.pros.poll = None


	def popenPros(self) :
		try :
			self.evaluation(True)

		except Exception, err:
			class Dummy() :
				def __init__(self) : 
					self.poll = 1
				def stdio(self, itr) :
					raise Exception, "import Class Exception : %s" % err
			self.pros = Dummy()


	def act(self) :

		if self.pros.poll == None :
			return ["NOK : %s=%s : Already Alive\n" % (self.nodeName, self.progName)]
		else :
			self.popenPros()

			self.actCnt += 1
			self.actTime = time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime( time.time() ) )

			__LOG__.Trace("+OK ACT : %s=%s" % (self.nodeName, self.progName))
			return ["+OK : %s=%s\n" % (self.nodeName, self.progName)]


	def term(self) :

		self.pros.poll = 1
		self.lastInMsg = "-"
		self.lastOutMsg = "-"
		__LOG__.Trace("+OK TRM : [%s]" % self.nodeName)
		return ["+OK : %s=%s\n" % (self.nodeName, self.progName)]


	def run(self) :

		self.loadQueue()
		self.setFlow()

		self.nodeStdinTh.start()
		self.nodeStdoutTh.start()

		self.stat = "ACT"

		while self.shutdown == False :

			if self.shutdown :
				break

			if self.pros.poll != None and self.stat == "ACT" and self.shutdown == False :
				self.actStat = 'ABN'
				self.term()
				self.act()
			else :
				self.actStat = 'OK'

			if self.shutdown :
				break

			time.sleep(1)

		self.stat = "TRM"
		self.term()
#		self.nodeStdinTh.join()
		self.nodeStdoutTh.join()
		self.saveQueue()





if __name__ == "__main__":
	node1 = Node("node1", "send", "send.Send('send1')")
	node2 = Node("node2", "recv", "recv.Recv('recv1')")
	node3 = Node("node3", "recv", "recv.Recv('recv2')")

	# node1 -B-> node2, node3
	#node1.broadcastNodeList.append(node2)
	#node1.broadcastNodeList.append(node3)

	# node1 -S-> node2, node3
	node2.sharingNodeList.append(node1)
	node3.sharingNodeList.append(node1)

	node1.start()
	node2.start()
	node3.start()

	node1.shutdownSet()
	node2.shutdownSet()
	node3.shutdownSet()

	node1.join()
	node2.join()
	node3.join()
