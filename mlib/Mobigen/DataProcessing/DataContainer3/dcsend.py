#!/usr/bin/python

VERSION = '2.0'

import sys, socket, time, re, struct, getopt
import Struct
import DataContainer

import signal
SHUTDOWN = False
def handler(sigNum, frame) :
	global SHUTDOWN
	SHUTDOWN = True
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

PACKER = Struct.Struct()

def send( sock, fileTime, msgTime, opt, key, val ) :
	sock.sendall( PACKER.pack(fileTime, msgTime, opt, key, val) )

def main() :
	global SHUTDOWN
	try :
		optList, args = getopt.getopt(sys.argv[1:], 'r:f:t:d')
		if len(args) < 4 : raise Exception
		optDict = {}
		for optKey, optVal in optList : optDict[optKey] = optVal

	except Exception, err:
		print 'usage : %s [-r<Recno>] [-f<Filter(reserved)>] [-t<dType(reserved)>] [-d] msgName ip port fileTime' % (sys.argv[0])
		print '        -d : debug mode'
		sys.exit()
		# if '-l' in optDict : server.load( optDict['-l'] )

	if '-r' in optDict : recno = int(optDict['-r'])
	else : recno = 0
	# if '-f' in optDict : filter = optDict['-f']
	# else : filter = 'all'
	# if '-t' in optDict : msgType = optDict['-t']
	# else : msgType = 'E'

	msgName, ip, port, fileTime = args
	port = int(port)
	dataType = 'b'
	fileTime = str(fileTime)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect( (ip, port) )
	print '* connected : remote ip=%s, port=%s' % (ip, port)

	db = DataContainer.DataContainer('.', DataType=dataType, Version=3)

	if fileTime == '-1' :
		while 1 :
			if SHUTDOWN : break

			fileTime, recno = db.getLastFileTimeRecno()
			if fileTime :
				break
			else :
				print 'no search last file'
				time.sleep(1)

	while 1 :
		if SHUTDOWN : break

		try :
			fileTime, msgTime, opt, key, val = db.get(fileTime, recno)
			break
		except :
			print 'get fail, fileTime=[%s], recno=[%s]' % (fileTime, recno)
			time.sleep(1)

	send( sock, fileTime, msgTime, opt, key, val )

	while True :
		if SHUTDOWN : break
		fileTime, msgTime, opt, key, val = db.next()
		send( sock, fileTime, msgTime, opt, key, val )

	print '+++ SHUTDOWN'

if __name__ == '__main__' : main()
