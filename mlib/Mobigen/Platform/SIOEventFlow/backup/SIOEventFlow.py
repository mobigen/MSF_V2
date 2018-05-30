#!/usr/bin/python

import subprocess, sys, shlex, select, threading, collections, time, ConfigParser, re

SHUTDOWN = False

class Node(threading.Thread) :
	def __init__(self, progName, fdHash, readList, maxQueueLen=10000) :
		threading.Thread.__init__(self)
		self.queue = collections.deque([],maxQueueLen)
		self.progName = progName
		self.fdHash = fdHash
		self.readList = readList

		self.initPros()
		self.nextNodeList = []

	def __del__(self) :
		self.flushQueue()
		self.pros.terminate()
		time.sleep(5)
		self.pros.kill()

	def flushQueue(self) :
		pass

	def initPros(self) :
		try :
			del( self.fdHash[self.pros.stdout] )
			self.readList.remove( self.pros.stdout )
		except AttributeError :
			pass
		self.pros = subprocess.Popen( self.progName, shell=True, bufsize=0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
		self.fdHash[self.pros.stdout] = self
		self.readList.append(self.pros.stdout)

	def run(self) :
		while( SHUTDOWN == False ) :
			try :
				inMsg = self.queue.popleft()
				print "debug : 1 : node : run : %s : inMsg=[%s]" % (self.progName, inMsg)

			except IndexError :
				if self.pros.poll() != None :
					self.initPros()
				time.sleep(1)
				continue

			try :
				self.pros.stdin.write( "%s\n" % inMsg )
				self.pros.stdin.flush()
				#print "debug : 2 : Node : %s : inMsg=[%s]" % (self.progName, inMsg)
	
				while True :
					cptMsg = self.pros.stderr.readline().strip()
					if cptMsg == inMsg :
						break
					elif cptMsg == "" :
						print "**********************"
					else :
						print "debug : 5 : Node : %s : cptMsg=[%s]" % (self.progName, cptMsg)
	
			except IOError :
				self.queue.appendleft(inMsg)
				self.pros.kill()

				if SHUTDOWN == True :
					break
	
				self.initPros()
				time.sleep(1)

	def put(self, msg) :
		self.queue.append(msg)
		# print "debug : node : put : %s : queue=[%s]" % (self.progName, self.queue)

def main() :
	if len(sys.argv) != 2 :
		print "usage: %s confFileName" % sys.argv[0]
		sys.exit()
	
	### Make Config ###
	confFileName = sys.argv[1]
	confFile = ConfigParser.ConfigParser()
	confFile.read( confFileName )

	confNode = {}
	for k,v in confFile.items("NODE") :
		confNode[k] = v
	print "debug : confNode = %s" % confNode

	confFlow = {}
	for k,v in confFile.items("FLOW") :
		confFlow[k] = re.split( "\s*,\s*", v.lower() )
	print "debug : confFlow = %s" % confFlow
	###################

	nodeHash = {}
	fdHash = {}
	readList = []
	for nodeName, progName in confNode.items() :
		nodeHash[nodeName] = Node(progName, fdHash, readList)

	for fromNodeName, nodeList in confFlow.items() :
		nodeHash[fromNodeName].nextNodeList = [ nodeHash[toNodeName] for toNodeName in nodeList ]
	
	for node in nodeHash :
		nodeHash[node].start()

	while True :
		readReady, writeReady, exReady = select.select( readList, [], [], 1)
		# print "debug : 0.2 : %s" % readReady

		if len(readReady) == 0 :
			print "debug : main : select no read data"
			continue

		for fd in readReady :
			msg = fd.readline().strip()
			if msg == '' :
				time.sleep(1)
				print "debug : 0.1 : main : readLine msg=[%s]" % (msg)
				continue

			# print "debug : 0 : main : readLine msg=[%s]" % (msg)

			for node in fdHash[fd].nextNodeList :
				node.put(msg)

if __name__ == "__main__" : main()
