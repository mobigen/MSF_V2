#!/home/mobigen/bin/python

import os
import sys
import time
import getopt
from socket import *

import Mobigen.Common.Log as Log ; Log.Init()


def Usage() :
	print "%s --force --pipe|--udp gate_name log_file_path file_size file_count" % sys.argv[0]

def Main(args) :
	if(len(args)<6) :
		Usage()
		sys.exit()

	try: opts, args = getopt.getopt(args[1:], "", ["force", "pipe", "udp"])
	except getopt.GetoptError: 
		Usage()
		sys.exit()

	path = "/tmp/mobigen/%s" % args[0]	

	for o, v in opts:
		if o in ("--force"):
			try : os.unlink(path)
			except : pass
			break

	bPIPE = False

	for o, v in opts:
		if o in ("--pipe"):
			try : os.mkfifo(path)
			except : pass
			gate = open(path, "r")
			bPIPE = True
			break

		if o in ("--udp"):
			gate = socket(AF_UNIX, SOCK_DGRAM)
			gate.bind(path)
			break

	if(len(args) == 4) : 
		Log.Init(Log.CRotatingLog(args[1], args[2], args[3]))

	try :
		while True :
			if bPIPE : 
				log = gate.readline()
				if(len(log)==0) : 
					time.sleep(1)
					continue
				__LOG__.Write(log[:-1])
			else : 
				log, addr = gate.recvfrom(1000000)
				__LOG__.Write(log[:-1])
	except :
		__LOG__.Exception()



if __name__ == "__main__" :
	Main(sys.argv)

