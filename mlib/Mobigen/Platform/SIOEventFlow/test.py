#!/usr/bin/python

import subprocess, sys, shlex, select, threading, collections, time

SHUTDOWN = False

class Node(threading.Thread) :
	def __init__(self, progName) :
		threading.Thread.__init__(self)
		self.progName = progName

		self.pros = subprocess.Popen( self.progName, shell=True, bufsize=1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)

	def run(self) :
		while( SHUTDOWN == False ) :
			print "---------------start"
			cptMsg = self.pros.stderr.readline().strip()
			print cptMsg
			print "---------------end"
			print "debug : Node : %s : cptMsg=[%s]" % (self.progName, cptMsg)
			time.sleep(1)

def main() :
	node = Node("ev1.py")
	node.start()

if __name__ == "__main__" : main()
