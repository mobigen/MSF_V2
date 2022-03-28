#!/bin/env python
### Version 1.0 : 2013/12/24 : JungJM ###
###	  SIOEventFlow2 Initialize
###
### Version 1.1 : 2013/12/30 : JungJM ###
###   NodeProcess.py StdERR Read Bug Fixed
###   SIOEventFlow.py KIL : check subProcess poll
###
### Version 1.2 : 2014/01/02 : JungJM ###
###   NodeProcess.py : NodeStdinTh Sleep 1 second Bug Fixed
###   NodeProcess.py : Process Term ppid Search Change (ps --ppid -> awk)
###
### Version 1.3 : 2014/01/14 : JungJM ###
###  SIOEventFlow.py : Edit 'shw' Command format (ABN, PID, ACT_TIME  Added)
###   NodeProcess.py : Add abnStat, pid, act time
###   NodeProcess.py : Add abnStat, pid, act time
###
### Version 1.4 : 2014/02/07 : JungJM ###
###  SIOEventFlow.py : Edit option Argument **args -> self
###                    Whole Event Dump File
###   NodeProcess.py : BugFix : Windows subprocess.Popen Edit, option Argument Edit
###   NodeProcess.py : option Argument Edit
###
### Version 1.5 : 2014/03/10 : JungJM ###
###  SIOEventFlow.py : BugFix : Command "INI" -> Node Change Flow Bug
###
### Version 1.6 : 2014/04/02 : JungJM ###
###  SIOEventFlow.py : Edit Logging Formatting
###
### Version 1.7 : 2014/06/16 : JungJM ###
###  NodeProcess.py : Bug Fix : Window OS Subprocess open Error Clean
###
### Version 1.8 : 2014/07/03 : JungJM ###
###  SIOEventFlow.py : Add SHQ Command Function
###  NodeProcess.py  : Add SHQ Command Function
###
### Version 1.9 : 2014/07/04 : JungJM ###
###  SIOEventFlow.py : Split SHW Command -> SHW, CFG
###
### Version 2.0 : 2014/07/17 : JungJM ###
###  SIOEventFlow.py : Modify Term Function (threading)
###
### Version 2.1 : 2014/09/04 : JungJM ###
###  NodeProcess.py : Edit logging format, Edit STA Commands output format 
###
### Version 2.2 : 2014/10/16 : JungJM ###
###  SIOEF : DEBUG_MODE Flat Add, NodeProcess.py : Initialize STA Option
###
### Version 2.3 : 2014/11/13 : JungJM ###
###  NodeProcess.py : RES Command bug fixed (TRM -> ACT)
###
### Version 2.4 : 2014/11/25 : JungJM ###
###  SIOEventFlow.py : Add LDP, SDP Commands
###  NodeProcess.py  : Add LDP, SDP Commands
###
### Version 2.5 : 2015/03/09 : JungJM ###
###  SIOEventFlow.py : Edit to Logging Format
###  NodeProcess.py  : Edit to Logging Format, Stable Process Kill



import subprocess
import sys
import shlex
import copy
import select
import threading
import collections
import time
import pdb
import ConfigParser
import re
import os
import ctypes
import signal
import traceback
from datetime import datetime

from NodeProcess import Node as NodeProcess
from NodeThread  import Node as NodeThread

import Mobigen.Common.Log as Log; Log.Init()

try : import idebug
except : pass

__VERSION__ = 'Version 2.5 : Release 2015/03/09\n'

SHUTDOWN = False
DEBUG_MODE=False

HLP_STR = '''=============================================================================================
cmd | description                     | command format   | answer format
---------------------------------------------------------------------------------------------
act | activate node                   | act,nodeName     | OK or NOK
trm | terminate node                  | trm,nodeName     | OK or NOK
res | act/term restart node           | res,nodeName     | OK or NOK
put | put standard in to process      | put,nodeName,cmd | OK or NOK
clr | clear process event queue       | clr,nodeName     | OK or NOK
dif | diff memory conf and file conf  | dif              | result multi-string line
ini | reload file conf to memory conf | ini              | result multi-string line
shw | show process status             | shw              | result multi-string line
cfg | show memory config setting      | cfg              | result multi-string line
deq | show global deque               | deq              | result multi-string line
sta | show process status             | sta,nodeName     | result multi-string line
shq | show node event queue           | shq,nodeName     | result multi-string line
ldp | load dump file to queue         | ldp,nodeName     | result multi-string line
sdp | save dump file from queue       | sdp,nodeName     | result multi-string line
bye | session close                   | bye              | no answer
kil | shutdown                        | kil              | no answer
hlp | help                            | hlp              | result multi-string line
ver | show eventflow version          | ver              | result multi-string line
=============================================================================================
'''


