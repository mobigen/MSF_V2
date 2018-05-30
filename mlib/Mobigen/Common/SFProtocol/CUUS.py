#!/usr/bin/python

import sys, getopt, os
from socket import *

def main() :
	servsock = socket( AF_UNIX, SOCK_DGRAM )
	servsock.bind('serverfile')

	try :
		s, addr = servsock.recvfrom(1024)
		if s == 'This is test string...\n':
			print 'UUDP   : Receive...................OK!!'
		else:
			print 'UUDP   : Receive...................Fail!!'
		servsock.sendto('This is response string...!!\n', addr)
	except Exception, err :
		print 'Exception : ', err

	servsock.close()
	os.remove('serverfile')

if __name__ == '__main__' :
	main()
