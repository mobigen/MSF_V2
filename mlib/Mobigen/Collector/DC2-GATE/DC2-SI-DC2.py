#!/usr/bin/python
# -*- coding: cp949 -*-

# V1.0 : 060706 : seory
# V1.1 : 060727 : tesse
# V1.2 : 060802 : tesse
#			elif fmt == 'd' :
#				msgTime = time.strftime("%Y%m%d%H%M%S")
#				db.put(msgTime, data)
# V1.21: 061124 : tesse
#		log( 'EOF received when read header' )
#		error( 'bad header size = [%s] not 16' % len(header) )


import sys, time, os, re, getopt
#from DataContainer import *
#import Mobigen.Archive.DataContainer2.DataContainer as DataContainer
import Mobigen.DataProcessing.DataContainer2 as DataContainer

import signal
SHUTDOWN = False
def handler(sigNum, frame) :
	global SHUTDOWN
	SHUTDOWN = True
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGHUP, handler)
signal.signal(signal.SIGPIPE, handler)

def error(val) :
	try :
		sys.stderr.write( "--- error : %s\n" % val )
		sys.stderr.flush()
	except : pass

def debug(val) :
	try :
		sys.stderr.write( "*** debug : %s\n" % val )
		sys.stderr.flush()
	except : pass

def log(val) :
	try :
		sys.stderr.write( "+++ log   : %s\n" % val )
		sys.stderr.flush()
	except : pass

# STDIN Binary DATA FORMAT : PType 1
# Space(6)length(10)yyyymmddhhmmss(14)OptData(16)Body

def main() :
	try :
		 ### 뒤에 인수가 올경우 : 붙이고, 아닐경우 안붙인다
		 ### : 에 상관없이 optList 는 튜플의 리스트로 반환된다.
		optList, args = getopt.getopt(sys.argv[1:], 'p:f:m:k:i:')
		if len(args) != 1 : raise Exception
		optDict = {}
		for optKey, optVal in optList : optDict[optKey] = optVal
	except :
		print 'usage : %s [-pfmki] homeDir' % (sys.argv[0])
		print '        -p[6] : protocol type, default:1'
		print '        -f[od|d] : od : message format = option(16byte) data'
		print '                        msgTime is current time'
		print '                    d : message format = data'
		print '                        msgTime is current time'
		print "                        option is ''"
		print '                 : default format = msgTime(yyyymmddhhmmss) option(16byte) data'
		print '        -m[w|a] : write or append mode, default=a'
		print '        -k[Num] : data keep hour, default=24'
		print '        -i[Num] : bad msgTime record skip condition hour, default=-1 means no check'
		print '        -v[2] : dc version , default=2'
		sys.exit()

	if '-p' in optDict : pType = int( optDict['-p'] )
	else : pType = 1

	if '-f' in optDict : fmt = optDict['-f']
	else : fmt = 'tod'

	if '-m' in optDict : mode = optDict['-m']
	else : mode = 'a'

	if '-k' in optDict : keepHour = int( optDict['-k'] )
	else : keepHour = 24

	if '-i' in optDict : fti = int( optDict['-i'] )
	else : fti = -1

	if '-v' in optDict : version = int( optDict['-v'] )
	else : version = 2

	homeDir = args[0]
	if os.path.exists(homeDir) == False :
		os.mkdir(homeDir)

	db = DataContainer.DataContainer(homeDir, Mode=mode,\
		KeepHour=keepHour, FileTimeInterval=fti, \
		Version=version)

	while True : 
		try :
			
			if pType == 6 :
				data = sys.stdin.readline()[:-1]
				if data == '' : break

			else :
				header = sys.stdin.read(16)
				if len(header) == 0 :
					log( 'EOF received when read header' )
					break
				if len(header) != 16 :
					error( 'bad header size = [%s] not 16' % len(header) )
					break

				size = int( header[6:16] )

				data = sys.stdin.read(size)
				if len(data) == 0 :
					log( 'EOF received when read body' )
					break
				if len(data) != size :
					error( 'bad body size = [%s] not 16' % len(data) )
					break

			if fmt == 'od' :
				msgTime = time.strftime("%Y%m%d%H%M%S")
				db.put(msgTime, data[16:], data[:16])

			elif fmt == 'd' :
				msgTime = time.strftime("%Y%m%d%H%M%S")
				db.put(msgTime, data)

			else :
				db.put(data[0:14], data[30:], data[14:30])

		except Exception, err :
			if SHUTDOWN == True :
				log( 'shutdown detected' )
			else :
				error( err.__str__() )
			break

	db.close()

main()
