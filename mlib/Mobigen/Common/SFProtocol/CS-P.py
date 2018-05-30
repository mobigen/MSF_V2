#!/usr/bin/python

import Mobigen.SF.lib.SFProtocol as sfp
import sys, getopt, time

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

	(pt, rsv, cmd, msg) = ('', '', '', '')
	fd1 = open('test.txt', 'w+')
	sf.setFD(fd1)

	writeStartSec = time.time()
	for count in range(10000):
		try :
			sf.write('','','This is test string...!!\n' )
		except Exception, err :
			print 'Exception : ', err
			break
	writeEndSec = time.time()

	print '10000 Write Time : %s' % (writeEndSec - writeStartSec)
	fd1.close()

	fd2 = open('test.txt', 'r')
	sf.setFD(fd2)

	readStartSec = time.time()
	for count in range(10000):
		try :
			(pt, rsv, cmd, msg) = sf.read()
			if msg != 'This is test string...!!\n':
				break
		except Exception, err :
			print 'Exception : ', err
	readEndSec = time.time()
	print '10000 Read Time : %s' % (readEndSec - readStartSec)
	fd2.close()

if __name__ == '__main__' :
	main()
