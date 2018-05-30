##from ctypes import *
import ctypes

#import calldll
import os
import sys, getopt
import win32gui 
import win32api 
import win32con
import struct
import array, time
import threading
from socket import *
import select, re
from traceback   import *
#import Connector
import SFProtocol as sfp
import logging, exceptions
import Mobigen.Common.Log as Log


#==================================
# - Protocol Info
#==================================
P_STD   	= 1
P_TCP   	= 2


#==================================
# - ERROR Info
#==================================
SOCKERR_001 	= 'SOCK-001'


#==================================
# - Format Info
#==================================
DELIMETER_CLI	= ','
DELIMETER_BUS	= ','

g_CopyFmt		= 'LLP'


#==================================
# - Hash Info
#==================================
ConnectorHash	= {}

key1Hash		= {}
key2Hash		= {}
keyBothHash 	= {}


#==================================
# - Global variable Info
#==================================

g_INIT_KEY		= '*,*'
g_RETRY_BUS		= 5


g_OUT_FILE		= None
g_DEBUG_LEVEL 	= logging.ERROR

g_HWNDMAIN		= None
SHUTDOWN		= False


def putNoti( cmd, connectorList, notiKey, msg ):

	### log write

	global g_OUT_FILE
	if g_OUT_FILE :
		g_OUT_FILE.write( msg )
		g_OUT_FILE.flush()
	
	idx = 0		
	for connector in connectorList :
		idx 	= idx + 1
		hwnd	= connector.hWnd
		
		#notiKey				= notiKey.replace(',', DELIMETER_CLI )
		#retMsg				= 'NTI|^|%s|^|%s|^|%s' % ( int(hwnd), notiKey, msg )

		notiData			= []
		notiData.append( 'NTI' )
		notiData.append( str(hwnd) );
		notiData.append( notiKey )
		notiData.append( msg )

		retMsg				= DELIMETER_CLI.join( notiData)
				
		char_buffer         = array.array( "c", retMsg )

		int_data			= 0
		char_buffer_address = char_buffer.buffer_info()[0] 
		char_buffer_size    = char_buffer.buffer_info()[1] 

		copy_struct			= struct.pack( g_CopyFmt, int_data, char_buffer_size, char_buffer_address )

		try :		
			win32gui.SendMessage(hwnd, win32con.WM_COPYDATA, 0, copy_struct )
			ret = win32api.GetLastError()
			
			# send Message Error, dereg	
			if ret == 1400 : ### ERROR_INVALID_WINDOW_HANDLE:
				__LOG__.Trace( "%-10s| Send To client : sendMessage err [%s] [%d/%d][%d:%s]" % ('ERROR', hwnd, idx, len(connectorList), ret, win32api.FormatMessage(ret) ), logging.ERROR )

				connector.deregister()	
			
				# send Message Self Handle
				global g_HWNDMAIN
				if g_HWNDMAIN : pass
				#{
				#	win32gui.SendMessage( g_HWNDMAIN, win32con.WM_COPYDATA, g_HWNDMAIN, copy_struct )
				#}
			else :
				__LOG__.Trace( "%-10s| SEND To client :[%d/%d][%d] [%s]:[%s]" % ('DEBUG', idx, len(connectorList),  hwnd, cmd, retMsg ), logging.DEBUG )
		except Exception, err:
			__LOG__.Exception()
			continue

		


