#!/bin/env python

from socket import *
import Mobigen.Common.Log as Log; Log.Init()
import sys, time

def ConnectEventFlow(IP, PORT):
	try :
		sock = socket(AF_INET, SOCK_STREAM)
		sock.connect((IP, PORT))
		return sock
	except :
		return Nonde

def DisConnectEventFlow(sock) :
	try :
		sock.sendall("bye\n")
	except :
		__LOG__.Exception()
	time.sleep(1)
	sock.close()

def main() :
	__LOG__.Trace("Process Start...")
	
	if len(sys.argv) != 3 :
		print '%s IP PORT' % sys.argv[0]
		sys.exit()

	IP = sys.argv[1]
	PORT = int(sys.argv[2])

	sock = ConnectEventFlow(IP, PORT)
	__LOG__.Trace("connect %s %s" % (IP, PORT))

	sock.sendall("trm,ps2\n")
	time.sleep(30)
	sock.sendall("act,ps2\n")
	time.sleep(30)
	sock.sendall("bye\n")
	time.sleep(5)
	
	DisConnectEventFlow(sock)
	
if __name__ == "__main__" :
	import Mobigen.Common.Log as Log;
	import sys, os, getopt; OPT, ARGS = getopt.getopt(sys.argv[1:], 'd')
	LOG_NAME = '~/LOG/%s.log' % (os.path.basename(sys.argv[0]))
	try : OPT.index(('-d', '')); Log.Init()
	except : Log.Init(Log.CRotatingLog(os.path.expanduser(LOG_NAME), 1000000, 5))
	sys.argv = [sys.argv[0]] + ARGS

	main()
