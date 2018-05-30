#!/usr/bin/python

VERSION = '2.1'
# 050906 : tesse

try : import psyco; psyco.full()
except : pass

import sys, socket, time, re, struct, getopt
import Struct
import DataContainer
import Mobigen.Common.Log as Log; Log.Init()

PACKER = Struct.Struct()

def sendCDR( sock, fileTime, msgTime, opt, key, val ) :
	serOpt, = struct.unpack('B', val[5])
	if serOpt in (4,7,12,15,25,33) :
		sock.sendall( PACKER.pack(fileTime, msgTime, opt, key, val) )

def sendF3K( sock, fileTime, msgTime, opt, key, val ) :
	valList = val.split('\n')

	if re.search( 'ATI', valList[2] ) :
		sock.sendall( PACKER.pack(fileTime, msgTime, opt, key, val) )

	else :
		if re.search('USRDATA', valList[8] ) :
			line = valList[8].strip()
		else :
			line = valList[9].strip()

		try :
			serOpt = int( line[20:24], 16 )
		except :
			__LOG__.Trace( 'invalid f3000 format : [%s]' % val )

		if serOpt in (4,7,12,15,25,33) :
			sock.sendall( PACKER.pack(fileTime, msgTime, opt, key, val) )

def send( sock, fileTime, msgTime, opt, key, val, dType, pNumList ) :
	opt = opt.strip()

	if dType == 'T' :
		sock.sendall( PACKER.pack(fileTime, msgTime, opt, key, val) )

	elif len(opt) > 0 and (opt[-1] in pNumList) :
		if dType == 'C' :
			sendCDR(sock, fileTime, msgTime, opt, key, val)
		elif dType == 'F' :
			sendF3K(sock, fileTime, msgTime, opt, key, val)
		else :
			sock.sendall( PACKER.pack(fileTime, msgTime, opt, key, val) )

def main() :
	global SHUTDOWN
	try :
		optList, args = getopt.getopt(sys.argv[1:], 'r:f:t:d')
		if len(args) < 4 : raise Exception
		optDict = {}
		for optKey, optVal in optList : optDict[optKey] = optVal

	except Exception, err:
		print 'usage : %s [-r<Recno>] [-f<Filter>] [-t<dType(C/F/T/E)>] [-d] msgName ip port fileTime' % (sys.argv[0])
		print '        -d : debug mode'
		sys.exit()
		# if '-l' in optDict : server.load( optDict['-l'] )

	if '-r' in optDict : recno = int(optDict['-r'])
	else : recno = 0
	if '-f' in optDict : filter = optDict['-f']
	else : filter = 'all'
	if '-t' in optDict : msgType = optDict['-t']
	else : msgType = 'E'

	msgName, ip, port, fileTime = args
	port = int(port)

	pNumList = filter.split(',')
	dataType = 'b'

	# print 'debug : ip=%s, port=%s, fileTime=%s, recno=%s' % (ip, port, fileTime, recno)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect( (ip, port) )
	print '* connected : remote ip=%s, port=%s' % (ip, port)

	db = DataContainer.DataContainer('.', DataType=dataType)

	if fileTime == '-1' :
		while 1 :
			fileTime, recno = db.getLastFileTimeRecno()
			if fileTime :
				break
			else :
				print 'no search last file'
				time.sleep(1)

	while 1 :
		try :
			fileTime, msgTime, opt, key, val = db.get(fileTime, recno)
			break
		except :
			print 'get fail, fileTime=[%s], recno=[%s]' % (fileTime, recno)
			time.sleep(1)

	send( sock, fileTime, msgTime, opt, key, val, msgType, pNumList )

	while True :
		fileTime, msgTime, opt, key, val = db.next()
		send( sock, fileTime, msgTime, opt, key, val, msgType, pNumList )
	#	__LOG__.Watch((fileTime, msgTime, opt, key))

if __name__ == '__main__' : main()
