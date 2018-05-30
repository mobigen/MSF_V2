#!/usr/bin/python
import sys

def main() :
	while 1 :
		print "echo : %s" % sys.stdin.readline()
		sys.stdout.flush()

main()
