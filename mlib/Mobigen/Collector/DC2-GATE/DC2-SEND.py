#!/usr/bin/python
# -*- coding: cp949 -*-

import sys, socket, time, re, struct, getopt
import signal

import Mobigen.DataProcessing.DataContainer2 as DataContainer
import Mobigen.DataProcessing.DataContainer2.Struct as Struct

import Mobigen.Common.Log as Log; Log.Init() 


FILTERMODE = False
FILTER = None
SHUTDOWN = False
def handler(sigNum, frame) :
	global SHUTDOWN
	SHUTDOWN = True
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

PACKER = Struct.Struct()

def send( sock, fileTime, msgTime, opt, key, val ) :

	if(FILTERMODE) :
		if(FILTER.search(opt)) :
		#	__LOG__.Watch((fileTime, msgTime, opt))
			sock.sendall( PACKER.pack(fileTime, msgTime, opt, key, val) )
	else :
	#	__LOG__.Watch((fileTime, msgTime, opt))
		sock.sendall( PACKER.pack(fileTime, msgTime, opt, key, val) )

def Usage() :
	print 'usage : %s [option] ip port send_dc_path' % (sys.argv[0])
	print 
	print 'option :'
	print '  -d, --debug                     debug mode'
	print '  -i, --index=filetime:index      dc2 index info'
	print '  -l, --last                      last-data'
	print '  -f, --filter                    filter pattern'
	sys.exit()

def Main() :
	global SHUTDOWN, FILTERMODE, FILTER
	try : optList, args = getopt.getopt(sys.argv[1:], 'i:idf:', ["filter=", "index=", "last", "debug"])
	except : Usage()
	if len(args) < 2 : Usage()


	if(len(args)==2) : 
		ip, port = args
		path = "."
	elif(len(args)==3) : 
		ip, port, path = args
	port = int(port)
	db = DataContainer.DataContainer(path)

	bIndexFlag = False
	bLastFlag = False
	optDict = {}
	for o, value in optList :
		if o in ('-i', '--index') : 
			bIndexFlag = True
			strFileTime, nRecNo = value.split(":") 
			nRecNo = int(nRecNo)
		if o in ('-l', '--last') : 
			bLastFlag = True
		if o in ('-f', '--filter') : 
			FILTERMODE = True
			FILTER=re.compile(value)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect( (ip, port) )
	__LOG__.Watch('* connected : remote ip=%s, port=%s' % (ip, port))

	if(bLastFlag) : 
		fileTime, msgTime, opt, key, val = db.getLast()
		__LOG__.Watch('* start : getLast')
	else :
		if(bIndexFlag==False) : strFileTime, nRecNo = db.getLastFileTimeRecno()
		__LOG__.Watch('* start : %s,%s' % (strFileTime, nRecNo))
		fileTime, msgTime, opt, key, val = db.get(strFileTime, nRecNo)

	send( sock, fileTime, msgTime, opt, key, val )

	while True :
		if SHUTDOWN : break
		fileTime, msgTime, opt, key, val = db.next()
		send( sock, fileTime, msgTime, opt, key, val )

	print '+++ SHUTDOWN'

if __name__ == '__main__' : 
	Main()
