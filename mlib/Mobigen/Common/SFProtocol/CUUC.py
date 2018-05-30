#!/usr/bin/python

import sys, getopt, os
from socket import *

def main() :

	csock = socket( AF_UNIX, SOCK_DGRAM )
	csock.bind('clientfile')

	try :
		csock.sendto('This is test string...\n', 'serverfile')
		s, addr = csock.recvfrom(1024)
		if s == 'This is response string...!!\n':
			print 'UUDP : Receive...................OK!!'	
		else:
			print 'UUDP : Receive...................Fail!!'	
	except Exception, err :
		print 'Exception : ', err

	csock.close()
	os.remove('clientfile')

if __name__ == '__main__' :
	main()
