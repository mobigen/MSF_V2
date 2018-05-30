#!/usr/bin/python
import time, sys

def main() :
	for i in range(100) :
		print i
		sys.stdout.flush()
		while 1 :
			buf = sys.stdin.read(1)
			sys.stderr.write( buf )
			sys.stderr.flush()
			if buf == '\n' : break
		time.sleep(1)

main()