#==========================================================================
#    CLASS       : busThread
#    Purpose     : Bus Interface Class ( protocol : CT_TCP )
#==========================================================================
class busThread( threading.Thread ) :
	def __init__(self, server_ip, server_port, **opts ):

		self.shutdown 	= False
		self.server_ip 	= server_ip
		self.server_port= server_port

		threading.Thread.__init__(self)
		
		self.sock		= None
		self.sf			= None
	
		global g_INIT_KEY	
		self.regKey	 = g_INIT_KEY.strip()
		
		# '-l' : flush mode
		opts['-l'] = 1

		#self.opts	= {}
		self.opts	= opts
		self.connectToServer(-1) # nMaxRetryCnt : -1 , retry connect until connecting to BUS

	def kill(self):
		self.shutdown = True
		self.close()

	def close(self):
		global g_OUT_FILE
		global SHUTDOWN
		
		self.sf.close()
		if g_OUT_FILE: g_OUT_FILE.close()

		SHUTDOWN = True		
		
	def connectToServer(self, nMaxRetryCnt ):	# nMaxRetryCnt : -1 , retry connect until connecting to BUS

		if self.sock : self.sf.close()
		
		self.sock = socket( AF_INET, SOCK_STREAM )

		retryCnt = 0
		while 1:
			try :
				self.sock.connect( (self.server_ip, self.server_port ) )
			except Exception, e:
				__LOG__.Trace( "%-10s| fail connectToServer : %s" % ( 'CRITICAL', str(e)), logging.CRITICAL );
				time.sleep(5);

				if nMaxRetryCnt > 0 :
					retryCnt += 1
					if 	retryCnt >= nMaxRetryCnt : return False
				continue

			__LOG__.Trace( "%-10s| Succ connectToServer [%s:%d]" % ('INFO', self.server_ip, self.server_port), logging.INFO );
			break
		
		self.sf = sfp.SFProtocol(sfp.SFP_CH_T, **self.opts  ) #, self.opts
		self.sf.setFD( self.sock )

		regStr = '0,%s' % self.regKey	# 0 : heartBeat
		self.sf.write( ' ', 'REG', regStr+'\n' )

		return True
		
	
	def run( self ):

		global g_OUT_FILE
		global g_HWNDMAIN	
		nCnt = 0	

		t1_time = time.time()
		
		while 1:

			try :
				(pt, rsv, cmd, msg) = self.sf.read()

				if msg != '':
					__LOG__.Trace( "%-10s| RECV from bus, len:[%d]" % (  "DEBUG", len(msg)) , logging.DEBUG )
					__LOG__.Trace( "%-10s| RECV from bus, msg:[%s]" % (  "NOTSET", msg) , logging.NOTSET )	

					if cmd == 'NTI' or cmd == 'STI' : self.checkKey ( cmd, msg )
					else : __LOG__.Trace( "%-10s| RECV bus bad format = [%s][%s]" % ( 'ERROR', cmd, msg), logging.ERROR )				

					if g_OUT_FILE :
						if nCnt == 0 : 		t1_time = time.time()
						nCnt  = nCnt +1
									
				"""				
				if select.select( [self.sock], [], [], 1 )[0]:
					while 1:
					#{
						try: 
						#{
							self.sock.settimeout(0.3)
							(pt, rsv, cmd, msg) = self.sf.read()
							self.sock.settimeout(0)
							
							if msg != '':
								__LOG__.Trace( "%-10s| RECV from bus, len:[%d]" % (  "DEBUG", len(msg)) , logging.DEBUG )

								__LOG__.Trace( "%-10s| RECV from bus, msg:[%s]" % (  "NOTSET", msg) , logging.NOTSET )	
				
								if cmd == 'NTI' or cmd == 'STI' : self.checkKey ( cmd, msg )
								else : __LOG__.Trace( "%-10s| RECV bus bad format = [%s][%s]" % ( 'ERROR', cmd, msg), logging.ERROR )				

								if g_OUT_FILE :
									if nCnt == 0 : 		t1_time = time.time()
									nCnt  = nCnt +1
						#}
						except timeout, e		: break						# timeout , read break
						except sfp.SFPDiscon 	: raise sfp.SFPDiscon		# session close
						except sfp.SFPBadFormat	:
							__LOG__.Exception()
							continue
						except sfp.SFPBadPType:
							__LOG__.Exception()
							continue
						except exceptions.ValueError :						# self.sf.read() value Error
							__LOG__.Exception()
							continue	
					#}
				"""
				global SHUTDOWN
				if SHUTDOWN : break
				
			except sfp.SFPDiscon:	## Session Close
				__LOG__.Exception()
				##break

				self.sf.close()
				if self.connectToServer( g_RETRY_BUS ) :				
					continue
				else : break	# retry connect fail
		
			except sfp.SFPBadFormat	:
				__LOG__.Exception()
				continue
			except sfp.SFPBadPType:
				__LOG__.Exception()
				continue
			except exceptions.ValueError :	# self.sf.read() value Error
				__LOG__.Exception()
				continue
			except Exception, err :			# Socket Error
				__LOG__.Exception()
				# reConnect To Bus
	
				self.sf.close()
				if self.connectToServer( g_RETRY_BUS ) : 
					continue
				else : break	# retry connect fail
	
		self.close()
		
		t2_time = time.time()
		if (t2_time - t1_time) > 0 :
			__LOG__.Trace( "%-10s| total record / total time =[%d/%f], record/sec =[%d]" % ( 'TEST_SUITE', nCnt, t2_time - t1_time, int( nCnt / (t2_time - t1_time) )  ) , logging.NOTSET )

		try :
			if g_HWNDMAIN :
				__LOG__.Trace( "+++ bus Thread End Before")		
				win32gui.SendMessage( g_HWNDMAIN, win32con.WM_DESTROY, 0, 0 )

				__LOG__.Trace( "+++ bus Thread End Message")			

			"""			
			ret = win32api.GetLastError()
			__LOG__.Trace( "%-10s| DestroyWindow err [%s] [%d:%s]" % ('ERROR', g_HWNDMAIN, ret, win32api.FormatMessage(ret) ), logging.ERROR )
			
			win32api.PostQuitMessage(0)
			"""
		except: __LOG__.Exception()

		__LOG__.Trace( "+++ bus Thread OK!!!")		

	def checkKey( self, cmd,  msg ) :
		global key1Hash, key2Hash, keyBothHash

		###tmpList = msg.split(DELIMETER_BUS )	#  Messsge Format Delimeter received from BUS

		if cmd == 'NTI' :
			tmpList = msg.split(DELIMETER_BUS )	#  Messsge Format Delimeter received from BUS
		else :
			tmpList = msg.split(DELIMETER_BUS, 2 )	#  Messsge Format Delimeter received from BUS
		
		if len(tmpList) % 3 == 0 :
		#{
			for i in range( len(tmpList)/3 ) :
				key1 = tmpList[i*3].strip()
				key2 = tmpList[i*3 + 1].strip()
				bothKey = '%s,%s' % (key1, key2)
				notiVal = tmpList[i*3 + 2].strip('\n')
				##notiVal = tmpList[i*3 + 2]
				
				if key1 == '*' or key2 == '*' :
					__LOG__.Trace( "%-10s| bad notification key format = [%s]" % ('ERROR', msg), logging.ERROR )
					continue

				if key1 != '' and key1Hash.has_key(key1) :
					putNoti( cmd, key1Hash[key1], bothKey , notiVal )

				if key2 != '' and key2Hash.has_key(key2) :
					putNoti( cmd, key2Hash[key2], bothKey, notiVal )

				if bothKey != ',' and keyBothHash.has_key(bothKey) :
					putNoti( cmd, keyBothHash[bothKey], bothKey, notiVal )
					
				if len( keyBothHash['*,*'] ) > 0 :
					putNoti( cmd, keyBothHash['*,*'], bothKey, notiVal )
		#}
		else: __LOG__.Trace( "%-10s| bad notification format = [%s][%s]" % (cmd, msg) , logging.ERROR )