def sigHandler(sigNum, frame) :
	global SHUTDOWN
	__LOG__.Trace( ">>>>> signal received : %s" % sigNum )
	SHUTDOWN = True

### signal handler ###
signal.signal(signal.SIGINT, sigHandler)			# signal  2 : interrupt
signal.signal(signal.SIGTERM, sigHandler)			# signal 15 : terminate
try : signal.signal(signal.SIGHUP, signal.SIG_IGN)	# signal  1 : hang up
except : pass
try : signal.signal(signal.SIGPIPE, signal.SIG_IGN)	# signal 13 : broken pipe
except : pass



class EventFlow(threading.Thread) :

	def __init__(self, confFileName) :

		threading.Thread.__init__(self)
	
		###################
		self.dumpDir = "."
		self.maxCmdQSize = 100000
		self.maxMonQSize = 1000
		self.killWaitTime = 9
		self.errorDataFileSkipFlag = False

		self.confFileName = confFileName
		self.nodeHash = dict()
		self.groupHash = dict()

		self.abnConfList = []

		self.monDeq = collections.deque( [], self.maxMonQSize )
		self.saveDeq = collections.deque( [], 1000 )
		self.saveEvtFileName = None
		self.confFileStr = ''
		###################

		self.initDiffConf( "INI" )


	def initDiffConf(self, cmd) :

		retStrList = []

		__LOG__.Trace("initDiffConf : cmd = [%s]" % cmd)

		confFile = ConfigParser.ConfigParser()
		confFile.read( self.confFileName )

		try : 
			processNodeItems = confFile.items('Process Node')
		except :
			try    : processNodeItems = confFile.items('Node')
			except : processNodeItems = []
			
		try    : threadNodeItems = confFile.items('Thread Node')
		except : threadNodeItems = []

		try :
			broadFlowItems = confFile.items('Broadcasting Flow')
		except :
			try    : broadFlowItems = confFile.items('Flow')
			except : broadFlowItems = []

		try    : shareFlowItems = confFile.items('Sharing Flow')
		except : shareFlowItems = []

		try    : groupItems = confFile.items('Group')
		except : groupItems = []

		dumpConfFile = re.split('\/', self.confFileName)[-1]
		self.dumpConfFile = re.sub('\.conf$', '', dumpConfFile)

		self.abnConfList = []

		### Read Conf File ###
		with open( self.confFileName, 'r' ) as fd :
			confFileStr = fd.read()
			if cmd == "INI" :
				self.confFileStr = confFileStr
		### Read Conf File ###

		### dump dir ###
		try    : dumpDir = os.path.expanduser(confFile.get("General", "dump dir"))
		except : dumpDir = os.getcwd()

		if self.dumpDir != dumpDir :
			retStrList.append( "OK : Dump Dir : %s -> %s\n" % (self.dumpDir, dumpDir) )
			if cmd == "INI" :
				self.dumpDir = dumpDir

				try :
					if not os.path.exists(self.dumpDir) :
						os.makedirs(self.dumpDir)
						__LOG__.Trace("initDiffConf : make dump dir = [%s]" % self.dumpDir)
				except Exception, err :
					self.abnConfList.append("Bad dump dir : %s\n" % self.dumpDir)
					__LOG__.Trace("initDiffConf : %s" % str(err) )
		### dump dir ###

		### event save file ###
		try : saveEvtFileName = confFile.get( "General", "event save file" )
		except : saveEvtFileName = '/dev/null'

		if self.saveEvtFileName != saveEvtFileName :
			retStrList.append( "OK : Event Save File : %s -> %s\n" % (self.saveEvtFileName, saveEvtFileName) )
			if cmd == "INI" :
				self.saveEvtFileName = saveEvtFileName
				try : os.makedirs( os.path.split( self.saveEvtFileName )[0] )
				except : pass
		### event save file ###

		### max global queue ###
		try : maxMonQSize = confFile.getint("General", "max monitor queue")
		except : maxMonQSize = 1000

		if self.maxMonQSize != maxMonQSize :
			retStrList.append( "OK : max monitor queue : %s -> %s\n" % ( self.maxMonQSize, maxMonQSize ) )
			if cmd == "INI" :
				self.maxMonQSize = maxMonQSize
				self.monDeq = collections.deque([], maxMonQSize)
		### max global queue ###

		### max cmd queue ###
		try : maxCmdQSize = confFile.getint("General", "max cmd queue")
		except : maxCmdQSize = 100000

		if self.maxCmdQSize != maxCmdQSize:
			retStrList.append( "OK : max cmd queue : %s -> %s\n" % (self.maxCmdQSize, maxCmdQSize) )
			if cmd == "INI" :
				self.maxCmdQSize= maxCmdQSize
		### max cmd queue ###

		### kill wait time ###
		try : killWaitTime = confFile.getint("General", "kill wait time")
		except : killWaitTime = 10

		if self.killWaitTime != killWaitTime :
			retStrList.append( "OK : kill wait time : %s -> %s\n" % (self.killWaitTime, killWaitTime) )
			if cmd == "INI" :
				self.killWaitTime = killWaitTime
		### kill wait time ###

		### error data file skip ###
		try : errorDataFileSkipFlag = confFile.get("General", "error data file skip")
		except : errorDataFileSkipFlag = "False"

		if errorDataFileSkipFlag.lower() == "true" :
			errorDataFileSkipFlag = True
		else :
			errorDataFileSkipFlag = False

		if self.errorDataFileSkipFlag != errorDataFileSkipFlag :
			retStrList.append( "OK : error data file skip : %s -> %s\n" % (self.errorDataFileSkipFlag, errorDataFileSkipFlag) )
			if cmd == "INI" :
				self.errorDataFileSkipFlag = errorDataFileSkipFlag
		### error data file skip ###

		### initialize ###
		if cmd == "INI" :
			newNodeThList = []
		### initialize ###

		### all confnode read ####
		confNode = {}
		for k,v in processNodeItems + threadNodeItems :
			nodeName = k.lower()
			if confNode.has_key( nodeName ) :
				if cmd == "INI" :
					self.abnConfList.append( "Bad Node Name : %s = %s\n" % ( nodeName, v ) )
			else :
				confNode[nodeName] = v
		### all confnode read ####

		### eventflow plugins setting ###
		EFMonitorNode = None
		for nodeName, progName in confNode.items() :
			if progName.startswith( 'EF' ) :
				if progName.startswith( 'EFMonitor' ) :
					EFMonitorNode = nodeName
				confNode[nodeName] = os.path.join( os.path.join( os.path.split( os.path.realpath( __file__ ) )[0], 'plugins' ), progName )
		### eventflow plugins setting ###

		### group setting ###
		confGroup = {}
		for k,v in groupItems :
			groupName = k.lower()
			nodeNameList = re.split( "\s*,\s*", v.lower() )

			resNodeNameList = []
			for nodeName in nodeNameList :
				if nodeName in confNode :
					resNodeNameList.append(nodeName)
				else :
					self.abnConfList.append( "Bad [Group] Section : %s = %s\n" % (groupName, nodeName) )

			if len(resNodeNameList) > 0 :
				confGroup[groupName] = resNodeNameList

		__LOG__.Trace ("11 : EventFlow : initDiffConf : confGroup = %s" % confGroup )

		for groupName, nodeNameList in confGroup.items() :
			try :
				if set( self.groupHash[groupName] ) != set( nodeNameList ) :
					oldGrpList = set( self.groupHash[groupName] )	
					newGrpList = set( nodeNameList )
					retStrList.append( "OK : %s -> %s\n" % (oldGrpList, newGrpList))
					if cmd == "INI" :
						self.groupHash[groupName] = nodeNameList
			except KeyError :
				__LOG__.Trace ("12 : initDiffConf  groupHash %s = %s" % (groupName, nodeNameList))
				self.groupHash[groupName] = nodeNameList
		### group setting ###

		### node process popen setting ###
		confThNode = [ nodeName for nodeName, progName in threadNodeItems ]
		confPsNode = [ nodeName for nodeName, progName in processNodeItems ]
		for nodeName, progName in confNode.items() :
			if nodeName in self.nodeHash :
				__LOG__.Trace("debug 33 : node[%s] = [%s] [%s]" % (nodeName, progName, self.nodeHash[nodeName].progName))
				if progName != self.nodeHash[nodeName].progName :
					retStrList.append( "OK : %s : %s -> %s\n" % (nodeName, self.nodeHash[nodeName].progName, progName) )

					if cmd == "INI" :
						self.nodeHash[nodeName].shutdownSet()
						self.nodeHash[nodeName].waitClose()
						# Thread Node
						if nodeName in confThNode :
							self.nodeHash[nodeName] = NodeThread(nodeName, progName, self)
						# Process Node
						else :
							self.nodeHash[nodeName] = NodeProcess(nodeName, progName, self)
						newNodeThList.append(self.nodeHash[nodeName])

			else :
				retStrList.append( "OK : new %s=%s\n" % (nodeName,progName) )

				if cmd == "INI" :
					# Thread Node
					if nodeName in confThNode :
						self.nodeHash[nodeName] = NodeThread(nodeName, progName, self)
					# Process Node
					else :
						self.nodeHash[nodeName] = NodeProcess(nodeName, progName, self)
					newNodeThList.append(self.nodeHash[nodeName])
		### node process popen setting ###

		### broadcasting flow setting ###
		broadFlow = {}
		for k, v in broadFlowItems :
			fromNodeName = k.lower()
			toNodeNameList = re.split( "\s*,\s*", v.lower() )

			resNodeNameList = []
			if fromNodeName in confNode :
				for toNodeName in toNodeNameList :
					if toNodeName in confNode :
						resNodeNameList.append(toNodeName)
					else :
						self.abnConfList.append( "Bad [Broadcast Flow] Section : bad toNodeName, %s = %s\n" % (fromNodeName, toNodeName) )
				broadFlow[fromNodeName] = resNodeNameList
			else :
				self.abnConfList.append( "Bad [Broadcast Flow] Section : bad fromNodeName = %s\n" % fromNodeName )
		### broadcasting flow setting ###

		###### EFMonitor setting ######
		if EFMonitorNode != None :
			for (nodeName, progName) in confNode.items() :
				if nodeName != EFMonitorNode :
					if not broadFlow.has_key( nodeName ) :
						broadFlow[nodeName] = list()
					broadFlow[nodeName].append( EFMonitorNode )

			try :
				for nodeName in broadFlow[EFMonitorNode] :
					broadFlow[nodeName].remove( EFMonitorNode )
			except :
				pass
		###### EFMonitor setting ######

		### self sharing flag setting ###
		if cmd == "INI" :
			for nodeName in self.nodeHash :
				self.nodeHash[nodeName].outDeq = False
			shareSelf = list()
			for nodeName in [ nodeName for nodeName, progName in shareFlowItems ] :
				if nodeName in confNode :
					shareSelf.append(nodeName)
			for nodeName in shareSelf :
				self.nodeHash[nodeName].outDeq = True
		### self sharing flag setting ###

		### sharing flow setting ###
		shareFlow = {}
		for k, v in shareFlowItems :
			fromNodeName = k.lower()
			toNodeNameList = re.split( "\s*,\s*", v.lower() )

			if fromNodeName in confNode :
				for toNodeName in toNodeNameList :
					if toNodeName in confNode :
						try :
							shareFlow[toNodeName].append(fromNodeName)
						except :
							shareFlow[toNodeName] = list()
							shareFlow[toNodeName].append(fromNodeName)
					else :
						self.abnConfList.append( "Bad [Share Flow] Section : bad toNodeName, %s = %s\n" % (fromNodeName, toNodeName) )
			else :
				self.abnConfList.append( "Bad [Share Flow] Section : bad fromNodeName = %s\n" % fromNodeName )
		### sharing flow setting ###

		### all node flow setting ###
		for nodeName in self.nodeHash :
			changeFlag = False

			### node broadflow setting ###
			try : oldBroadNodeNameList = [ broadNode.nodeName for broadNode in self.nodeHash[nodeName].broadcastNodeList ]
			except : oldBroadNodeNameList = []
			try : newBroadNodeNameList = broadFlow[nodeName]
			except : newBroadNodeNameList = []

			if set( oldBroadNodeNameList ) != set( newBroadNodeNameList ) :
				retStrList.append( "OK BroadcastingFlow : diff : %s : %s -> %s\n" % ( nodeName, oldBroadNodeNameList, newBroadNodeNameList ) )
				
			if cmd == "INI" :
				changeFlag = True
				try : self.nodeHash[nodeName].broadcastNodeList = [ self.nodeHash[broadcastNode] for broadcastNode in broadFlow[nodeName] ]
				except : self.nodeHash[nodeName].broadcastNodeList = []
			### node broadflow setting ###

			### node shareflow setting ###
			try : oldShareNodeNameList = [ shareNode.nodeName for shareNode in self.nodeHash[nodeName].sharingNodeList ]
			except : oldShareNodeNameList = []
			try : newShareNodeNameList = shareFlow[nodeName]
			except : newShareNodeNameList = []

			if set( oldShareNodeNameList ) != set( newShareNodeNameList ) :
				retStrList.append( "OK SharingFlow : diff : %s : %s -> %s\n" % ( nodeName, oldShareNodeNameList, newShareNodeNameList ) )

			if cmd == "INI" :
				changeFlag = True
				try : self.nodeHash[nodeName].sharingNodeList = [ self.nodeHash[shareNode] for shareNode in shareFlow[nodeName] ]
				except : self.nodeHash[nodeName].sharingNodeList = []
			### node shareflow setting ###

			if changeFlag :
				self.nodeHash[nodeName].setFlow()
		### all node flow setting ###

		### node close&start ###
		for nodeName in self.nodeHash.keys() :
			if nodeName not in confNode :
				retStrList.append( "OK : close %s\n" % (nodeName) )

				if cmd == "INI" :
					self.nodeHash[nodeName].shutdownSet()
					self.nodeHash[nodeName].waitClose()
					del( self.nodeHash[nodeName] )

		if cmd == "INI" :
			for th in newNodeThList :
				th.start()
		### node close&start ###

		__LOG__.Trace(">>>>>>>>>>>>>>>>>>>>>>>>>>>")
		__LOG__.Trace("retStrList = [%s]" % retStrList)
		return retStrList


	def initConf(self) :
		return self.initDiffConf( "INI" )


	def diffConf(self) :
		return self.initDiffConf( "DIF" )


	def showGlobalQueue(self) :
		try : return ["[%s] %10s : %s\n" % (qTime, nodeName, msg)  for (qTime, nodeName, msg) in self.monDeq ]
		except : return [""]


	def clr(self, nodeList) :

		retStrList = []
		if "all" in nodeList  or  "ALL" in nodeList :
			nodeList = self.nodeHash.keys()
			nodeList.sort()

		for nodeName in nodeList :
			if self.nodeHash.has_key(nodeName) :
				retStrList.append( self.nodeHash[nodeName].clearQueue() )
			else :
				retStrList.append( "[ %s ] node not exists\n" % nodeName )
		return retStrList
			

	def nodeStatus(self, nodeList) :

		retStrList = []
		if "all" in nodeList  or  "ALL" in nodeList  or  len( nodeList ) == 0 :
			nodeList = self.nodeHash.keys()
			nodeList.sort()

		for nodeName in nodeList :
			if self.nodeHash.has_key(nodeName) :
				retStrList.append( self.nodeHash[nodeName].nodeStatus() )
			else :
				retStrList.append( "[ %s ] node not exists\n" % nodeName )
		return retStrList


	def showQueue(self, words) :

		retStrList = []
		nodeName = words.pop(0)
		try :
			for msg in self.nodeHash[nodeName].broadcastDeq.__copy__() :
				retStrList.append( msg.strip() + '\n' )
			for shareNode in self.nodeHash[nodeName].sharingNodeList :
				for msg in shareNode.sharingDeq.__copy__() :
					retStrList.append( msg.strip() + '\n' )
		except KeyError, e :
			retStrList.append( "[ %s ] node not exists\n" % nodeName )
		except :
			__LOG__.Exception()
		return retStrList
	

	def config(self) :

		retStrList = []
		retStrList.append( "-" * 55 + "\n")
		retStrList.append( "dump dir         = %s\n" % self.dumpDir )
		retStrList.append( "max global queue = %s\n" % self.maxMonQSize )
		retStrList.append( "max local queue  = %s\n" % self.maxCmdQSize )
		retStrList.append( "kill wait time   = %s\n" % self.killWaitTime )
		retStrList.append( "error data skip  = %s\n" % self.errorDataFileSkipFlag )
		retStrList.append( "event save file  = %s\n" % self.saveEvtFileName )
		retStrList.append( "-" * 55 + "\n")

		prnNodeNameList = self.nodeHash.keys()
		prnNodeNameList.sort()

		for nodeName in prnNodeNameList : 
			retStrList.append( "node : %s = %s\n" % (nodeName, self.nodeHash[nodeName].progName) )
		retStrList.append( "-" * 55 + "\n")

		shareNodeNameList = []
		broadNodeNameList = []
		for nodeName in prnNodeNameList :
			broadNodeNameList = [ nextNodeObj.nodeName for nextNodeObj in self.nodeHash[nodeName].broadcastNodeList ]
			shareNodeNameList = [ nextNodeObj.nodeName for nextNodeObj in self.nodeHash[nodeName].sharingNodeList ]

			if len(broadNodeNameList) :
				retStrList.append( "broadcast flow : %s = %s\n" % (nodeName, ",".join( broadNodeNameList )) )
			if len(shareNodeNameList) :
				retStrList.append( "sharing flow   : %s = %s\n" % (",".join( shareNodeNameList ), nodeName ))

		retStrList.append( "-" * 55 + "\n")
		retStrList.extend( self.abnConfList )

		return retStrList


	def show(self) :

		retStrList = []
		retStrList.append( "-" * 110 + "\n")
		retStrList.append( " ABN |  NODE  | GROUP |  STATUS  |  PID  |    ACTIVATE TIME    | Q SIZE |  PROGRAM_NAME \n")
