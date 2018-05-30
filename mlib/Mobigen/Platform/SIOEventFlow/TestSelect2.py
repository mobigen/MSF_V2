#!/usr/bin/python
import select, subprocess, threading

class Test(threading.Thread) :
	def __init__(self) :
		threading.Thread.__init__(self)
		self.ps1 = subprocess.Popen( "ev1.py", shell=True, bufsize=1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)

	def run(self) :
		while True :
			self.ps1.stdin.write( "xxx\n" )
			self.ps1.stdin.flush()
			print self.ps1.stderr.readline(),

def main() :
	node = Test()
	node.start()

main()
