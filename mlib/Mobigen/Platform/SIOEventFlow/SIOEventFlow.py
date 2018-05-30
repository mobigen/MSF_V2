#!/bin/env python
### Version 0.1 : 111004 : tesse ###
### Version 0.1.1 : 111031 : seory ###
###		class Node: def term ###
###		class EventFlow: def run ###
### Version 0.1.2 : 120216 : seory ###
###     class Node: def term ###
###         add function of child processes of a node when node is terminated
### Version 0.1.3 : 120220 : seory ###
###     class EventFlow : add self.delayTerm

import subprocess, sys, shlex, select, threading, collections, time, ConfigParser, re, os, signal, types
import Mobigen.Common.Log as Log

SHUTDOWN = False

HLP_STR = '''=============================================================================================
cmd | description                     | command format | answer format
---------------------------------------------------------------------------------------------
kil | shutdown                        | kil            | no answer
bye | session kill                    | bye            | no answer
act | activate node                   | act,nodeName   | OK or NOK
trm | terminate node                  | trm,nodeName   | OK or NOK
dif | diff memory conf and file conf  | dif            | result multi-string line
ini | reload file conf to memory conf | ini            | result multi-string line
shw | show memory conf                | shw            | result multi-string line
hlp | help                            | hlp            | result multi-string line
=============================================================================================
'''

def db(line) :
	sys.stderr.write( "debug : %s\n" % line )
	sys.stderr.flush()

def errPrn(line) :
	#sys.stderr.write( "debug : %s\n" % line )
	#sys.stderr.flush()
	__LOG__.Trace(">> debug : %s" % line)
	pass

def logPrn(line) :
	#sys.stderr.write( "log : %s\n" % line )
	#sys.stderr.flush()
	__LOG__.Trace("======= [%s]" % line)

def sigHandlerCHLD(sigNum, f) :
	pass

def sigHandler(sigNum, f) :
	global SHUTDOWN
	errPrn( ">>>>> sigHandler : signal received = %s" % sigNum )
	signal.signal(signal.SIGINT, signal.SIG_IGN)	
	signal.signal(signal.SIGTERM, signal.SIG_IGN)	
	#signal.signal(signal.SIGPIPE, signal.SIG_IGN)	
	SHUTDOWN = True

### signal handler ###
signal.signal(signal.SIGCHLD, sigHandlerCHLD)
signal.signal(signal.SIGINT, sigHandler)
signal.signal(signal.SIGTERM, sigHandler)
#signal.signal(signal.SIGPIPE, sigHandler)

