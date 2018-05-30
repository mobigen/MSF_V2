#!/usr/bin/python

import Mobigen.SF.lib.SFProtocol as sfp
import sys, getopt, time
from socket import *

def main() :
	try :
		optStr = sfp.getOptStr()
		optList, args = getopt.getopt(sys.argv[1:], optStr)
		if len(args) != 2 : raise Exception
		opts = {}
		for optKey, optVal in optList : opts[optKey] = optVal
	except :
		print 'usage : %s [-options] servIP servPort' % (sys.argv[0])
		sfp.prnOpt()
		sys.exit()

	sf = sfp.SFProtocol(sfp.SFP_CH_U, **opts)

	servIP = args[0]
	servPort = int(args[1])

	servsock = socket( AF_INET, SOCK_DGRAM )
	servsock.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1)
	servsock.bind( (servIP, int(servPort)) )
	servsock.connect((servIP, 9998))
	sf.setFD(servsock)
	(pt, rsv, cmd, msg) = ('', '', '', '')

	readStartSec = time.time()
	for count in range(100000):
		try :
			(pt, rsv, cmd, msg) = sf.read()

			if msg != 'This is test string....!!\n':
				break
		except Exception, err :
			print 'Exception : ', err
			break
	readEndSec = time.time()
	print '100000 Receive Time : %s' % (readEndSec - readStartSec)

	time.sleep(3)
	for count in range(100000):
		try :
			sf.write('','','This is response string...!!\n' )
		except Exception, err :
			print 'Exception : ', err
			break
	servsock.close()

if __name__ == '__main__' :
	main()