#		retStrList.append( "  OK |  ps01  |  ***  | ACT(001) | 54132 | 2014-01-14 13:43:12 |  0012  |  python ....../...//../xxx.py" )
		retStrList.append( "-" * 110 + "\n")

		prnNodeNameList = self.nodeHash.keys()
		prnNodeNameList.sort()

		groupNodeHash = {}
		for groupName in self.groupHash :
			for nodeName in self.groupHash[groupName] :
				if nodeName in prnNodeNameList :
					groupNodeHash[nodeName] = groupName

		for nodeName in prnNodeNameList :
			prnGrpName = '***'
			prnNextNodeName = '***'
			nextNodeNameList = [ nextNodeObj.nodeName for nextNodeObj in ( self.nodeHash[nodeName].broadcastNodeList + self.nodeHash[nodeName].sharingNodeList ) ]
			qSize = 0
			for NodeDeq in self.nodeHash[nodeName].stdinDeqList :
				qSize += len(NodeDeq)
			if nodeName in groupNodeHash : prnGrpName = groupNodeHash[nodeName]
			if len(nextNodeNameList) : prnNextNodeName = ",".join( nextNodeNameList )
			tmpProName = self.nodeHash[nodeName].progName
			if os.path.basename(tmpProName).startswith('EF') :
				tmpProName = os.path.basename(tmpProName)
			if len(self.nodeHash[nodeName].progName) > 120 :
				tmpProName = self.nodeHash[nodeName].progName[:120]
			prnOutStr = " {0: >3} |{1:^8}|{6:^7}| {2}({3:0>3}) | {4:^5} | {5} |{7:^8}| {8}\n".format( \
						self.nodeHash[nodeName].actStat, nodeName, self.nodeHash[nodeName].stat, self.nodeHash[nodeName].actCnt, \
						self.nodeHash[nodeName].prosPid, self.nodeHash[nodeName].actTime, prnGrpName, str(qSize).zfill(4), tmpProName )

			retStrList.append(prnOutStr)

		retStrList.append( "-" * 110 + "\n")

		return retStrList


	def actTermCall(self, termNode, retStrList) :
		retStrList.extend( termNode.term() )
		termNode.actCnt = 0


	def actTermNode(self, cmd, nodeNameList) :

		retStrList = []
		thList = []

		if  nodeNameList[0].upper() == 'ALL' :
			nodeNameList = self.nodeHash.keys()
		nodeNameList.sort()

		for entryName in nodeNameList :
			try :
				nodeName = entryName
				if cmd == "ACT" :
					retStrList.extend( self.nodeHash[nodeName].act() )
					self.nodeHash[nodeName].stat = "ACT"
				else :
					self.nodeHash[nodeName].stat = "TRM"
					thList.append( threading.Thread(target=self.actTermCall, args=[self.nodeHash[nodeName], retStrList]) )

			except KeyError :
				try :
					groupName = entryName
					for nodeName in self.groupHash[groupName] :
						try :
							if cmd == "ACT" :
								retStrList.extend( self.nodeHash[nodeName].act() )
								self.nodeHash[nodeName].stat = "ACT"
							else :
								self.nodeHash[nodeName].stat = "TRM"
								thList.append( threading.Thread(target=self.actTermCall, args=[self.nodeHash[nodeName], retStrList]) )

						except KeyError :
							retStrList.append("NOK : %s : process node name not exist\n" % groupName)
				except KeyError :
					retStrList.append("NOK : %s : process node name not exist\n" % groupName)

		for thObj in thList :
			thObj.daemon = True
			thObj.start()
		for thObj in thList :
			thObj.join()

		return retStrList
	

	def actNode( self, nodeNameList ) :
		return self.actTermNode( "ACT", nodeNameList )


	def termNode( self, nodeNameList ) :
		return self.actTermNode( "TRM", nodeNameList )


	def put(self, nodeName, msgList) :

		if nodeName not in self.nodeHash.keys() and nodeName not in self.groupHash.keys() :
			return "-NOK : %s : process node name not exists\n" % nodeName

		for msg in msgList :
			self.nodeHash[nodeName].put(msg.rstrip() + "\n")
		if len( msgList.__str__() ) > 100 :
			return "+OK : put %s event %s..] -> %s Queue\n" % (len(msgList), msgList.__str__()[:100], nodeName)
		else :
			return "+OK : put %s event %s -> %s Queue\n" % (len(msgList), msgList.__str__(), nodeName)


	def saveEvent(self) :

		while not SHUTDOWN :
			try : 
				msg = self.saveDeq.popleft()
				with open( self.saveEvtFileName, 'a' ) as fd :
					fd.write( msg + '\n' )
			except : 
				time.sleep(1)
				continue


	def loadSaveQueue(self, cmd, nodeNameList) :

		if nodeNameList[0].upper() == 'ALL' :
			nodeNameList = self.nodeHash.keys()
		nodeNameList.sort()

		retStrList = list()
		for nodeName in nodeNameList :

			try :
				if cmd == 'LDP' :
					retStrList.extend( self.nodeHash[nodeName].loadQueue() )
				else :
					retStrList.extend( self.nodeHash[nodeName].saveQueue() )

			except KeyError :
				try :
					groupName = nodeName
					for groupNodeName in self.groupHash[groupName] :
						if cmd == 'LDP' :
							retStrList.extend( self.nodeHash[nodeName].loadQueue() )
						else :
							retStrList.extend( self.nodeHash[nodeName].saveQueue() )

				except KeyError :
					retStrList.append("-NOK : %s : process node name not exist\n" % nodeName)

		return retStrList


	def guiCmd(self, cmd, words) :
	
		if cmd == 'GSHW' :
			ret = self.EFGuiCommand.xxx(words)

		elif cmd == 'GSTA' :
			ret = self.EFGuiCommand.xxx(words)

		return ret


	def run(self) :

		thObj = threading.Thread( target=self.saveEvent )
		thObj.setDaemon( True )
		thObj.start()

		while not SHUTDOWN :
			time.sleep(1)
	
		__LOG__.Trace(">>> while break")
		for node in self.nodeHash :
			self.nodeHash[node].shutdownSet()

		for node in self.nodeHash :
			__LOG__.Trace ("14 : EventFlow : run : %s wait" % self.nodeHash[node].nodeName)
			self.nodeHash[node].waitClose()
			try : 
				__LOG__.Trace ("14 : EventFlow : run : %s joined  process poll : %s" % ( self.nodeHash[node].nodeName, self.nodeHash[node].pros.poll() ))
			except :
				__LOG__.Trace ("14 : EventFlow : run : %s joined" % ( self.nodeHash[node].nodeName))
		__LOG__.Trace("System Exit")
		os._exit(1)