class Node(threading.Thread) :
	def __init__(self, nodeName, progName, fdHash, readList, dumpDir, dumpConfFile, **args) :
		threading.Thread.__init__(self)
		self.shutdown = False
		self.stat = "TRM"
		self.actCnt = 0

		maxQueueLen = args["maxQueueLen"]
		self.killWaitTime = args["killWaitTime"]
		self.errorDataFileSkip = args["errorDataFileSkip"]
		self.delayTerm = args["delayTerm"]

		self.queue = collections.deque([],maxQueueLen)
		self.nodeName = nodeName
		self.progName = progName

		#processName = re.split('\/', self.progNameList[0])[-1]
		try :
			self.dumpFileName = "%s/%s_%s.dump" % (dumpDir, dumpConfFile, nodeName) 
		except :
			self.dumpFileName = "%s/%s.dump" % (dumpDir, dumpConfFile)

		self.fdHash = fdHash
		self.readList = readList

		self.pros = None
		self.act()
		self.nextNodeList = []

		self.loadQueue()

	def shutdownSet(self) :
		#errPrn("00 : Node : %s:shutdown : call" % self.nodeName)
		__LOG__.Trace("Node : %s: shutdown : call" % self.nodeName)	
		self.shutdown = True

	def popenPros(self) :
		try :
			#self.pros = subprocess.Popen( self.progName, shell=False, bufsize=0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
			progNameList = shlex.split(self.progName)
			self.pros = subprocess.Popen(progNameList, bufsize=0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)

			self.fdHash[self.pros.stdout] = self
			self.readList.append(self.pros.stdout)
		except Exception, err :
			while True :
				try :
					if self.pros.poll() == None :
						self.pros.terminate()
						time.sleep(1)
						self.pros.kill()
						__LOG__.Trace("Node : %s: popenPros kill itself... " % self.nodeName)	
					else :
						break
				except Exception, err :
					break

			__LOG__.Trace("Node : %s: popenPros fail " % self.nodeName)	

	def act(self) :
		if self.pros == None :  # initial start  or first act
			self.popenPros()
			self.actCnt += 1
			return ["OK : %s=%s\n" % (self.nodeName, self.progName)]
		else :
			if self.pros.poll() == None :
				return ["NOK : %s=%s : already alive\n" % (self.nodeName, self.progName)]
			else :
				self.popenPros()
				self.actCnt += 1
				return ["OK : %s=%s\n" % (self.nodeName, self.progName)]

	def term(self) :
		logPrn("[%s] term mode start" % (self.nodeName))

		retStrList = []

		### get child pid of node ###
		nodeChildPidList = []
		try :
			ppid = self.pros.pid
			p = os.popen('ps --ppid %s' % ppid)
			__LOG__.Trace("DB 00 : ppid = %s" % ppid)
			
			for line in p.readlines() :
				line = line.strip()
				if line == '' : continue
				lineList = re.split('\s+', line)
				if lineList[0] == 'PID' : continue
				__LOG__.Trace("DB 00 : tmpPid = [%s]" % line)
				try : 
					tmpPid = int(lineList[0])
					nodeChildPidList.append(tmpPid)
				except Exception, err : 
					__LOG__.Exception()
					pass	
			p.close()
		except :
			pass

		try :
			self.pros.terminate()
			time.sleep(1)

			if self.pros.poll() == None :
				time.sleep(self.killWaitTime)
				self.pros.kill()
				__LOG__.Trace("[%s] kill -9" % (self.nodeName))
				retStrList = ["OK : %s : kill -9 after %s sec\n" % (self.nodeName, self.killWaitTime)]
			else :
				__LOG__.Trace("[%s] kill " % (self.nodeName))
				retStrList = ["OK : %s\n" % (self.nodeName)]

			while True :
				time.sleep(1)
				try :
					if self.pros.poll() == None :
						self.pros.kill()
						__LOG__.Trace("Node : %s: term : kill itself... " % self.nodeName)	
					else :
						break
				except Exception, err :
					break

			for childPid in nodeChildPidList :
				try : 
					os.kill(int(childPid), 9)	
					__LOG__.Trace("[%s] child PID kill -9" % (childPid))
					retStrList = ["OK : CHILD PID[%s] kill -9\n"  % childPid]
				except : 
					__LOG__.Trace("[%s] already terminated" % (childPid))

		except OSError :
			#db( "step 8" )
			__LOG__.Trace("[%s] already terminated" % (self.nodeName))
			retStrList = ["OK : %s : already terminated\n" % (self.nodeName)]
		except  Exception, err :
			__LOG__.Trace(">>>>>>>>>> ERR 01 >>>>>>>>>>>>>>>>")
			__LOG__.Exception()

		### version 0.1.1 ###
		try : del( self.fdHash[self.pros.stdout] )
		except AttributeError : logPrn(">>>> 1111 >>>> [%s]" % self.pros.stdout)
		except Exception, err : logPrn(">>>> 2222 >>>> [%s]" % err)

		#except KeyError : pass
		try : self.readList.remove( self.pros.stdout )
		except AttributeError : logPrn(">>>> 3333 >>>> [%s]" % self.pros.stdout)
		except Exception, err : logPrn(">>>> 4444 >>>> [%s]" % err)
		#except ValueError : pass

		return retStrList

	def saveQueue(self) :
		fd = open( self.dumpFileName, "w" )
		for line in self.queue :
			#errPrn( "02 : [%s] saveQueue : %s" % (self.nodeName, line ))
			fd.write( "%s\n" % line )
		fd.close()
	
	def loadQueue(self) :
		if os.path.exists( self.dumpFileName ) :
			fd = open( self.dumpFileName )
			for line in fd :
				self.queue.append( line.strip() )
			fd.close()

	def run(self) :
		self.stat = "ACT"

		while( self.shutdown == False ) :
			if self.stat == "ACT" :
				try :
					inMsg = None
					if self.pros.poll() != None :
						raise IOError

					try :
						inMsg = self.queue.popleft()
		
					except IndexError :
						time.sleep(1)
						continue
	
					self.pros.stdin.write( "%s\n" % inMsg )
					self.pros.stdin.flush()
					__LOG__.Trace( "[%s] : *** buf->stdin *** : inMsg = [%s]" % (self.nodeName, inMsg) )
		
					while True :
						if self.pros.poll() != None :
							raise IOError

						readReady, writeReady, exReady = select.select( [self.pros.stderr], [], [], 1)

						if self.shutdown == True :
							break

						if len(readReady) > 0 :
							cptMsg = self.pros.stderr.readline()

							if cptMsg == "\n" :
								continue
							elif cptMsg == "" :
								#db( "step a3" )
								#errPrn ("05 : Node : run : %s : cptMsg=[%s]" % (self.nodeName, cptMsg))
								__LOG__.Trace(">>> [%s] : Node : run : cptMsg=[%s]" % (self.nodeName, cptMsg))
								raise IOError
	
							else :
								cptMsg = cptMsg.strip()
		
								if cptMsg == inMsg :
									#db( "step a2" )
									__LOG__.Trace( "[%s] : *** stderr->node *** : Node :  stderrMsg = [%s]" % (self.nodeName, inMsg) )
									## 2012-02-20 add
									if self.delayTerm > 0 : 
										__LOG__.Trace( "**** DB 3333 : [%s] : >>>> sleep DELAY TERM  %s" % (self.nodeName, self.delayTerm))
										time.sleep(self.delayTerm)
									break
								else :
									#db( "step a4" )
									#errPrn ("06 : Node : run : %s : cptMsg=[%s]" % (self.nodeName, cptMsg))
									__LOG__.Trace(">>> [%s] : Node : run : cptMsg=[%s]" % (self.nodeName, cptMsg))
					#while True :
		
				# except IOError :
				except Exception, err :
					__LOG__.Exception()
					#db( "step a5" )

					if not self.errorDataFileSkip and inMsg != None :
						self.queue.appendleft(inMsg)
						__LOG__.Trace(">>> [%s:%s] : Node : run : inMsg recoverd : %s " % (self.nodeName,self.stat,inMsg))
	
					if self.shutdown == True :
						break
		
					#db( "step a6" )
					__LOG__.Trace(">>> [%s:%s] : Node : run : IOError " % (self.nodeName,self.stat ))
	
					if self.stat == "ACT" :
						self.term()
						self.act()

					time.sleep(1)

			else :
				time.sleep(1)

		self.saveQueue()
		__LOG__.Trace("[%s] Node : run : term call" % (self.nodeName))
		self.term()

	def waitClose(self) :
		while True :
			if self.pros.stdout in self.readList :
				time.sleep(1)
			else :
				break
		
	def put(self, msg) :
		self.queue.append(msg)
		__LOG__.Trace( "[%s:%s] : putMsg = [%s]" % (self.nodeName,self.progName, msg) )

