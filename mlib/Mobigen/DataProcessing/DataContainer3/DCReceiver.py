#!/usr/bin/python

VERSION = '1.12'

import Mobigen.Common.Log as Log; Log.Init()
import sys, telnetlib, time, re, struct, os, socket, threading
import Struct
import Mobigen.Tools.Socket

import signal
SHUTDOWN = False
def handler(sigNum, frame) :
	global SHUTDOWN
	SHUTDOWN = True
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

class ThRecv(threading.Thread, Struct.Struct) :
	def __init__(self, recvPort, dcrecvObj, **args) :
		threading.Thread.__init__(self)
		Struct.Struct.__init__(self)

		self.recvPort = recvPort
		self.dcrecvObj = dcrecvObj
		self.sockP = None
		self.sockC = None
		self.shutdown = False
		self.bAlive = False

	def alive(self) :
		return self.bAlive

	def run(self) :
		self.bAlive = True
		sockP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sockP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sockP.bind( ('', self.recvPort) )
		sockP.listen(1)
		#sockP.settimeout(1)
		__LOG__.Trace( 'ThRecv Start' )

		while 1 :
			if self.shutdown : break
			try :
				(self.sockC, addr) = sockP.accept()
				#self.sockC.settimeout(1)
				__LOG__.Trace(  'accepted from %s,%s : ok' % addr)
				break
			except socket.timeout :
				continue

		try :
			while True :
				if self.shutdown : 
					__LOG__.Watch(self.shutdown)
					break

				try :
					#ovh = self.sockC.recv(52)
					ovh = Mobigen.Tools.Socket.read(self.sockC, 52)
				except socket.timeout :
					__LOG__.Exception()	

				fileTime, msgTime, opt, key, valLen = self.unpack(ovh)
				val = Mobigen.Tools.Socket.read(self.sockC, valLen)

				self.dcrecvObj.action( fileTime, msgTime, opt, key, val )
			#	__LOG__.Watch((fileTime, msgTime, opt, key))
		except :
			__LOG__.Exception()

		try : self.sockC.close()
		except : pass
		try : self.sockP.close()
		except : pass

		__LOG__.Trace( 'ThRecv Stop' )
		self.bAlive = False

	def close(self) :
		__LOG__.Trace("close")
		self.shutdown = True
		self.join()
		self.bAlive = False

class DCReceiver(threading.Thread) :
	def __init__(self, ip, id, passwd, recvIp, recvPort, rmtDir, fileTime, **args) :
		threading.Thread.__init__(self)

		self.ip = ip
		self.id = id
		self.passwd = passwd
		self.recvIp = recvIp
		self.recvPort = int(recvPort)
		self.rmtDir = rmtDir
		self.fileTime = fileTime
		self.shutdown = False

		try : self.lastFlag = args['LastRecordFlag']
		except : self.lastFlag = False
	
		try : self.telnetPort = int( args['TelnetPort'] )
		except : self.telnetPort = 23

		try : self.sendCMD = args['SendCMD']
		except : self.sendCMD = 'DC2-SEND'
#		except : self.sendCMD = 'dcsend.py'
	
		try : self.recno = int(args['Recno'])
		except : self.recno = 0
	
		try : self.filter = args['Filter']
		except : self.filter = None
#		except : self.filter = 'all'
	
		try : self.msgType = args['MsgType']
		except : self.msgType = 'all'
	
		try : self.msgName = args['MsgName']
		except : self.msgName = 'all'


	


		print '* ip =', self.ip
		print '* id =', self.id
		print '* passwd =', self.passwd
		print '* recvIp =', self.recvIp
		print '* recvPort =', self.recvPort
		print '* rmtDir =', self.rmtDir
		print '* fileTime =', self.fileTime
		print '* telnetPort =', self.telnetPort
		print '* recno =', self.recno

		self.thr = ThRecv(self.recvPort, self, **args)

		### telnet connect ###
		self.telnet = telnetlib.Telnet(self.ip, self.telnetPort)
		__LOG__.Trace( 'telnet : conneted' )
	
	def alive(self) :
		return self.thr.alive()

	def run(self) :
		__LOG__.Trace("DCReceiver Start")
		try :
			self.thr.start()
		
			self.telnet.read_until('login', 10)
			self.telnet.write(self.id + '\n')
			__LOG__.Trace( '* id send : id = %s' % (self.id) )
		
			self.telnet.read_until('Password:', 10)
			self.telnet.write(self.passwd + '\n')
			__LOG__.Trace( '* passwd send : passwd = %s' % (self.passwd) )
			time.sleep(1)
		
			cmd = 'cd %s\n' % (self.rmtDir)
			self.telnet.write(cmd)
			__LOG__.Trace( '* cmd send : cmd = %s' % cmd )
			time.sleep(1)
		
			optList = []
			if(self.lastFlag) : optList.append("--last")
			else : optList.append("--index=%s:%s" % (self.fileTime, self.recno))
			if(self.filter) : optList.append("--filter='%s'" % self.filter)
			cmd = '%s %s %s %s >& /dev/null & \n' % (self.sendCMD, " ".join(optList), self.recvIp, self.recvPort)

			#cmd = '%s -r%s -f%s -t%s %s %s %s %s >& /dev/null & \n' \
			#		% (self.sendCMD, self.recno, self.filter, self.msgType, \
			#		   self.msgName, self.recvIp, self.recvPort, self.fileTime)

			self.telnet.write(cmd)
			__LOG__.Trace( '* cmd send : cmd = %s' % cmd )

		#	while True :
		#		if(self.alive()==False) : break
		#		time.sleep(2)
		except :
			__LOG__.Exception()

		self.telnet.write("quit\n")
	#	try : self.telnet.close()
	#	except : pass

	def close(self) :
		self.thr.close()

		try : self.telnet.close()
		except : pass

		__LOG__.Trace("close")
		self.shutdown = True
		self.join()
		
def main() :
	global SHUTDOWN
	class Test(DCReceiver) :
		def __init__(self, ip, id, passwd, recvIp, recvPort, rmtDir, fileTime, **args) :
			DCReceiver.__init__(self, ip, id, passwd, recvIp, recvPort, rmtDir, fileTime **args )

		def action( self, fileTime, opt, key, val ) :
			print 'fileTime=%s, key=%s, val=%s, opt=%s' % ( fileTime, key, val, opt )
	
	obj = Test('150.23.15.92', 'eva', 'hello.mobigen', '150.23.15.94', 60374, '/home/eva/mlib/PyModules/DataContainer/testdata', '20050801230000', 0, True )
	obj.daemon = True
	obj.start()

	while True :
		if SHUTDOWN :
			obj.close()
			break
		else :
			time.sleep(1)

if __name__ == '__main__' : main()
