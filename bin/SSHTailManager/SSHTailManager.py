#!/usr/bin/env python
#-*- coding:utf-8 -*-

#LTER 김포 SSHTailManager 수정 파일

import sys
import re
import os
import types
import time
import re
import socket  # socket
import signal
import collections
import ConfigParser
import MySQLdb

import paramiko
import threading


#import Mobigen.Common.Log as Log; Log.Init()
import Mobigen.Common.Log as Log

#Parser
from TEventManager import SMSIParser
from TEventManager import AddNetDefaultParser
from TEventManager import PM_AddNetParser
from TEventManager import EMPParser
from TEventManager import Z2_INT_Parser
from TEventManager import Z1_ECI_Parser
from TEventManager_SMSC import SMSCParser


LOOP = True

proc_manager = None

SHUTDOWN = False

class IndxHandler :

	def __init__(self, sRdir, sBase, sRidx) :

		self.sRdir = sRdir      # for default filename
		self.sBase = sBase
		self.sRidx = sRidx

		if not os.path.exists(os.path.dirname(self.sRidx)) :
			os.makedirs(os.path.dirname(self.sRidx))

	def read(self) :

		try :

			oIndx = open( self.sRidx, 'r')
			sName, sLnum = oIndx.readline().strip().split(',')
			oIndx.close()

		except Exception, ex :

			sName, sLnum = self.make()

		return ( sName, int(sLnum) )

	def save(self, sName, sLnum) :

		try :

			oIndx = open( self.sRidx, 'w' )
			oIndx.write( sName + "," + str(sLnum) + "\n")
			oIndx.close()

		except Exception, ex :

			__LOG__.Exception("Oops: %s" % (str(ex)))
			pass

	def make(self) :

		#self.sBase = self.sBase.replace('%', '%%')
		__LOG__.Trace(self.sBase)
		sTemp = time.strftime( self.sBase ) if  self.sBase.find('%') >= 0 else self.sBase
		sRdnm = os.path.join( self.sRdir, sTemp ); sRnum = "0"
		__LOG__.Trace(sRdnm)

		return ( sRdnm, sRnum )

class SSHTailer :

	def __init__(self, sHost, sPort, sUser, sPass, sRdir, sPatn, sBase, sLdir, sRidx,sSect) :#, sIdir, sInam) :


		self.bLoop = True

		self.sHost = sHost
		self.sPort = sPort
		self.sUser = sUser
		self.sPass = sPass

		self.sRdir = sRdir
		self.sPatn = sPatn
		self.sBase = sBase
		self.sLdir = sLdir
		self.sRidx = sRidx

		self.sSect = sSect

		if not os.path.exists(self.sLdir) :
			os.makedirs(self.sLdir)

		# for find command
		self.sTdir = os.path.dirname ( os.path.join( sRdir, sPatn ) )
		self.sTnam = os.path.basename( os.path.join( sRdir, sPatn ) )

		self.oIndx = IndxHandler( self.sRdir, self.sBase, self.sRidx )
		self.sName, self.iLine = self.oIndx.read()
		__LOG__.Trace("Read: Indx ( %s, %d )" % ( self.sName, self.iLine ))

		self.hSSH = {}
		self.hSSH["C"]  = [ self.connect(), None, None, None ]
		self.hSSH["T"]  = [ self.connect(), None, None, None ]

		stdin, stdout, stderr = self.hSSH["C"][0].exec_command("uname")
		sdata = ''.join( stdout.readlines() )
		sdata = sdata.replace('\n', '').strip()
		sdata = sdata.upper()

		self.sOsnm = ''
		self.sPpid = ''

		self.encode= ''

		if       "LINUX" in sdata :
			self.hSSH["C"][1] = 'find %s -maxdepth 1 -name "%s" -print'
			self.hSSH["T"][1] = 'echo $$; tail -n +%d -f %s'
			self.encode = 'utf8'
		elif "SUNOS" in sdata :
			self.hSSH["C"][1] = 'find %s -name "%s" -print'
			self.hSSH["T"][1] = 'echo $$; tail +%df %s'
			self.encode = 'cp949'
		else :
			self.hSSH["C"][1] = 'find %s -name "%s" -print'
			self.hSSH["T"][1] = 'echo $$; tail -n +%d -f %s'

		self.sOsnm = sdata

	def __del__(self) :

		self.clear()

	def stop(self) :

		self.bLoop = False

		self.clear()

	def clear(self) :

		try :   self.cleanup()
		except : pass
		try :   self.disconnect()
		except : pass

	def check(self) :

		if      not self.isexistname() :

			sName = self.getnextname()

			if      not sName :
				return False

			self.sName = sName; self.iLine = 1

		self.execute(); return True

	def connect(self) :

		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname=self.sHost, port=int(self.sPort), username=self.sUser, password=self.sPass, timeout = 10)

		__LOG__.Trace("Conn: %s/%s %s/%s" % (self.sHost, self.sPort, self.sUser, self.sPass))

		return ssh

	def reconnect(self) :

		self.disconnect()

		self.hSSH["C"][0] = self.connect()
		self.hSSH["T"][0] = self.connect()

		__LOG__.Trace("Reco: %s/%s" % (self.sHost, self.sPort))

	def disconnect(self) :

		try     : self.hSSH["C"][0].close()
		except : pass
		try     : self.hSSH["T"][0].close()
		except : pass

		__LOG__.Trace("Disc: %s/%s" % (self.sHost, self.sPort))

	def getnames(self) :

		Names = []