class EventFlow(threading.Thread) :
	def __init__(self, confFileName) :
		threading.Thread.__init__(self)
	
		###################
		self.dumpDir = "."
		self.maxCmdQ = 10000
		self.killWaitTime = 10
		self.delayTerm = 0
		self.errorDataFileSkipVal = False

		self.confFileName = confFileName
		self.nodeHash = None
		self.fdHash = None
		self.readList = None
		self.groupHash = None

		self.abnConfList = []
		###################

		self.initConf()

	def initDiffConf(self, cmd) :
		retStrList = []

		logPrn("initDiffConf : cmd = [%s]" % cmd)

		confFile = ConfigParser.ConfigParser()
		confFile.read( self.confFileName )

		dumpConfFile = re.split('\/', self.confFileName)[-1]
		dumpConfFile = re.sub('\.conf$', '', dumpConfFile)

		self.abnConfList = []
		### dump dir ###
		dumpDir = confFile.get("General", "dump dir")
		if self.dumpDir != dumpDir :
			retStrList.append( "OK : %s -> %s\n" % (self.dumpDir, dumpDir) )
			if cmd == "INI" :
				self.dumpDir = dumpDir

				try :
					if not os.path.exists(self.dumpDir) :
						os.mkdir(self.dumpDir)
						logPrn("initDiffConf : make dump dir = [%s]" % self.dumpDir)
				except Exception, err :
					self.abnConfList.append("Bad dump dir : %s\n" % self.dumpDir)
					errPrn("initDiffConf : %s" % str(err) )

		### max cmd queue ###
		try : maxCmdQ = confFile.getint("General", "max cmd queue")
		except : maxCmdQ = 10000

		if self.maxCmdQ != maxCmdQ :
			retStrList.append( "OK : max cmd queue : %s -> %s\n" % (self.maxCmdQ, maxCmdQ) )
			if cmd == "INI" :
				self.maxCmdQ = maxCmdQ

		### kill wait time ###
		try : killWaitTime = confFile.getint("General", "kill wait time")
		except : killWaitTime = 10

		if self.killWaitTime != killWaitTime :
			retStrList.append( "OK : kill wait time : %s -> %s\n" % (self.killWaitTime, killWaitTime) )
			if cmd == "INI" :
				self.killWaitTime = killWaitTime

		### delay term ###
		try : delayTerm = confFile.getint("General", "delay term")
		except : delayTerm = 0

		if self.delayTerm != delayTerm :
			retStrList.append( "OK : delay term : %s -> %s\n" % (self.delayTerm, delayTerm) )
			if cmd == "INI" :
				self.delayTerm = delayTerm

		### error data file skip ###
		try : errorDataFileSkipVal = confFile.get("General", "error data file skip")
		except : errorDataFileSkipVal = "False"

		if errorDataFileSkipVal.lower() == "true" :
			errorDataFileSkipVal = True
		else :
			errorDataFileSkipVal = False

		if self.errorDataFileSkipVal != errorDataFileSkipVal :
			retStrList.append( "OK : error data file skip : %s -> %s\n" % (self.errorDataFileSkipVal, errorDataFileSkipVal) )
			if cmd == "INI" :
				self.errorDataFileSkipVal = errorDataFileSkipVal

		### conf read ####
		confNode = {}
		for k,v in confFile.items("Node") :
			nodeName = k.lower()
			tmpList = re.split("\s+", v)

			### java check ###
			if re.search( "java$", tmpList[0] ) :
				javaFileExist = True
				for tmpFileName in tmpList :
					if re.search( "\.jar$", tmpFileName ) :
						if not os.path.exists( tmpFileName ) :
							javaFileExist = False
							break

				if javaFileExist :
					confNode[nodeName] = v
					errPrn("debug 01 confNode[%s] = %s" % (nodeName, v))
					logPrn ("07: EventFlow : initDiffConf : %s = %s" % (k,v) )
				else :
					self.abnConfList.append( "Bad [Node] Section : %s = %s\n" % (k,v) )
					errPrn ("08: EventFlow : initDiffConf : java file not exist %s = %s" % (k,v) )
			else :
				exeFileName = tmpList[0]
				if os.path.exists( exeFileName ) :
					confNode[nodeName] = v
					errPrn("debug 02 confNode[%s] = %s" % (nodeName, v))
					logPrn ("09: EventFlow : initDiffConf : %s = %s" % (k,v) )
				else :
					self.abnConfList.append( "Bad [Node] Section : %s = %s\n" % (k,v) )
					logPrn ("10: EventFlow : initDiffConf : exe file not exist %s = %s" % (k,v) )

		confGroup = {}
		for k,v in confFile.items("Group") :
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

		errPrn ("11 : EventFlow : initDiffConf : confGroup = %s" % confGroup )

		confFlow = {}
		for k,v in confFile.items("Flow") :
			fromNodeName = k.lower()
			toNodeNameList = re.split( "\s*,\s*", v.lower() )

			resNodeNameList = []
			if fromNodeName in confNode :
				for toNodeName in toNodeNameList :
					if toNodeName in confNode :
						resNodeNameList.append(toNodeName)
					else :
						self.abnConfList.append( "Bad [Flow] Section : bad toNodeName, %s = %s\n" % (fromNodeName, toNodeName) )

				confFlow[fromNodeName] = resNodeNameList
			else :
				self.abnConfList.append( "Bad [Flow] Section : bad fromNodeName = %s\n" % fromNodeName )

		errPrn ("09 : EventFlow : nitDiffConf : confFlow = %s" % confFlow)
	
		if cmd == "INI" :
			if self.nodeHash == None : self.nodeHash = {}
			if self.fdHash == None : self.fdHash = {}
			if self.readList == None : self.readList = []
			if self.groupHash == None : self.groupHash = {}

			newNodeThList = []

		for groupName, nodeNameList in confGroup.items() :
			try :
				if set( self.groupHash[groupName] ) != set( nodeNameList ) :
					oldGrpList = set( self.groupHash[groupName] )	
					newGrpList = set( nodeNameList )
					retStrList.append( "OK : %s -> %s\n" % (oldGrpList, newGrpList))
					if cmd == "INI" :
						self.groupHash[groupName] = nodeNameList
			except KeyError :
				errPrn ("12 : initDiffConf  groupHash %s = %s" % (groupName, nodeNameList))
				self.groupHash[groupName] = nodeNameList

	
		for nodeName, progName in confNode.items() :
			if nodeName in self.nodeHash :
				errPrn("debug 33 : node[%s] = [%s] [%s]" % (nodeName, progName, self.nodeHash[nodeName].progName))
				if progName != self.nodeHash[nodeName].progName :
					retStrList.append( "OK : %s -> %s\n" % (self.nodeHash[nodeName].progName, progName) )

					if cmd == "INI" :
						self.nodeHash[nodeName].shutdownSet()
						self.nodeHash[nodeName].waitClose()
						self.nodeHash[nodeName] = Node(nodeName, progName, self.fdHash, self.readList, self.dumpDir, dumpConfFile, errorDataFileSkip=self.errorDataFileSkipVal, maxQueueLen=self.maxCmdQ, killWaitTime=self.killWaitTime, delayTerm=self.delayTerm)
						newNodeThList.append(self.nodeHash[nodeName])

			else :
				retStrList.append( "OK : new %s=%s\n" % (nodeName,progName) )

				if cmd == "INI" :
					self.nodeHash[nodeName] = Node(nodeName, progName, self.fdHash, self.readList, self.dumpDir, dumpConfFile, errorDataFileSkip=self.errorDataFileSkipVal, maxQueueLen=self.maxCmdQ, killWaitTime=self.killWaitTime, delayTerm=self.delayTerm)
					newNodeThList.append(self.nodeHash[nodeName])

		for nodeName in self.nodeHash :
			if nodeName not in confNode :
				retStrList.append( "OK : close %s\n" % (nodeName) )

				if cmd == "INI" :
					self.nodeHash[nodeName].shutdownSet()

		for fromNodeName, nodeList in confFlow.items() :
			curList = self.nodeHash[fromNodeName].nextNodeList
			confList = []
			for toNodeName in nodeList :
				if toNodeName in self.nodeHash : 
					confList.append(self.nodeHash[toNodeName])
				else : 
					retStrList.append( "OK : Flow : new : fromNodeName[%s]->toNodeName[%s]\n" % (fromNodeName,toNodeName))
					if toNodeName in confNode :
						confList.append(confNode[toNodeName])

			if set( curList ) != set( confList ) :
				#errPrn("initConf : new : %s" % set(confList))

				if cmd == "INI" :
					self.nodeHash[fromNodeName].nextNodeList = confList
					#errPrn("10 : EventFlow : initDiffConf : new : %s" % set(confList))
		
		if cmd == "INI" :
			for th in newNodeThList :
				th.start()

		logPrn(">>>>>>>>>>>>>>>>>>>>>>>>>>>")
		logPrn("retStrList = [%s]" % retStrList)
		return retStrList

	def initConf(self) :
		return self.initDiffConf( "INI" )

	def diffConf(self) :
		return self.initDiffConf( "DIF" )

	def show(self) :
		retStrList = []
		retStrList.append( "-" * 55 + "\n")
		retStrList.append( "dump dir        = %s\n" % self.dumpDir )
		retStrList.append( "max cmd queue   = %s\n" % self.maxCmdQ )
		retStrList.append( "kill wait time  = %s\n" % self.killWaitTime )
		retStrList.append( "error data skip = %s\n" % self.errorDataFileSkipVal )
		retStrList.append( "-" * 55 + "\n")

		prnNodeNameList = self.nodeHash.keys()
		prnNodeNameList.sort()

		for nodeName in prnNodeNameList : 
			retStrList.append( "node : %s = %s\n" % (nodeName, self.nodeHash[nodeName].progName) )
		retStrList.append( "-" * 55 + "\n")

		nextNodeNameList = []
		for nodeName in prnNodeNameList :
			nextNodeNameList = [ nextNodeObj.nodeName for nextNodeObj in self.nodeHash[nodeName].nextNodeList ]
				
			if len(nextNodeNameList) :
				retStrList.append( "flow : %s = %s\n" % (nodeName, ",".join( nextNodeNameList )) )

		retStrList.append( "-" * 55 + "\n")
		retStrList.extend( self.abnConfList )

		# ------------------------------------------------------------------
		retStrList.append( "-" * 55 + "\n")
		retStrList.append( " NODE |  STATUS  |  GROUP  | NEXT_NODE |  PROGRAM_NAME \n")
		retStrList.append( "-" * 55 + "\n")

		groupNodeHash = {}
		for groupName in self.groupHash :
			for nodeName in self.groupHash[groupName] :
				if nodeName in prnNodeNameList :
					groupNodeHash[nodeName] = groupName
		# ------------------------------------------------------------------

		for nodeName in prnNodeNameList :
			prnGrpName = '***'
			prnNextNodeName = '***'
			nextNodeNameList = [ nextNodeObj.nodeName for nextNodeObj in self.nodeHash[nodeName].nextNodeList ]
			if nodeName in groupNodeHash : prnGrpName = groupNodeHash[nodeName]
			if len(nextNodeNameList) : prnNextNodeName = ",".join( nextNodeNameList )  
			tmpProName = self.nodeHash[nodeName].progName
			if len(self.nodeHash[nodeName].progName) > 60 :
				tmpProName = self.nodeHash[nodeName].progName[:60]
			prnOutStr = " %4s | %s(%03d)  |  %5s  | %9s | %s\n" % \
			           (nodeName,self.nodeHash[nodeName].stat,self.nodeHash[nodeName].actCnt,prnGrpName,prnNextNodeName,tmpProName)
			retStrList.append(prnOutStr)

		retStrList.append( "-" * 55 + "\n")

		return retStrList
	
	def actTermNode(self, cmd, nodeNameList) :
		retStrList = []

		if  nodeNameList[0].upper() == 'ALL' :
			nodeNameList = self.nodeHash.keys()
		nodeNameList.sort()

		#print "+++++++++++++++ NodeNameList (%s)" % nodeNameList

		for entryName in nodeNameList :
			try :
				nodeName = entryName
				if cmd == "ACT" :
					self.nodeHash[nodeName].stat = "ACT"
					retStrList.extend( self.nodeHash[nodeName].act() )
				else :
					self.nodeHash[nodeName].stat = "TRM"
					### def term can be called if abnormal term case, by tesse, seory
					self.nodeHash[nodeName].actCnt = 0
					#logPrn("actTermNode : 001 :  %s: term call" % (nodeName))
					retStrList.extend( self.nodeHash[nodeName].term() )

			except KeyError :
				try :
					groupName = entryName
					for nodeName in self.groupHash[groupName] :
						try :
							if cmd == "ACT" :
								self.nodeHash[nodeName].stat = "ACT"
								retStrList.extend( self.nodeHash[nodeName].act() )
							else :
								self.nodeHash[nodeName].stat = "TRM"
								### def term can be called if abnormal term case, by tesse, seory
								self.nodeHash[nodeName].actCnt = 0
								#logPrn("actTermNode : 002 :  %s: term call" % (nodeName))
								retStrList.extend( self.nodeHash[nodeName].term() )

						except KeyError :
							retStrList.append("NOK : %s : no node name exist\n" % nodeName)
				except KeyError :
					retStrList.append("NOK : %s : no group name exist\n" % groupName)

				#retStrList.append("NOK : %s : no node name exist\n" % nodeName)

		return retStrList
	
	def actNode( self, nodeNameList ) :
		return self.actTermNode( "ACT", nodeNameList )

	def termNode( self, nodeNameList ) :
		return self.actTermNode( "TRM", nodeNameList )

	def run(self) :
		while SHUTDOWN == False :
			try :
				readReady, writeReady, exReady = select.select( self.readList, [], [], 1)
			except Exception, err :
				errPrn (">>> 000000 : %s" % str(err) )
			# errPrn ("debug : 0.2 : %s" % readReady)
	
			#errPrn ("11 : EventFlow : run : select read data line = %s" % (readReady))
	
			if len(readReady) == 0 :
				#errPrn ("12 : EventFlow : run : select no read data line = %s" % len(readReady))
				if SHUTDOWN == True :
					break
				else :
					continue
	
			for fd in readReady :
				msg = fd.readline()

				if msg[:7] == "file://" :
					msg = msg.strip()

				elif msg == "" :
					time.sleep(1)
					errPrn ("13.1 :EventFlow : run : readLine msg=[%s]" % (msg))
					continue

				else :
					continue
	
				#errPrn ("main : readLine msg=[%s]" % (msg))
				### version 0.1.1 ###
				try :
					for node in self.fdHash[fd].nextNodeList :
						node.put(msg)
						__LOG__.Trace("[%s] : *** stdout->buf put *** EventFlowClass : put stdout msg to cmdQueue, msg=[%s]" % (node.nodeName,msg))
				except KeyError :
					__LOG__.Exception()
	
		errPrn(">>> while break")
		for node in self.nodeHash :
			self.nodeHash[node].shutdownSet()

		for node in self.nodeHash :
			self.nodeHash[node].join()
			errPrn ("14 : EventFlow : run : %s joined" % self.nodeHash[node].nodeName)

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

		errPrn("***************************")
		errPrn("******* 1 : SIOEventFlow : sfio : [%s]" % cmd)
		errPrn("***************************")

		if cmd == "SHW" :
			retStrList = self.eventFlow.show()
			res = "%s" % "".join(retStrList)
			return self.retFmt(res)

		elif cmd == "KIL" :
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
		
		else :
			return None

	def run(self) :
		while(True) :
			try :
				line = sys.stdin.readline()
			except IOError :
				__LOG__.Exception()
				break
				
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

		__LOG__.Trace(">>> SIOEvent Thread : eventFlow join")

def main() :
	if len(sys.argv) < 2 or len(sys.argv) > 3 :
		print ("usage: %s confFileName [clear]" % sys.argv[0])
		sys.exit()
	
	### Make Config ###
	logPrn("--------------------------------------------")
	logPrn(" START !!!!!!")
	confFileName = sys.argv[1]
	ef = SIOEventFlow(confFileName)
	errPrn(">>> main : debug 1 : ")
	ef.run()
	
if __name__ == "__main__" : 
	import Mobigen.Common.Log as Log;
	import sys, os, getopt; OPT, ARGS = getopt.getopt(sys.argv[1:], 'd')
	LOG_NAME = '~/LOG/%s.log' % (os.path.basename(sys.argv[0]))

	try : OPT.index(('-d', '')); Log.Init()
	except : Log.Init(Log.CRotatingLog(os.path.expanduser(LOG_NAME), 1000000, 5))
	sys.argv = [sys.argv[0]] + ARGS

	main()
