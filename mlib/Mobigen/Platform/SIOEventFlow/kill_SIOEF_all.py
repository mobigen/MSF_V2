#!/bin/env python

from socket import *
import sys, time

IP = 'localhost'

def ConnectEventFlow(IP, PORT):
	try :
		sock = socket(AF_INET, SOCK_STREAM)
		sock.connect((IP, PORT))
		return sock
	except :
		return None

def DisConnectEventFlow(sock) :
	try :
		sock.sendall("kil\n")
	except Exception, err :
		print err
	time.sleep(15)
	try : sock.close()
	except : pass

def main() :
	
	if len(sys.argv) != 2 :
		print '%s PORT|ALL(9001,9002,9003,9004,9005,9006,9007)' % sys.argv[0]
		sys.exit()

	if sys.argv[1].upper() == 'ALL' :
		portList = [9001,9002,9003,9004,9005,9006,9007]
	else :
		portList = [int(sys.argv[1])]

	for PORT in portList :
		try : 
			sock = ConnectEventFlow(IP, PORT)
			time.sleep(1)	
			DisConnectEventFlow(sock)
		except :
			pass
	
	
if __name__ == "__main__" :
	main()
