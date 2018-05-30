#!/usr/bin/python
import subprocess

class Node( subprocess.Popen ) :
	def __init__(self) :
		subprocess.Popen.__init__(self)

def main() :
	node = Node( "ev1.py", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)

main()
