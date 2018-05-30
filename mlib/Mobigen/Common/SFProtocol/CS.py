#!/usr/bin/python

import Mobigen.SF.lib.SFProtocol as sfp
import sys, getopt

def main() :
	try :
		optStr = sfp.getOptStr()
		optList, args = getopt.getopt(sys.argv[1:], optStr)
		opts = {}
		for optKey, optVal in optList : opts[optKey] = optVal
	except :
		print 'usage : %s [-options]' % (sys.argv[0])
		sfp.prnOpt()
		sys.exit()

	sf = sfp.SFProtocol(sfp.SFP_CH_S, **opts)

	try :
		fd1 = open('test.txt', 'w+')
		sf.setFD(fd1)
		sf.write('','','This is test string...!!\n' )
		fd1.close()
		fd2 = open('test.txt', 'r')
		sf.setFD(fd2)
		(pt, rsv, cmd, msg) = ('', '', '', '')
		(pt, rsv, cmd, msg) = sf.read()
		fd2.close()
		if msg == 'This is test string...!!\n':
			print 'STDIO : Receive...................OK!!'
		else:
			print 'STDIO : Receive...................Fail!!'
	except Exception, err :
		print 'Exception : ', err

if __name__ == '__main__' :
	main()