class SIOEventFlow(threading.Thread) :
	def __init__(self, confFileName) :
		threading.Thread.__init__(self)
		self.eventFlow = EventFlow(confFileName)
		self.eventFlow.start()
		__LOG__.Trace(">>> SIOEvent Thread : eventFlow start")

	def retFmt(self, line) :
		return "<begin>\n%s<end>\n" % line
		
	def sfio(self, line) :
		global SHUTDOWN

		words = line.strip().split(',')
		if len(words) == 0 :
			return None

		cmd = words.pop(0).upper()

		__LOG__.Trace("***************************")
		__LOG__.Trace("******* 1 : SIOEventFlow : sfio : [%s]" % cmd)
		__LOG__.Trace("***************************")

		if cmd == "SHW" :
			retStrList = self.eventFlow.show()
			res = "%s" % "".join(retStrList)
			return self.retFmt(res)

		if cmd == "CFG" :
			retStrList = self.eventFlow.config()
			res = "%s" % "".join(retStrList)
			return self.retFmt(res)

		elif cmd[:3] == "KIL" :
			SHUTDOWN = True
			self.eventFlow.join()
			return None

		elif (cmd == "ACT" or cmd == "TRM") and len(words) >= 1 :
			nodeNameList = words
			if cmd == "ACT" :
				retStrList = self.eventFlow.actNode(nodeNameList)
			else :
				retStrList = self.eventFlow.termNode(nodeNameList)

			res = "%s" % "".join(retStrList)
			return self.retFmt(res)

		elif cmd == "RES" :
			nodeNameList = words
			retStrList  = self.eventFlow.termNode(nodeNameList)
			retStrList += self.eventFlow.actNode(nodeNameList)
			res = "%s" % "".join(retStrList)
			return self.retFmt(res)

		elif cmd == "DIF" : 
			retStrList = self.eventFlow.diffConf()
			res = "%s" % "".join(retStrList)
			return self.retFmt(res)
		
		elif cmd == "INI" : 
			res =  "%s" % "".join(self.eventFlow.initConf())
			return self.retFmt(res)
		
		elif cmd == "HLP" :
			res =  "%s" % HLP_STR
			return self.retFmt(res)

		elif cmd == "DEQ" :
			res = "%s" % "".join(self.eventFlow.showGlobalQueue())
			return self.retFmt(res)

		elif cmd == "CLR" :
			res = "%s" % "".join(self.eventFlow.clr(words))
			return self.retFmt(res)

		elif cmd == "STA" :
			res = "%s" % "".join(self.eventFlow.nodeStatus(words))
			return self.retFmt(res)

		elif cmd == "PUT" :
			nodeName = words.pop(0)
			res = self.eventFlow.put(nodeName, words)
			return self.retFmt(res)

		elif cmd == "SHQ" :
			res = "%s" % "".join(self.eventFlow.showQueue(words))
			return self.retFmt(res)

		elif cmd == "VER" :
			res = "%s" % __VERSION__
			return self.retFmt(res)

		elif (cmd == "LDP" or cmd == "SDP")  and len(words) >= 1 :
			res = self.eventFlow.loadSaveQueue(cmd, words)
			return self.retFmt( ''.join(res) )

		elif cmd == "DBG" :
			res = 'Execute Fail'
			try : res = eval ( '%s' % ','.join(words) )
			except : 
				try : exec ( '%s' % ','.join(words) )
				except : __LOG__.Exception()
			return self.retFmt('%s\n' % res)

		elif cmd[:1] == "G" :	# GUI Only Commands
			res = self.eventFlow.guiCmd(cmd, words)
			return self.retFmt(res)

		else :
			return self.retFmt("Invalid Commands : [%s] Show Help Message Command : HLP\n" % cmd)


	def run(self) :
		while(True) :
			try :
				line = sys.stdin.readline()
			except IOError :
				__LOG__.Exception()
				break
				
			try :
				cmd = line[:3].upper()

				if line == "\n" :
					pass
				elif line == "" :
					break
				elif cmd == "BYE" or cmd == "KIL" :
					self.sfio("KIL\n")
					break
				else :
					ansStr = self.sfio(line)
					if ansStr != None :
						sys.stdout.write(ansStr)
						sys.stdout.flush()

			except :
				__LOG__.Exception()

		__LOG__.Trace(">>> SIOEvent Thread : eventFlow join")



def main() :
	global DEBUG_MODE
	DEBUG_MODE = True
	if len(sys.argv) < 2 or len(sys.argv) > 3 :
		print ("usage: %s confFileName [clear]" % sys.argv[0])
		sys.exit()
	
	### Make Config ###
	__LOG__.Trace("--------------------------------------------")
	__LOG__.Trace(" START !!!!!!")

	confFileName = sys.argv[1]

	ef = SIOEventFlow(confFileName)
	__LOG__.Trace(">>> main : debug 1 : ")
	ef.run()
	
if __name__ == "__main__" : 
	import Mobigen.Common.Log as Log;
	import sys, os, getopt; OPT, ARGS = getopt.getopt(sys.argv[1:], 'd')
	LOG_NAME = '~/SIOEF/%s.log' % (os.path.basename(sys.argv[0]))

	try : OPT.index(('-d', '')); Log.Init()
	except : Log.Init(Log.CRotatingLog(os.path.expanduser(LOG_NAME), 1000000, 5))
	sys.argv = [sys.argv[0]] + ARGS

	main()

