#!/usr/bin/python

import Mobigen.SF.lib.SFProtocol as sfp
import sys, getopt
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
		sys.exit()

	sf = sfp.SFProtocol(sfp.SFP_CH_U, **opts)

	servIP = args[0]
	servPort = int(args[1])

	cSock = socket( AF_INET, SOCK_DGRAM )
	cSock.bind((servIP, int(servPort)))
	cSock.connect((servIP, 9997))
	sf.setFD(cSock)

	try :
		sf.write('','','This is response string....!!\n')	
		(pt, rsv, cmd, msg) = ('', '', '', '')
		(pt, rsv, cmd, msg) = sf.read()
		if msg == 'This is test string...!!\n':
			print 'UDP : Receive...................OK!!'
		else:
			print 'UDP : Receive...................Fail!!'
	except Exception, err :
		print 'Exception : ', err

	cSock.close()

if __name__ == '__main__' :
	main()