#==========================================================================
#    CLASS       : Connector
#    Purpose     : Client Object Class
#==========================================================================
class Connector :
	#def __init__(self, cSock, addr, key1Hash, key2Hash, keyBothHash, conList, **opts) :
	def __init__(self, hWnd, key1Hash, key2Hash, keyBothHash, conList ) :
		#self.sf = sfp.SFProtocol( sfp.SFP_CH_T, **opts)
		#self.sf.setFD(cSock)

		self.hWnd		= hWnd		
		self.key1Hash 	= key1Hash
		self.key2Hash 	= key2Hash
		self.keyBothHash = keyBothHash
		
		self.heartBeatSec = 0
		self.startSec 	= time.time()

		self.deregiBothList = []
		self.deregiKey1List = []
		self.deregiKey2List = []
		
		self.conList = conList
		

	"""
	def ansNOK(self, reason) :
		self.sf.write( '#E', 'NOK', reason + '\n' )

	def ansOK(self, reason) :
		self.sf.write( '', 'OK', reason + '\n' )

	def ansHeart(self) :
		aliveSec = time.time() - self.startSec

		if aliveSec >= self.heartBeatSec :
			try :
				self.sf.write( '', 'NOP', 'heart beat\n' )
				###__LOG__.Trace('%s : send heart beat, [%s] sec' % (self.addr, aliveSec) )

			except Exception, err :
				###__LOG__.Exception()
				###__LOG__.Trace('%s : SFPDiscon'%(self.addr) )
				self.deregister()

		self.startSec = time.time()
	"""
	
	def regiNotiKeyList(self, notiKeyList, msg) :
		if len(notiKeyList) % 2 != 0 :
			err = '%-10s| invalid register format, msg=[%s]' % ('ERROR', msg )
			raise Exception, err

		for i in range( len(notiKeyList) / 2 ) :
			key1 = notiKeyList[i*2].strip()
			key2 = notiKeyList[i*2 + 1].strip()

			if key1 == '' or key2 == '' :
				err = '%-10s| empty key, [%s]' % ('ERROR', msg )
				raise Exception, err
			
			if key1 == '*' and key2 == '*' :
				self.regiNotiKey( self.keyBothHash, '*,*', self.deregiBothList )
			elif key1 == '*' :
				self.regiNotiKey( self.key2Hash, key2, self.deregiKey2List )
			elif key2 == '*' :
				self.regiNotiKey( self.key1Hash, key1, self.deregiKey1List )
			else :
				self.regiNotiKey( self.keyBothHash, '%s,%s' % (key1, key2), self.deregiBothList )
				
		#print "adapter : regiNotiKeyList : ", self.key1Hash, self.key2Hash,self.keyBothHash

	### add self reference to notiKeyHash
	def regiNotiKey(self, notiKeyHash, notiKey, deregiKeyList) :
		
		if not notiKeyHash.has_key(notiKey) : notiKeyHash[notiKey] = []

		try :
			notiKeyHash[notiKey].index(self)
			__LOG__.Trace( "%-10s| %s : regiNoti, %s, already registered" % ('ERROR', self.hWnd, notiKey), logging.ERROR )
		except :
			notiKeyHash[notiKey].append(self)
			__LOG__.Trace( "%-10s| %s : regiNoti OK, [%s]" % ('INFO', self.hWnd, notiKey), logging.INFO )

		try :
			deregiKeyList.index(notiKey)
		except :
			deregiKeyList.append(notiKey)

	### remove self reference from notiKeyHash
	def deregiNotiKey(self, notiKeyHash, deregiKeyList ) :
		for notiKey in deregiKeyList :
			if notiKeyHash.has_key(notiKey) :
				try : notiKeyHash[notiKey].remove(self)
				except : pass
				__LOG__.Trace( "%-10s| %s : deregiNoti: [%s]" % ('INFO', self.hWnd, notiKey), logging.INFO )
		
			if notiKey != '*,*' and len( notiKeyHash[notiKey] ) == 0 :
				try : del( notiKeyHash[notiKey] )
				except : pass
				__LOG__.Trace( "%-10s| %s : deregiNoti and pop key, [%s]" % ('INFO', self.hWnd, notiKey), logging.INFO )

	def deregister(self) :
		try : self.sf.flush()
		except : pass

		self.deregiNotiKey( self.key1Hash, self.deregiKey1List )
		self.deregiNotiKey( self.key2Hash, self.deregiKey2List )
		self.deregiNotiKey( self.keyBothHash, self.deregiBothList )
		self.deregiNotiKey( self.keyBothHash, ['*,*'] )

		"""
		try : self.cSock.close()
		except : pass
		"""
		
		try : self.conList.remove(self)
		except : pass

		__LOG__.Trace("%-10s| %s : deregister completed"% ('INFO', self.hWnd), logging.INFO )

	#------------------------------------------------------------
	# Add : 0529 : 
	#------------------------------------------------------------
	def deregiNotiOneKey(self, notiKeyHash, notiKey ) :
		if notiKeyHash.has_key( notiKey ) :
			try : notiKeyHash[notiKey].remove(self)
			except : pass
			__LOG__.Trace( "%-10s| %s : deregiNoti: [%s]" % ('INFO', self.hWnd, notiKey), logging.INFO )
	
			if notiKey != '*,*' and len( notiKeyHash[notiKey] ) == 0 :
				try : del( notiKeyHash[notiKey] )
				except : pass
				__LOG__.Trace( "%-10s| %s : deregiNoti and pop key, [%s]" % ('INFO', self.hWnd, notiKey), logging.INFO )
		else :
			err = "%-10s| deregistration , not found key=[%s]" % ( 'ERROR', notiKey )
			raise Exception, err


	#------------------------------------------------------------
	# Add : 0529 : 
	#------------------------------------------------------------
	def deregisterOfKey(self, deregiKeyList ) :
		try : self.sf.flush()
		except : pass

		if len(deregiKeyList) % 2 != 0 :
			err = '%-10s| invalid deregister format, key=%s' % ( 'ERROR', deregiKeyList )
			raise Exception, err

		for i in range( len( deregiKeyList ) / 2 ) :
			key1 = deregiKeyList[i*2].strip()
			key2 = deregiKeyList[i*2 + 1].strip()

			if key1 == '' or key2 == '' :
				err = '%-10s| empty key' % 'ERROR'
				raise Exception, err
					
			if key1 == '*' and key2 == '*' :
				self.deregiNotiOneKey( self.keyBothHash, '*,*' )
				try:
					self.deregiBothList.remove('*,*')
				except : pass
				
			elif key1 == '*' :
				self.deregiNotiOneKey( self.key2Hash, key2 )
				try:
					self.deregiKey2List.remove( key2 )
				except : pass
				
			elif key2 == '*' :
				self.deregiNotiOneKey( self.key1Hash, key1 )
				try:
					self.deregiKey1List.remove(key1)
				except : pass
			else :
				self.deregiNotiOneKey( self.keyBothHash, '%s,%s' % (key1, key2) )
				try:
					self.deregiBothList.remove( '%s,%s' % (key1, key2) )
				except : pass
	
		"""
		try : self.cSock.close()
		except : pass

		try : self.conList.remove(self)
		except : pass
		"""
		
	def register(self, msg) :
		try :
			regiKeyList = msg.split( DELIMETER_BUS )
			#self.heartBeatSec = int( regiKeyList.pop(0) )

		except :
			# self.ansNOK('bad heart beat sec value')
			# continue
			pass # make default self.heartBeatSec 0

		self.regiNotiKeyList( regiKeyList, msg )

		#self.ansOK('registration completed')

		try :
			self.conList.index(self)
		except :
			self.conList.append(self)