#	       self.hSSH["C"][2] = self.hSSH["C"][1] % ( self.sRdir, self.sPatn )
		self.hSSH["C"][2] = self.hSSH["C"][1] % ( self.sTdir, self.sTnam )


		stdin, stdout, stderr= self.hSSH["C"][0].exec_command( self.hSSH["C"][2] )

		for sName in stdout.readlines() :

			sName = sName.strip()
			Names.append( sName )

		Names.sort()

		__LOG__.Trace("Comd: %s" % ( self.hSSH["C"][2] ))
		__LOG__.Trace("Chck: Curr:%s, Last:%s" % ( self.sName, Names[-1:] ))

		return Names

	def execute(self) :

		Sess = self.hSSH["T"][0].get_transport().open_session()
		Sess.settimeout(10)
		self.hSSH["T"][3] = Sess.makefile()

		self.hSSH["T"][2] = self.hSSH["T"][1] % ( self.iLine, self.sName )
		Sess.exec_command( self.hSSH["T"][2] ) #"cd %s; %s" % ( self.sRdir, sComd ) )

		__LOG__.Trace("Comd: %s" % ( self.hSSH["T"][2] ))

	def cleanup(self) :


		sComd = 'ps -ef|grep %s|grep -v grep' %(self.sPpid)

		Sess = self.hSSH["T"][0].get_transport().open_session()
		Temp = Sess.makefile()
		Sess.exec_command( sComd )

		for sPros in Temp.xreadlines() :

			lWord = sPros.split()
			if len(lWord) < 2 :

				continue

			elif lWord[2] == self.sPpid :

				sComd = 'kill -9 %s' %(lWord[1])
				break

			else :

				# ps -fu eva | grep 'tail -f SRQA03-omc_log-20150501.log' | grep -v grep | awk '{print $2}'
				sComd = "kill -9 `ps -fu %s | grep '%s' | grep -v grep | awk '{print $2}'`" % ( self.sUser, self.hSSH["T"][2] )
				#sComd = "kill -9 %s"%(self.sPpid)

		self.hSSH["T"][0].get_transport().open_session().exec_command( sComd )

		__LOG__.Trace("Comd: %s" % ( sComd ))

	def getnextnames(self) :

		Nexts = []

		for sName in self.getnames() :

			if  sName > self.sName :

				Nexts.append( sName )

		return Nexts

	def isexistname(self) :

		for sName in self.getnames() :

			if  sName == self.sName :
				return True

		else :
			return False


	def getnextname(self) :

		Nexts = self.getnextnames()

		if  Nexts : return Nexts.pop(0)
		else      : return None

	def collect(self) :

		iRcnt = 0

		while self.bLoop :

			data = ''

			try :

				#data = self.hSSH["T"][3].readline()
				#data = self.hSSH["T"][3].readlines()
				if self.sSect =='PM_ADDNET1' or self.sSect =='PM_ADDNET2':
					sBnam = time.strftime("STATUS_%Y%m%d.csv")  #SAVE FILE NAME PATTERN
				else:
					sBnam = self.sName
				sLdnm = os.path.join( self.sLdir, os.path.basename( sBnam  ) )
				self.oFile = open( sLdnm, "a" )
				tmp = self.hSSH["T"][3].readline().strip()

				if tmp != '' :

					self.sPpid = tmp
					iRcnt = 0
					__LOG__.Watch( self.sPpid )

				else  :

					iRcnt += 1
					if iRcnt >= 10 : raise Exception("Get Line Abnormal State.")
					else : continue

				sTemp = ''
				if self.encode != 'cp949':
					sTemp = self.hSSH["T"][3].readline()
				else:
					sTemp = self.hSSH["T"][3].readline().decode('cp949')

				if not  sTemp.strip() == '' :

					self.oFile.write( sTemp ); self.oFile.flush()
					yield  sTemp


				for line in self.hSSH["T"][3].xreadlines() :

					self.oFile.write( line ); self.oFile.flush()
					yield line

			except socket.timeout :

				__LOG__.Trace("timeout!")

				if  not self.bLoop :

					break

				sNext = self.getnextname()

				# for simulation
				if  sNext :

					self.cleanup(); time.sleep(10)

					self.sName = sNext; self.iLine = 1
					self.execute()

					continue

				self.cleanup(); time.sleep(10)
				#self.sName = self.sName; self.iLine = 1
				self.reconnect()
				self.execute()
				continue

			except Exception, ex :

				__LOG__.Exception()
				sNext = self.getnextname()

				if  sNext :

					self.cleanup(); time.sleep(10)
					self.sName = sNext; self.iLine = 1
					self.execute()
					continue

				self.cleanup(); time.sleep(10)
				#self.sName = self.sName; self.iLine = 1
				self.reconnect()
				self.execute()

	def fileinfo(self) :

		return ( self.sName, self.iLine )

	def filename(self) :

		return self.sName

	def fileindx(self) :

		return self.iLine

