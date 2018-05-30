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
		sfp.prnOpt()
		sys.exit()

	sf = sfp.SFProtocol(sfp.SFP_CH_T, **opts)

	servIP = args[0]
	servPort = int(args[1])

	servsock = socket( AF_INET, SOCK_STREAM )
	servsock.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1)
	servsock.bind( (servIP, int(servPort)) )
	servsock.listen(1)

	cSock, addr = servsock.accept()
	sf.setFD(cSock)

	try :
		(pt, rsv, cmd, msg) = ('', '', '', '')
		(pt, rsv, cmd, msg) = sf.read()

		if msg == 'This is test string....!!\n':
			print 'TCP   : Receive...................OK!!'
		else:
			print 'TCP   : Receive...................Fail!!'
		sf.write('','','This is response string...!!\n' )
	except Exception, err :
		print 'Exception : ', err

	servsock.close()

if __name__ == '__main__' :
	main()