#==========================================================================
#    CLASS       : gsWindow
#    Purpose     : Main Window Class
#==========================================================================
class gsWindow: 
	def __init__(self , className, serverIp, serverPort, **opts ): 
		message_map = {
			win32con.WM_DESTROY: self.OnDestroy,
			win32con.WM_CLOSE: self.OnClose,
			win32con.WM_COPYDATA: self.OnCopyData,
		}

		wc = win32gui.WNDCLASS() 
		wc.hIcon =  win32gui.LoadIcon(0, win32con.IDI_APPLICATION) 
		wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW) 
		wc.hbrBackground = win32con.COLOR_WINDOW 
#		wc.lpszClassName = "WinAdapter"
		wc.lpszClassName = className
		wc.lpfnWndProc = message_map 
		self.hinst = wc.hInstance = win32api.GetModuleHandle(None) 
		self.cAtom = win32gui.RegisterClass(wc)

		self.ConnectorHash = {}
		self.conList	= []
		self.busTh		= None	# busServer thread
		
		#print 'adapter: hinst: %s\n' % self.hinst
		
		self.hwnd = win32gui.CreateWindowEx( 
		win32con.WS_EX_APPWINDOW, 
		self.cAtom, 
		className, #"WinAdapter App",
		win32con.WS_OVERLAPPED | win32con.WS_SYSMENU, 
		win32con.CW_USEDEFAULT, 0, 
		win32con.CW_USEDEFAULT, 0, 
		0, 0, self.hinst, None) 

		global g_HWNDMAIN
		g_HWNDMAIN = self.hwnd

		##win32gui.ShowWindow(self.hwnd, win32con.SW_SHOWDEFAULT) 
		#win32gui.UpdateWindow(self.hwnd) 

		__LOG__.Trace( "WINDOW :[%d]" % (g_HWNDMAIN),  (logging.CRITICAL) )

		self.serverIp	= serverIp
		self.serverPort	= serverPort
		self.busTh 		= busThread( self.serverIp, self.serverPort, **opts )
		self.busTh.start()

	#------------------------------------------------------------
	# Function: OnCopyData
	# ARG		: hwnd	- main handle, not dest Handle
	#			: msg
	#			: wparam
	#			: lparam
	#------------------------------------------------------------		
	def OnCopyData(self, hwnd, msg, wparam, lparam):

		try : #{
			#------------------------------------------------------------
			# copyData unpack
			#------------------------------------------------------------
			structure	= ctypes.string_at( lparam, struct.calcsize( g_CopyFmt) )
			data 		= struct.unpack(g_CopyFmt, structure)
			int_data, str_len, str_adr = data
			my_string 	= ctypes.string_at( str_adr, str_len )

			pos = my_string.find('\00' )
			if pos > 0 : my_string = my_string[:pos]
			
			__LOG__.Trace( "%-10s| RECV from Client [%s]:[%s]" % ('DEBUG', hwnd, my_string ), logging.DEBUG )

			#------------------------------------------------------------
			# message split
			#------------------------------------------------------------
			noti_list = my_string.split( DELIMETER_CLI )
			if len( noti_list ) < 3 :
				__LOG__.Trace( "%-10s| client registry bad format [%s]:[%s]" % ('ERROR', hwnd, noti_list), logging.ERROR )
				return

			cmd	= noti_list[0].strip()

			
			#------------------------------------------------------------
			# Client Delete : Client Handle Don't Found, Recv message
			# -- putNoti : SendMessage Error
			#------------------------------------------------------------
			""""
			if 	wparam == self.hwnd	:	# self message : client delete message
				__LOG__.Trace( "%-10s| RECV from [CLEINT DELETE][%s]:[%s]" % ('ERROR', hwnd, my_string ), logging.ERROR )

				hWnd		= None
				className 	= noti_list[1].strip()

				try :			# search handle in Client Hash
					hWnd		= int(className )
					connector 	= self.ConnectorHash[ hWnd ]
				except Exception : __LOG__.Exception()

				###connector.deregister()
				try 	: del( self.ConnectorHash[ hWnd ] )
				except 	: pass
				
				return
			"""
			
			#-----------------
			# message : REG
			#-----------------
			if cmd == 'REG' :
				hWnd		= None
				className 	= noti_list[1].strip()

				try :				# search handle in Client Hash
					hWnd	= int(className )
				except Exception : __LOG__.Exception()

				try :
					connector    = self.ConnectorHash[ hWnd ]
				except KeyError:  # hwnd, new Connector
					
					connector   = Connector(hWnd, key1Hash, key2Hash, keyBothHash, self.conList )
					self.ConnectorHash[hWnd] = connector
					
				msg = DELIMETER_BUS.join( noti_list[2:] )

				try:			
					connector.register(msg)
					__LOG__.Trace( "%-10s| [%s] client complete [%s]:[%s]" % ('INFO', cmd, hWnd, my_string ), logging.INFO )				
				except:	__LOG__.Exception()
			
			#-----------------
			# message : DRG
			#-----------------
			elif cmd == 'DRG' :		# deregistartion
				hWnd		= None
				className 	= noti_list[1].strip()

				try :
					hWnd	= int(className )
				except Exception , e: __LOG__.Exception()

				try :				
					connector    = self.ConnectorHash[ hWnd ]
				except KeyError:  # hwnd, new Connector
					__LOG__.Trace("%-10s| [%s]  client don't found key, first registration [%s]:[%s]" % ( 'ERROR', cmd, hWnd, my_string ), logging.ERROR )
					return

				try :				
					connector.deregisterOfKey( noti_list[2:] )
					__LOG__.Trace( "%-10s| [%s] client complete [%s]:[%s]" % ('INFO', cmd, hWnd, my_string ), logging.INFO )			
				except : __LOG__.Exception()
		
			#-----------------
			# message : NTI/STI
			#-----------------	
			elif cmd == 'NTI' or cmd == 'STI' :
				try:
					msg = DELIMETER_BUS.join( noti_list[1:] ).strip('\n')	# strip 1 over '\n'
					self.busTh.sf.write(' ', cmd , msg+'\n'  )

					__LOG__.Trace( "%-10s| SEND [%s] to Bus [%s]" % ('INFO', cmd, msg ), logging.INFO )
				except :
					__LOG__.Exception()

					self.busTh.sf.close()
					if self.busTh.connectToServer( g_RETRY_BUS ) :				
						pass
					else :  # retry connect fail
						win32gui.SendMessage( self.hwnd, win32con.WM_DESTROY, 0, 0 )

			#-----------------
			# message : DIS
			#-----------------	
			elif cmd == 'DIS':		
				__LOG__.Trace( "%-10s| [%s] total:[%d] ==================================" % ('DEBUG', cmd , len(self.ConnectorHash) ), logging.CRITICAL )
				for keys, value in key1Hash.iteritems() :	# keys, value : connector list
					__LOG__.Trace( "%-10s| [%s][key1   ]	[%s]#[%s]" % ('DEBUG', cmd, keys, len(value) ), logging.CRITICAL )
					
				for keys, value in key2Hash.iteritems() :
					__LOG__.Trace( "%-10s| [%s][key2   ]	[%s]#[%s]" % ('DEBUG', cmd, keys, len(value) ), logging.CRITICAL )
					
				for keys, value in keyBothHash.iteritems() :
					__LOG__.Trace( "%-10s| [%s][keyBoth]	[%s]#[%s]" % ('DEBUG', cmd, keys, len(value) ), logging.CRITICAL )
					
			else :	__LOG__.Trace( "%-10s| bad cmd format [%s]" % ('ERROR', my_string), logging.ERROR )
		#}
		except :
			__LOG__.Exception()
			win32gui.DestroyWindow(self.hwnd)
			
		""" 
		#hdc=win32gui.GetDC(hwnd);
		#win32gui.DrawText(hdc, msg, 1, (15,20, 500,500), 1);
		#win32gui.ReleaseDC(hwnd, hdc);
		"""

	def OnDestroy(self, hwnd, msg, wparam, lparam):

		__LOG__.Trace( "OnDestroy Call +++++++++++++++++++++++++++++++++++++++++++++++++" , (logging.CRITICAL) )			
		#win32gui.DestroyWindow(self.hwnd)
		
		try:    win32gui.UnregisterClass(self.cAtom, self.hinst) 
		except: pass

		global SHUTDOWN
		if not SHUTDOWN :	# User Close		
			if self.busTh :
				if self.busTh.isAlive():
					self.busTh.kill()	
					self.busTh.join()		

			__LOG__.Trace( "BUS THREAD END +++++++++++++++++++++++++++++++++++++++++++++++++" , (logging.CRITICAL) )			

		__LOG__.Trace( "OnDestroy END +++++++++++++++++++++++++++++++++++++++++++++++++" , (logging.CRITICAL) )
		win32gui.PostQuitMessage(0)

	def OnClose(self, hwnd, msg, wparam, lparam):      

		__LOG__.Trace( "OnClose END +++++++++++++++++++++++++++++++++++++++++++++++++" , (logging.CRITICAL) )			
		win32gui.DestroyWindow(self.hwnd)

		"""		
		try:    win32gui.UnregisterClass(self.cAtom, self.hinst) 
		except: pass

		if self.busTh :
			self.busTh.kill()
			self.busTh.join()

		__LOG__.Trace( "END +++++++++++++++++++++++++++++++++++++++++++++++++" , (logging.CRITICAL) )			
		win32gui.PostQuitMessage(0)
		"""