class DBMySQL:

	def __init__(self,sSect,PARSER):

		self.PARSER = PARSER
		self.sSect = sSect
		self.set_config()

	def set_config(self):
		self.li_equip = []
		self.status_db = -1 # 0: connected 1,2,3,4,,,,: reconnection count
		try:    self.equip_group_name = self.PARSER.get(self.sSect,'EQUIP_GROUP')
		except: self.equip_group_name = '-'
		__LOG__.Trace(self.equip_group_name)

	def connect_db(self):

		if self.status_db > 0:
			__LOG__.Trace("Try Reconnection .....(%d)"%self.status_db)

		try:
			self.con = MySQLdb.connect(
					host = '211.237.65.153',
					port = 3306 ,
					user = 'sktlnms',
					passwd = '!Hello.nms0',
					db = 'SKTLNMS',
				)

			self.con.set_character_set('UTF8')
			self.con.autocommit(True)
			self.cur = self.con.cursor()
			self.status_db = 0
		except Exception:
			__LOG__.Exception()
			time.sleep(30)
			self.status_db += 1
			if self.status_db <4:
				self.connect_db()
			else:
				sys.exit()


	def disconnect_db(self):

		try:    self.cur.close()
		except: pass
		try:    self.con.close()
		except: pass

	def __del__(self):
		self.disconnect_db()

	def query_equip(self, retry = 0):       #DB에서 알람 정보 GET

		sql = """
		   SELECT NE_ID, NE_NAME, N.EQUIP_TYPE_ID AS EQUIP_TYPE_ID, EQUIP_TYPE_NAME, VENDOR_ID,E.EQUIP_GROUP_ID AS EQUIP_GROUP_ID, EQUIP_GROUP_NAME, DEL_YN
		   FROM TB_CO_NE N
		   JOIN TB_CO_EQUIP E
		   ON N.EQUIP_TYPE_ID = E.EQUIP_TYPE_ID
		   JOIN TB_CO_EQUIP_GROUP G
		   ON E.EQUIP_GROUP_ID = G.EQUIP_GROUP_ID
		   WHERE N.DEL_YN = 'N'
		"""

		try:
			self.cur.execute(sql)
			rows = self.cur.fetchall()
			self.li_equip = []

			for row in rows:

				equip = {}

				ne_id, ne_name, equip_type_id, equip_type_name, vendor_id, equip_group_id, equip_group_name, del_yn = row
				#__LOG__.Trace("ne_id : %s, ne_name : %s, equip_type_id : %s, equip_type_name : %s, vendor_id : %s, equip_group_id %s, equip_group_name : %s"% row)
				equip["NE_ID"] = ne_id
				equip["NE_NAME"] = ne_name
				equip["EQUIP_TYPE_ID"] = equip_type_id
				equip["EQUIP_TYPE_NAME"] = equip_type_name
				equip["VENDOR_ID"] = vendor_id
				equip["EQUIP_GROUP_ID"] = equip_group_id
				equip["EQUIP_GROUP_NAME"] = equip_group_name
				equip["DEL_YN"] = del_yn

				self.li_equip.append(equip)
		except MySQLdb.OperationalError as e:
			self.disconnect_db()
			__LOG__.Trace("ERROE : %s"%e)
			self.connect_db()
			retry += 1
			if retry <= 3 :
				self.query_equip(retry)

		except Exception:
			__LOG__.Exception()


	def get_equip(self, ne_info):   # 장비 정보 조회

		ne_key , ne_val = ne_info

		for equip in self.li_equip:

			if equip[ne_key] == ne_val:

				return equip

		return {}

	def query_alarm(self, retry = 0):       # DB에서 알람 정보 GET
		if self.equip_group_name != '-':

			try :
				sql = """
					SELECT F.EQUIP_TYPE_ID, ALARM_CODE, ALARM_NAME, ALARM_DESC
					FROM TB_FM_ALARM_CODE_INFO F,
						(   select E.EQUIP_TYPE_ID from TB_CO_EQUIP E,TB_CO_EQUIP_GROUP G
							WHERE E.EQUIP_GROUP_ID= G.EQUIP_GROUP_ID and G.EQUIP_GROUP_NAME ='%s') T
					WHERE F.EQUIP_TYPE_ID =T.EQUIP_TYPE_ID AND F.DEL_FLAG = 'N'
				"""
				__LOG__.Trace( sql %( self.equip_group_name ))

				try:

					self.cur.execute( sql % ( self.equip_group_name ) )
					rows = self.cur.fetchall()

					self.dict_alarm = {}
					for row in rows:

						try:
							equip_type_id, alarm_code, alarm_name, alarm_desc  =row

							if equip_type_id not in self.dict_alarm:
								self.dict_alarm[equip_type_id] = []

							alarm = {}

							alarm['ALARM_CODE']=alarm_code
							alarm['ALARM_NAME']=alarm_name
							alarm['ALARM_DESC']=alarm_desc

							self.dict_alarm[equip_type_id].append(alarm)

						except:
							__LOG__.Exception()
					__LOG__.Trace("SUCCESS ALARM QUERY")

				except MySQLdb.OperationalError as e:
					self.disconnect_db()
					__LOG__.Trace("ERROR : %s"%e)
					self.connect_db()
					retry += 1
					if retry <= 3 :
						self.query_alarm(retry)

				except Exception:
					__LOG__.Exception()

			except :
				__LOG__.Exception()



	def query_alarms(self,equip_type_id,vendor_id, where):
		li = []

		try :
			sql = """SELECT ALARM_CODE,ALARM_NAME,ALARM_DESC FROM TB_FM_ALARM_CODE_INFO WHERE EQUIP_TYPE_ID= '%s' AND VENDOR_ID = '%s'"""

			__LOG__.Trace( sql % ( equip_type_id, vendor_id))
			sql = sql % (equip_type_id, vendor_id)

			sql += where
			try:
				self.cur.execute( sql )
				rows = self.cur.fetchall()
				for cols in rows :
					li.append(cols)

			except MySQLdb.OperationalError as e:
				__LOG__.Trace("ERROE : %s"%e)
				self.connect_db()

			except Exception:
				pass
				#__LOG__.Exception()

			#__LOG__.Trace("%s %s %s"%(repr(alarm_code),repr(alarm_name),repr(alarm_desc)))
		except :
			__LOG__.Exception()

		return li

	def get_alarm(self,alarm_info): # 알람 조회

		equip_type_id , alarm_key , alarm_val = alarm_info

		li_alarm = self.dict_alarm[equip_type_id]

		for alarm in li_alarm:

			if alarm[alarm_key] == alarm_val:

				return alarm

		return {}

	def listen_stdin(self): #구성정보나 알람정보 변경시 갱신

		data = ''

		global SHUTDOWN
		__LOG__.Trace('listen_stdin START............')
		while not SHUTDOWN:
			try:

				data = sys.stdin.readline()
				__LOG__.Trace('STD IN : %s'%data)
				prefix, alarm_date = data.split('://')
				if prefix=='ALARM':
					self.query_alarm()
				elif prefix=='CONFIG':
					self.query_equip()
			except:
				__LOG__.Trace(data)
				__LOG__.Exception()
				time.sleep(1)

			sys.stderr.write('\n')
			sys.stderr.flush()


	def run(self):

		try:

			self.connect_db()
			self.query_equip()
			self.query_alarm()
			thread_listen = threading.Thread(target=self.listen_stdin,args=())
			thread_listen.daemon = True
			thread_listen.start()


		except Exception:
			__LOG__.Exception()

