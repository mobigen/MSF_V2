#!/usr/bin/env pypy

import sys
import socket
import getopt


class EFMonitor() :

	def __init__( self ) :
		pass

	
	def stdio( self, itr ) :
		try :
			for line in itr :
				yield line
		except :
			pass



if __name__ == "__main__" :
	
	mon = EFMonitor()

	for evt in mon.stdio( iter( sys.stdin.readline, "" ) ) :

		sys.stdout.write(evt)
		sys.stdout.flush()

		sys.stderr.write(evt)
		sys.stderr.flush()