def main( **opts):

	global g_INIT_KEY
	global g_DEBUG_LEVEL
	global key1Hash, key2Hash, keyBothHash

	optStr = sfp.getOptStr()
	optList, args = getopt.getopt(sys.argv[1:], optStr, ['level=', 'output-file='] )

	opts = {}
	for optKey, optVal in optList : opts[optKey] = optVal
		
	SERVER_IP 		= args[0]
	SERVER_PORT 	= int( args[1] )
	winClassName 	= args[2]

	g_INIT_KEY	= '*,*'
	if len( args ) > 3 :
		g_INIT_KEY = DELIMETER_BUS.join( args[3:] )
	
	key1Hash = {}
	key2Hash = {}
	keyBothHash = { '*,*':[] }

	w = gsWindow( winClassName, SERVER_IP, SERVER_PORT, **opts ) 
	win32gui.PumpMessages()

if __name__ == "__main__":

	try :
		optStr = sfp.getOptStr()
		optList, args = getopt.getopt(sys.argv[1:], optStr, ['level=', 'output-file='] )
		if len(args) < 3 : raise Exception
		opts = {}
		for optKey, optVal in optList : opts[optKey] = optVal
	except :
		print 'usage : %s [-options] [--level=] serverIp, port, winClassName, key[default:*,*]' % (sys.argv[0])
		print 'examp : %s 10.10.10.10 1234 WinAdapter' % (sys.argv[0])

		sfp.prnOpt()
		print "        --level     : CRITICAL / ERROR / WARNING / INFO / DEBUG"
		print sys.exc_info()
		sys.exit()

	#-----------------------------------------------------------------------
	# Log Const LEVEL variable Resetting :
	#			__LOG__ library : if level > self.level : return
	#
	# 			CRITICAL 	/ ERROR / WARNING 	/ INFO 	/ DEBUG	/ NOTSET
	#	ORG:		5		/	4	/	3		/	2	/	1	/ 0
	#	THIS:		0		/	1	/	2		/	3	/	4	/ 5	
	#-----------------------------------------------------------------------
	logging.CRITICAL 	= 0
	logging.ERROR	 	= 10
	logging.WARNING	 	= 20
	logging.INFO		= 30
	logging.DEBUG		= 40
	logging.NOTSET		= 50
	#-----------------------------------------------------------------------
	
	strLevel = ''
	if opts.has_key( '--level' ) :
		strLevel = opts['--level'].strip()

		if	 strLevel == 'NOTSET' 	: g_DEBUG_LEVEL = logging.NOTSET	#0		
		elif strLevel == 'DEBUG' 	: g_DEBUG_LEVEL = logging.DEBUG		#10 
		elif strLevel == 'INFO' 	: g_DEBUG_LEVEL = logging.INFO		#20
		elif strLevel == 'WARNING'	: g_DEBUG_LEVEL = logging.WARNING	#30
		elif strLevel == 'ERROR' 	: g_DEBUG_LEVEL = logging.ERROR		#40
		elif strLevel == 'CRITICAL' : g_DEBUG_LEVEL = logging.CRITICAL	#50
		else :	g_DEBUG_LEVEL = logging.ERROR							#ERROR : 40
						
	else :
		g_DEBUG_LEVEL 	= logging.ERROR								#
		strLevel 		= 'ERROR'

	try :
		if opts.has_key( '--output-file' ) :
			fileName 	= opts['--output-file'].strip()		
			g_OUT_FILE	= open( fileName , 'w')

			#logfile = open('.\wa_bus.log', 'w')

	except :
		print "ERROR : Check output-file=: ", fileName, sys.exc_info()
		time.sleep(10)
		sys.exit()

	LOG_FILE = '%s.log' % sys.argv[0]
	Log.Init( Log.CRotatingLog( LOG_FILE, 10000000, 5, 'a+', g_DEBUG_LEVEL ) )
	__LOG__.Trace( "START :LEVEL [%s:%d], KEY:[%s]+++++++++++++++++++++++++++++++++++++++++++++++++" % (strLevel,g_DEBUG_LEVEL, g_INIT_KEY),  (logging.CRITICAL) )


	""" - TEST
	print "#########################################################"
	impStepList = extract_stack()
	impStepList.reverse()
	
	for impStep in impStepList:
		print "@@@@@@ ", impStep

	if(len(impStepList)!=1 ) :
		try : 
			parentModulePath = impStepList[0][0]

			print ">>>>>>>>>>>>>>", parentModulePath 		
		except :
			import psyco
			frame = psyco._getemulframe()
			parentModulePath = frame.f_code.co_filenam

		print "++++++", parentModulePath
			
		curModule = None
			
		for name in  sys.modules :
			moduleInfo = str(sys.modules[name])

			print "$$$$$$$$$$$$ : ", name , "------>", moduleInfo			
			if (moduleInfo.find( '__main__' ) != -1) : 		
				print "OKOKOK!!! : ", name , "------>", moduleInfo
				curModule = sys.modules[name]

				break;			

		sys.modules['__main__'] = curModule
	"""
	
	
	main() 