class ProcessManager(threading.Thread) :

	def __init__(self) :

		threading.Thread.__init__(self)
		self.process_		   self.start_process()


	def stop(self) :

		self.shutdown = True


	def run(self) :

		self.start_process()
		base = ''

		while not self.shutdown :

			self.chk_process()
			"""
			curr = time.strftime("%Y%m%d%H%M")
					if base == '' :
				base = curr

			elif base != curr :


				Base  = curr
				self.chk_process()

			else :

				time.sleep(1)
			"""
			time.sleep(1)
		self.close_porcess()

class Worker :

	def __init__(self, sSect, sConf) :

		self.bLoop = True

		self.sSect = sSect
		self.sConf = sConf

		Conf = ConfigParser.SafeConfigParser()
		Conf.read(sConf)

		self.Conf = Conf

		self.sHost = Conf.get( sSect, "HOST" )
		self.sPort = Conf.get( sSect, "PORT" )
		self.sUser = Conf.get( sSect, "USER" )
		self.pwd_list = Conf.get( sSect, "PASS" ).split(',')
		self.sPass = self.pwd_list[0]
		self.sType = Conf.get( sSect, "TYPE" )
		self.eType = Conf.get( sSect, "EQUIP_TYPE" )

		self.dHost = Conf.get( 'DBMS', "HOST" )
		self.dPort = Conf.get( 'DBMS', "PORT" )
		self.dUser = Conf.get( 'DBMS', "USER" )
		self.dPass = Conf.get( 'DBMS', "PASS" )
		self.dBase = Conf.get( 'DBMS', "BASE" )

		self.sUids = Conf.get( sSect, "UIDS" )
		self.sEndp = Conf.get( sSect, "EPTN" )

		self.sRdir = Conf.get( sSect, "RDIR" )
		self.sPatn = Conf.get( sSect, "PATN" )
		self.sBase = Conf.get( sSect, "BASE" )
		self.sLdir = Conf.get( sSect, "LDIR" )
		self.sRidx = Conf.get( sSect, "RIDX" )


		# for simulation
		try     : self.sIntv = Conf.get( sSect, "INTV" )
		except : self.sIntv = "1"

		self.oData = None
		self.oSndr = None
		self.oPasr = None
		self.oDict = None

		__LOG__.Trace( "Conf: %s" % ( [ self.sType, self.sUids, self.sEndp] ))

		signal.signal(signal.SIGTERM, self.sign)
		signal.signal(signal.SIGINT , self.sign)
		try : signal.signal(signal.SIGHUP , self.sign)
		except : pass
		try : signal.signal(signal.SIGPIPE, self.sign)
		except : pass

		def get_pwd():

			while True:
				for pwd in self.pwd_list:
					yield pwd

		self.pwd_iter = get_pwd()


	# 15:Terminate, 2:Interrupt, 1:Hangup, 13:BrokenPipe
	def sign(self, iNum=0, iFrm=0) :

		__LOG__.Trace("Sign: %d" % (iNum))

		self.bLoop = False

		if      self.oData :

			self.oData.stop()


	def work(self) :

		__LOG__.Trace("Work: strt")

		sBase = time.strftime("%Y%m%d%H%M")

		db_handler = DBMySQL(self.sSect,self.Conf)
		db_handler.run()

		while self.bLoop :

			# check dictionary
			try :
				self.oData = SSHTailer( self.sHost, self.sPort, self.sUser, self.sPass, self.sRdir, self.sPatn, self.sBase, self.sLdir, self.sRidx,self.sSect)
				break
			except paramiko.ssh_exception.AuthenticationException:	  self.sPass = next(self.pwd_iter)
			except :
				__LOG__.Exception()
				try : self.oData.stop()
				except : pass

				__LOG__.Exception()
				time.sleep(60)

		#global proc_manager


		#proc_manager = ProcessManager()
		#proc_manager.deamon = True
		#proc_manager.set_process()
		#proc_manager.start()


		while self.bLoop :

			try :

				while self.bLoop :

					if      self.oData.check() :

						break

					__LOG__.Trace("None: not found '%s'" % ( self.oData.filename() ))

					time.sleep(10)

			except Exception :

				__LOG__.Exception()

				self.oData.stop()
				time.sleep(1)
				try : self.oData = SSHTailer( self.sHost, self.sPort, self.sUser, self.sPass, self.sRdir, self.sPatn, self.sBase, self.sLdir, self.sRidx,self.sSect)
				except paramiko.ssh_exception.AuthenticationException:	  self.sPass = next(self.pwd_iter)
				except : self.oData.stop(); __LOG__.Exception(); time.sleep(10)


			sBase = ''
			sCurr = ''
			sTemp = ''
			iBase = 0

			iCnt = 0

			#Parser 선정
			if       self.sSect ==  "SMSIOAM"	       : self.oPasr = SMSIParser( self.sSect , self.sEndp )
			elif self.sSect ==      "SMSI1"		 : self.oPasr = SMSIParser( self.sSect , self.sEndp )
			elif self.sSect ==      "ADDNET1" or self.sSect ==  "ADDNET2" or self.sSect == 'ADDNET_TEST'	    : self.oPasr = AddNetDefaultParser( self.sSect ,self.Conf)
			elif self.sSect ==  "PM_ADDNET1" or self.sSect ==  "PM_ADDNET2"	 : self.oPasr = PM_AddNetParser( self.sSect, self.Conf )
			elif "EMP"	in  self.sSect		: self.oPasr = EMPParser(self.sSect,self.Conf)
			elif self.sSect == 'z2-SKTL-INT'	: self.oPasr = Z2_INT_Parser(self.sSect,self.Conf)
			elif self.sSect == 'z1-SKTL-ECI'	: self.oPasr = Z1_ECI_Parser(self.sSect,self.Conf)
			elif 'SMSC'     in self.sSect		   : self.oPasr = SMSCParser(self.sEndp, db_handler)

			while self.bLoop :

				try :

					oLine = self.oData.collect() # taiㅣ 수집 데이터
					if      oLine  :
						for sline in oLine :
							__LOG__.Trace("SLINE : %s" % sline)

							if not self.bLoop : break
							self.oData.iLine += 1


							if sline == '' : time.sleep(0); continue

							#sline = re.sub('\r|\x8c|\x00', '', sline)
							sline = re.sub('\r', '', sline)

							if sline :

								#sLine = re.sub('\r|\x8c|\x00', '', sLine)
								#__LOG__.Watch(sline)
								send_data =[]

								try:
									send_data = self.oPasr.parse(sline.strip())
								except Exception:
									__LOG__.Exception()

								if send_data != []:

									ne_id  = send_data[1]
									ne_name = send_data[11]	 #ne_name

									alarm_code = send_data[3]	       #alarm_code
									alarm_name = send_data[4]	       #alarm_name
									equip = {}

									#구성정보 조회 조건
									if ne_id != "-" :	       equip = db_handler.get_equip( ("NE_ID", ne_id) )
									elif ne_name != "-" :   equip = db_handler.get_equip( ("NE_NAME", ne_name) )

									__LOG__.Trace(equip)

									if len(equip) == 0 :
										__LOG__.Trace('Error Equip Exists!! NE_ID[%s], NE_NAME[%s]' % (ne_id, ne_name))

									try:
										if equip["DEL_YN"] == "N":      # 사용 장비 필터
											alarm = {}
											if 'SMSC' not in self.sSect     :
												if alarm_code != '-' :	  alarm = db_handler.get_alarm( (equip['EQUIP_TYPE_ID'], 'ALARM_CODE', alarm_code ) )
												elif alarm_name != '-' :	alarm = db_handler.get_alarm( (equip['EQUIP_TYPE_ID'], 'ALARM_NAME', alarm_name ) )
												send_data[3]    = alarm['ALARM_CODE']										   #alarm_code
												send_data[4]    = alarm['ALARM_NAME']										   #alarm_name
												send_data[10]   = alarm['ALARM_NAME'] if send_data[10]=='-' else send_data[10]  #alarm_desc

											send_data[1]    = equip["NE_ID"]												#NE_ID
											send_data[2]    = "^^".join( [ equip["EQUIP_TYPE_ID"] ,send_data[2],"" ] )	      #equip_type_id^^loca
											send_data[8]    = str(equip["EQUIP_GROUP_ID"])								  #equip_group_id
											send_data[11]   = equip["NE_NAME"]											      #ne_name
											send_data[12]   = equip["EQUIP_TYPE_NAME"]									      #equip_type_name
											send_data[13]   = equip["EQUIP_GROUP_NAME"]									     #equip_group_name

											__LOG__.Trace(send_data)

											if '-'  not in send_data[:14]:  #데이터 규격 확인

												sys.stdout.write("DATA://"+"|^|".join(send_data)+"\n")
												sys.stdout.flush()
												__LOG__.Trace("DATA://"+"|^|".join(send_data))

									except Exception:
										__LOG__.Exception()

									self.oData.oIndx.save( self.oData.sName, self.oData.iLine )
									__LOG__.Trace("Save: Indx ( %s, %d )" % ( self.oData.fileinfo() ))

								sCurr = time.strftime("%Y%m%d%H%M")

								if sBase == '' :

									sBase = sCurr

								elif sBase != sCurr :

									__LOG__.Trace('Reload Dict Data.')
									sBase  = sCurr

								else :
									pass

						self.oData.oIndx.save( self.oData.sName, self.oData.iLine )
						__LOG__.Trace("Save: Indx ( %s, %d )" % ( self.oData.fileinfo() ))

					time.sleep(0)

				except Exception, ex :

					__LOG__.Exception()
					try: self.oData = SSHTailer( self.sHost, self.sPort, self.sUser, self.sPass, self.sRdir, self.sPatn, self.sBase, self.sLdir, self.sRidx,self.sSect)
					except paramiko.ssh_exception.AuthenticationException:	  self.sPass = next(self.pwd_iter)
					time.sleep(1)

		db_handler.disconnect_db()
		#proc_manager.stop()

		__LOG__.Trace("Work: stop")


def main() :

	if  len(sys.argv) < 3 :
		sys.stderr.write("Usage: %s SECTION CONFIG\n" % (sys.argv[0]))
		sys.stderr.flush()
		sys.exit()

	sSect = sys.argv[1]
	sConf = sys.argv[2]

	Conf = ConfigParser.SafeConfigParser()
	Conf.read(sConf)

	sLogd = os.path.expanduser(Conf.get('COMMON', 'LOG'))
	sLogm = _.Trace("process strt: ( pid:%d ) >>>" % (os.getpid()))

	try :

		oWork = Worker(sSect, sConf)
		oWork.work()

	except Exception, ex :

		__LOG__.Exception()

	#proc_manager.stop()
	time.sleep(5)

	__LOG__.Trace("process stop: ( pid:%d ) <<<" % (os.getpid()))

if __name__ == '__main__' :

	main()
