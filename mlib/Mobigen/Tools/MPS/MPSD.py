#!/bin/env python
# coding: utf-8
# -*- coding: <ko_KR.eucKR> -*-
#########################################################
VERSION = '2.2.1'
#########################################################
# version 2.0.0
# update : 2005.04.07 : by yong
# * test completed
#
# version 2.1.0
# update : 2005.04.08 : by yong
# * add process running mode (POP)
# * add process terminate method ( file )
# * add add use or not use force kill( kill -9 )
# 
# version 2.1.1
# * patch - file path argument error pixed
#
# version 2.1.2
# * patch - bug pixed on SUN's thread model
#
# version 2.1.3
# * update - apply run mod(POP) at reboot
#
# version 2.1.4
# * patch out error when get wrong mid
#
# version 2.1.5
# * set PS_TIME when term process
#
# version 2.1.6
# * mps.d로 실행된 프로그램이 리스너 하는 버그 수정함.
#
# version 2.1.7
# * log모듈 사용하도록 수정함.
#
# version 2.1.8
# * SIGCLD를 SIG_IGN 추가함. -> 다시 수정 wait함수에서 이상현상이 보임
#   fork()후 close하는 함수를 수정함.
#
# version 2.2.0
# * re.split() -> shlex.split() 으로 수정
#########################################################

#import psyco
#psyco.profile()

### import python foundation class ###
import os, signal, sys, time, re
import thread
import logging
from logging.handlers import RotatingFileHandler
from socket import *
import ConfigParser
import shlex

import Mobigen.Common.Log as Log; Log.Init()

PS_EXECMD = {}
PS_GROUP = {}
GROUP_PS = {}
PS_PROCNAME = {}
PS_PID = {}
PS_TYPE = {}
PS_DESC = {}
PS_ORDER = {}
PS_TIME = {}
PS_MODE = {}
PS_TERM = {}
PS_FORCE_KILL = {}
OLD_PID = {}

MDIR = '/tmp/mps.d'

SHUTDOWN = False
SYNC = True
CUR_CLIENT_CNT = 0
SERVER_PORT = 1992
MAX_CLIENT_CONN = 20
CONF_FILE = ''
conf = None

lock = thread.allocate_lock()

debug = False

global svrsock

### signal define ###
def sigHandler(sigNum,f) :
	
	global SHUTDOWN

	__LOG__.Trace('[handler] : Term signal received')
	signal.signal(signal.SIGINT, signal.SIG_IGN)	
	signal.signal(signal.SIGTERM, signal.SIG_IGN)	
	SHUTDOWN = True

### signal handler ###
signal.signal(signal.SIGINT, sigHandler)
signal.signal(signal.SIGTERM, sigHandler)
signal.signal(signal.SIGPIPE, signal.SIG_IGN)
signal.signal(signal.SIGHUP, signal.SIG_IGN)

def shutdownChk() :
	global SHUTDOWN

	try :
		while 1 :
			if SHUTDOWN == True : break
			if  os.path.exists(MDIR+'/19990..shutdown') :
				lock.acquire()
				SHUTDOWN = True
				lock.release()
				__LOG__.Trace("[shutdownChk] find shutdown file!!")
				os.unlink(MDIR+'/19990..shutdown')

			time.sleep(1)
	except :
		pass


def loadConf() :

	global SYNC
	global SHUTDOWN
	global PS_EXECMD
	global GROUP_PS
	global PS_GROUP
	global PS_PROCNAME
	global PS_TYPE
	global PS_DESC
	global PS_ORDER
	global PS_TIME
	global PS_MODE
	global PS_TERM
	global PS_FORCE_KILL

	global CONF_FILE
	global conf
	
	__LOG__.Trace('[thReloadConf] : reflesh configuration')
	conf = ConfigParser.ConfigParser()
	conf.read(CONF_FILE)

	lock.acquire()

	PS_EXECMD.clear()  
	GROUP_PS.clear()
	PS_GROUP.clear()
	PS_PROCNAME.clear()
	PS_TYPE.clear()  
	PS_DESC.clear()	
	PS_MODE.clear()
	PS_TERM.clear()
	PS_FORCE_KILL.clear()

	groupMembers = conf.sections()
	
	for sectionName in groupMembers :
		try: (secUnit,groupName) = re.split('\s+',sectionName)
		except: continue
			
		#for(midStr,cmdStr) in conf.items(sectionName) :
		if secUnit == 'Process' :
			for(paramKey,paramVal) in conf.items(sectionName) :
				(mid,termType,desc) = paramKey.split(',')
			#	tmpCmdStr = re.split('\s+',paramVal)
				tmpCmdStr = shlex.split(paramVal)

				processName = tmpCmdStr[0]
				if (os.path.basename(processName) == "python") :
					processName = tmpCmdStr[1]

				if (os.path.basename(processName) == "java") :
					for el in tmpCmdStr :
						if (re.search("\.jar$", el)) :
							processName = el
							break
	
				if ( os.path.exists(processName) == False ) :
					__LOG__.Trace('[thReloadConf] not exist command! - '+ str(processName))
					continue
	
				PS_EXECMD[mid] = paramVal
				PS_TYPE[mid] = termType
				PS_DESC[mid] = desc
				PS_GROUP[mid] = groupName
			#	tmpProcName = re.split('\s+',paramVal)
			#	tmpProcName = shlex.split(paramVal)
				
			#	if (bExecute) : (dummy,procName) = os.path.split(tmpProcName[1])
			#	else : (dummy,procName) = os.path.split(tmpProcName[0])

				(dummy, procName) = os.path.split(processName)

				__LOG__.Trace("dummy(%s), procName(%s)" % (dummy, procName))
				#print "***** " + procName + " ****"
				try :
					PS_PROCNAME[mid] = re.match('(\S+)\s+',procName).group(1)
				except :
					PS_PROCNAME[mid] = procName
	
				if ( GROUP_PS.has_key(groupName) ) :
					GROUP_PS[groupName] = GROUP_PS[groupName] + ',' + str(mid)
				else :
					GROUP_PS[groupName] = mid
		elif secUnit == 'MID' :
			for(paramKey,paramVal) in conf.items(sectionName) :
				if paramKey == 'run mode' : PS_MODE[groupName] = paramVal
				if paramKey == 'shutdown file' : PS_TERM[groupName] = paramVal
				if paramKey == 'use force kill' : PS_FORCE_KILL[groupName] = paramVal
		else :
			continue
				

	# end of construct configuration!!

	for mid in PS_ORDER.keys() :
		if ( PS_PROCNAME.has_key(mid) == False ) :
			del PS_ORDER[mid]
			del PS_TIME[mid]
			thread.start_new_thread(killProc,(mid,))
			#killProc(mid)
		# if end
	# for end

	for mid in PS_PROCNAME.keys() :
		if ( PS_ORDER.has_key(mid) == False ) :
			PS_ORDER[mid] = 'ACT'
			PS_TIME[mid] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())

	lock.release()
#end of loadCon function

def cleanUp():

	global PS_EXECMD

	for grepWord in PS_EXECMD.values() :	
		f = os.popen("ps -efw | grep '" + grepWord + "' | grep -v 'grep'",'r')
		result = f.read().split('\n')

		if len(result) == 0 : continue

		tmpItems = re.split('\s+',result[0])

		if ( len(tmpItems) <= 1 ) : continue

		killPid = int(tmpItems[1])
		__LOG__.Trace("[CLEAN-UP] try kill " + str(killPid) + ", " + grepWord)

		killCount = 0

		while (killCount< 50 ) :
			killCount = killCount + 1
			try :
				os.kill(int(killPid),0)
			except Exception, err :
				__LOG__.Trace('[CLEAN-UP] ' + str(err))
				break
				
			try :
				os.kill(int(killPid),15)
			except Exception, err :
				__LOG__.Trace("[Clean-UP] kill Fail => " + str(killPid) + "," + grepWord)
				__LOG__.Exception(err)

			time.sleep(0.2)
		# end while

		try :
			os.kill(int(killPid),9)
			__LOG__.Trace('Process [' + str(killPid) + ',' + grepWord + '] was killed by force!!')
		except Exception, err:
			pass
	# end for

	__LOG__.Trace('[Clean-UP] Complete clean up')

# end cleanUp function

def thCliSocket(svrsock,thId) :
	
	global SHUTDOWN
	global GROUP_PS
	global PS_ORDER
	global CONF_FILE

	while 1 :
		if SHUTDOWN == True : break

		try :
			(conn, addr) = svrsock.accept()
		except Exception, err:
			time.sleep(0.1)
			continue

		if conn == None :
			__LOG__.Trace('[thCliSocket] Socket accept fail!!')
			break

		__LOG__.Trace('[thCliSocket] client connected : ' + addr[0])

		conn.settimeout(60)

		heartbit = 0
		while 1:
#		{
			if SHUTDOWN == True : break

			try:
				rMsg = conn.recv(3000)

				if rMsg == None : break
				if len(rMsg) == 0 : break

				rMsg = re.sub('\s+$','',rMsg)
				rMsg = re.sub('^\s+','',rMsg)
			except:
				heartbit = heartbit + 60
				__LOG__.Trace('[thCliSocket:'+addr[0]+'] no cmd received!!')
				continue


			__LOG__.Trace('[thCliSocket:'+addr[0]+'] recv cmd : ' + rMsg)
			
			cmdItems = re.split('\s+',rMsg)
			cmd = cmdItems.pop(0)
			cmd = cmd.upper()

			try :
	
				if(cmd == '<BYE>' or cmd == 'EXIT' or cmd == 'QUIT' or cmd == 'BYE') :
					__LOG__.Trace('[thCliSocket:'+addr[0]+'] recv quit msg : '+cmd)
					conn.send('<EXIT>\n')
					break
				elif(cmd == 'SHOW') :
					__LOG__.Trace('[thCliSocket:'+addr[0]+'] recv show cmd : ' + cmd)
					if ( len(cmdItems) == 0 ) :
						showItem(conn,'all')
					else :
						 showItem(conn,cmdItems[0])
				elif(cmd == 'ACT' or cmd == 'TERM') :
					__LOG__.Trace('[thCliSocket:'+addr[0]+'] recv cmd : ' + cmd )
	
					mids = []
					if ( len(cmdItems) > 0 ) :
						if ( len(cmdItems) == 1 and re.match('^\D+',cmdItems[0]) ) :
							if ( cmdItems[0] == 'all' ) :
								mids = PS_ORDER.keys()
							elif ( GROUP_PS.has_key(cmdItems[0]) ) :
								tmpMids = GROUP_PS[cmdItems[0]]
								mids = tmpMids.split(',')
							else :
								conn.send("<error>\n")
								conn.send(cmdItems[0] + "not exists int group member\n")
								conn.send("<end>\n")
						else :
							for tmpArgs in cmdItems :
								if  re.match('(\d+)-(\d+)',tmpArgs) :
									m = re.match('(\d+)-(\d+)',tmpArgs)
									for i in range(int(m.group(1)),int(m.group(2)) + 1) :
										if str(i) in PS_ORDER.keys() :
											mids.append(str(i))
								elif re.match('(\d+)',tmpArgs) :
									mids.append(tmpArgs)
								else :
									continue
					else :
						conn.send("<error>\n")
						conn.send("need MID or GROUP_NAME or all\n")
						conn.send("<end>\n")
						continue
	
					__LOG__.Trace('[thCliSocket:'+addr[0]+'] cmd : mids => ' + str(mids))
	
					mids.sort()
	
					for mid in mids:
						if PS_ORDER.has_key(mid) == False : 
							conn.send("<error>\n")
							conn.send(str(mid) + " is not defined in configure file\n")
							conn.send("<end>\n")
							continue

						lock.acquire()
						PS_ORDER[mid] = cmd
						lock.release()
	
						if cmd == 'TERM' :
							thread.start_new_thread(killProc,(mid,))
							#killProc(mid)
							try :
								os.unlink(MDIR+'/'+str(mid)+'.ACT')
							except Exception, err :
								__LOG__.Trace(err)
				elif ( cmd == 'SYNC' ) :
					loadConf()
					time.sleep(2)
				elif ( cmd == 'HELP' ) :
					conn.send('help start \n')
					conn.send('Usage_1 : Command by process  => [term|act] 1000-1003 1007....\n')
					conn.send('Usage_2 : Command by group    => [term|act] group_name\n')
					conn.send('Usage_3 : Display by group    => show group_name\n')
					conn.send('Usage_4 : Show all list of item   => show all \n')
					conn.send('Usage_5 : Show help message     => [help]\n')
					conn.send('Usage_6 : Apply after edit configure file => sync\n')
					conn.send('Usage_7 : Quit this console => quit\n')
					conn.send('help end \n')
					continue
				else :
					continue
				
				if cmd != 'SHOW' : showItem(conn,'all')

			except Exception, err:
				__LOG__.Trace(err)
				sys.exit()
				break

			time.sleep(0.2)
#		} while
		try : conn.close()
		except : pass
	
	try : svrsock.close()
	except : pass
	__LOG__.Trace('[thCliSocket] server socket closed ID ' + str(thId))
#	}

def thChldUp(mid) :
	global PS_EXECMD
	global PS_PROCNAME
	global PS_ORDER
	global PS_TIME
	global PS_PID
	global PS_MODE
	global OLD_PID

	cmdStr = PS_EXECMD[mid]
	procName = PS_PROCNAME[mid]

	while ( SHUTDOWN == False ) :

		try :
			if PS_ORDER[mid] == 'TERM' :
				__LOG__.Trace("[thChldUp]["+str(mid)+":"+procName+"] received TERM cmd")
				break
			elif PS_ORDER.has_key(mid) == False or PS_ORDER[mid] != 'ACT' :
				__LOG__.Trace("[thChldUp]["+str(mid)+":"+procName+"] undefined command")
				break
		except Exception,err :
			__LOG__.Trace(err)
			time.sleep(1)
			break


		__LOG__.Trace("[thChldUp]["+str(mid)+":"+procName+"] ACT")


		# add by truelsy@mobigen.com (2012/05/14)
		#items = re.split('\s+',cmdStr)
		items = shlex.split(cmdStr)
		__LOG__.Trace("+++ items (%s)" % items)

		processName = items[0]
		if (os.path.basename(processName) == "python") :
			processName = items[1]

		if (os.path.basename(processName) == "java") :
			bExecuteJava = False
			for item in items :
				if (re.search("\.jar$", item)) :
					bExecuteJava = True
					processName = item
					break

			if not bExecuteJava :
				__LOG__.Trace("[thChldUp]["+str(mid)+":"+procName+"] can't execute!!")
				break

		if os.path.exists(processName) == False :
			__LOG__.Trace("[thChldUp]["+str(mid)+":"+procName+"] can't execute!!")
			break


		PS_TIME[mid] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())

		pid = 0
		try :
			pid = os.fork()

			if pid == 0 :
				global svrsock
				if svrsock:
					os.close(svrsock.fileno())
					svrsock = None
				filePath = items[0]
				(dummy,items[0]) = os.path.split(filePath)

				__LOG__.Trace("filePath (%s)" % filePath)
				__LOG__.Trace("items (%s)" % items)

				os.execl(filePath,*tuple(items))
				sys.exit(0)
			else :
				PS_PID[mid] = pid
				OLD_PID[mid] = pid
				os.system("touch "+ MDIR + '/' +str(mid)+".ACT")
		except Exception, err :
			__LOG__.Trace(err)
			break;
		
		__LOG__.Trace("[thChldUp]["+str(mid)+":"+procName+"] success forked.. waitting now..")

		try :
			os.waitpid(pid,0)
		except :
			break
		
		if PS_ORDER[mid] == 'ACT' :
			__LOG__.Trace("[thChldUp]["+str(mid)+":"+procName+":"+str(pid)+"] ABNORMAL_TERM")
			if PS_MODE.has_key(mid) and PS_MODE[mid] == 'POP' :
				__LOG__.Trace("[thChldUp]["+str(mid)+":"+procName+"] Wake UP!! but POP mode!!")
				lock.acquire()
				if PS_PID.has_key(mid) : del PS_PID[mid]
				PS_ORDER[mid] = 'TERM'
				lock.release()
				break

		__LOG__.Trace("[thChldUp]["+str(mid)+":"+procName+"] Wake UP!! going to restart!!")


		time.sleep(1)
	__LOG__.Trace("[thChldUp]["+str(mid)+":"+procName+"] thread out of life !! ")


def killProc(mid) :
	global PS_TYPE
	global PS_PROCNAME
	global PS_ORDER
	global PS_TIME
	global PS_PID
	global PS_TERM
	global PS_FORCE_KILL

	procName = "***"
	pid = 0 
	termType = 15

	if PS_PID.has_key(mid)  : pid = PS_PID[mid]
	if PS_TYPE.has_key(mid)  : termType = PS_TYPE[mid]
	if PS_PROCNAME.has_key(mid) : procName = PS_PROCNAME[mid]


	if PS_TIME.has_key(mid) :
		PS_TIME[mid] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())

	if pid == 0 : return

	if PS_TERM.has_key(mid) :
		os.system("touch " + PS_TERM[mid] )

	killCount = 0

	while 1  :
		killCount = killCount + 1
		if killCount > 50 : break

		try :
			os.kill(int(pid),0)
		except Exception, err :
			__LOG__.Trace('[killProc] ' + str(err))
			break
			
		try :
			os.kill(int(pid),int(termType))
			__LOG__.Trace( "TRY TO KILL!!!!!! (" + str(killCount) + ")"  + str(pid) )
		except Exception, err :
			__LOG__.Trace("[killProc] kill Fail => " + str(pid) )
			__LOG__.Exception(err)

		time.sleep(0.1)
	# end while

	if PS_FORCE_KILL.has_key(mid) == False or PS_FORCE_KILL[mid] != 'NO' :
		try :
			os.kill(int(pid),9)
			__LOG__.Trace('Process [' + str(pid) + ',' + procName + '] was killed by force!!')
		except Exception, err:
			pass
	
	try :
		lock.acquire()
		if PS_PID.has_key(mid) : del PS_PID[mid]
		lock.release()
	except Exception, err :
		__LOG__.Trace(err)

	__LOG__.Trace("[killProc]["+str(mid)+":"+procName+":"+str(pid)+"] killed")


def showItem(prnOut,prnUnit) :
	global PS_ORDER
	global GROUP_PS
	global PS_GROUP
	global PS_PROCNAME
	global PS_DESC
	global PS_PID
	global PS_MODE

	mids = []
	if prnUnit == 'all' :
		mids = PS_ORDER.keys()
		mids.sort()
	else :
		if GROUP_PS.has_key(prnUnit) :
			mids = GROUP_PS[prnUnit].split(',')
			mids.sort
		else :
			prnOut.send("<error>\n")
			prnOut.send(str(prnUnit) + "not exist in group members\n")
			prnOut.send("<end>\n")
			return
	

	prnOut.send("-------------------------------------------------------------------------------------------------------------\n")
	prnOut.send("  ABN   MID    NAME             DESC             GROUP       MODE    PID    CMD    STA         TIME      \n")
	prnOut.send("-------------------------------------------------------------------------------------------------------------\n")
	prnOut.send("<begin>\n")

	abn = ''

	for mid in mids :
		if PS_PID.has_key(mid) and PS_ORDER[mid] == 'ACT' :
			abn = 'OK'
		else :
			abn = '***'

		procName = "***************"
		if PS_PROCNAME.has_key(mid) : procName = PS_PROCNAME[mid]
		desc = ''
		if PS_DESC.has_key(mid) : desc = PS_DESC[mid]
		groupName = '***'
		if PS_GROUP.has_key(mid) : groupName = PS_GROUP[mid]
		pid = '***'
		if PS_PID.has_key(mid) : pid = PS_PID[mid]
		cmd = '***'
		if PS_ORDER.has_key(mid) : cmd = PS_ORDER[mid]

		sts = ''

		if pid != '***' and pid != 'CRTD' :
			try	:
				os.kill(int(pid),0) 
				sts = 'ACT'
			except :
				sts = 'TERM'
		elif pid == 'CRTD':
			sts = '***'

		if cmd == 'TERM' and OLD_PID.has_key(mid) :
			oldPid = OLD_PID[mid]
			try :
				os.kill(int(oldPid),0)
				sts = 'ACT'
				pid = oldPid
			except :
				pass

		if len(sts) and sts != cmd :
			abn = 'ABN'
		
		if len(sts) == 0 :
			sts = '***'

		midTime = '***********'
		if PS_TIME.has_key(mid) : midTime = PS_TIME[mid]
		psMode = PS_MODE.get(mid,'NML')

		format = "  %3s | %04d | %-14s | %-14s | %-9s | %3s | %5s | %4s | %4s | %s"
		rMsg = format % (abn,int(mid),procName,desc,groupName,psMode,pid,cmd,sts,midTime)

		prnOut.send(rMsg+'\n')
	
	prnOut.send("<end>\n")
	return 1

def main():
	global SHUTDOWN
	global SYNC
	global PS_ORDER
	global PS_PID
	global PS_PROCNAME
	global CONF_FILE
	global PS_MODE

	thread.start_new_thread(shutdownChk,())

	global svrsock

	try :
		svrsock = socket(AF_INET, SOCK_STREAM)
		svrsock.settimeout(1.0)
		svrsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		svrsock.bind(('', SERVER_PORT))
		svrsock.listen(MAX_CLIENT_CONN)
	except Exception, err :
		__LOG__.Trace('[MAIN] : cannot bind server socket' )
		__LOG__.Exception(err)
		sys.exit()
		

	#thread.start_new_thread(thReloadConf,(confFile,))

	loadConf()

	#cleanUp()

	for mid in PS_EXECMD.keys() :
		if ( os.path.exists(MDIR+'/'+str(mid)+'.ACT') ) :
			if (  PS_MODE.get(mid,'NML') == 'POP' ) :
				PS_ORDER[mid] = 'TERM'
			else :
				PS_ORDER[mid] = 'ACT'
		else :
			PS_ORDER[mid] = 'TERM'
		PS_TIME[mid] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())

	for i in range(0,MAX_CLIENT_CONN) :
		thread.start_new_thread(thCliSocket,(svrsock,i))	
		__LOG__.Trace("[MAIN] thSockClient run.. " + str(i))
		time.sleep(0.1)

	while 1 :
		if SHUTDOWN :
			__LOG__.Trace("[MAIN] TERM signal received!!")
			break

		for mid in PS_ORDER.keys() :
			if PS_PID.has_key(mid) == False and PS_ORDER[mid] == 'ACT' :
				if  OLD_PID.has_key(mid) == True :
					# try run up this process but already alive
					pid = OLD_PID[mid]
					try :
						os.kill(int(pid),0)
						lock.acquire()
						PS_PID[mid] = pid
						lock.release()
						continue
					except :
						pass

				lock.acquire()
				PS_PID[mid] = 'CRTD'
				lock.release()
				thread.start_new_thread(thChldUp,(mid,))
				__LOG__.Trace("[MAIN][" + str(mid) + "," + PS_PROCNAME[mid] + "] thread run..")

		time.sleep(0.1)

	__LOG__.Trace("[MAIN] catch TERM signal going to kill all proces..")

	for mid in PS_ORDER.keys() :
		__LOG__.Trace("[MAIN] try kill " + str(mid) + "," + PS_PROCNAME[mid] )
		lock.acquire()
		PS_ORDER[mid] = 'TERM'
		lock.release()
		killProc(mid)
	
	__LOG__.Trace("[MAIN] Complete kill all process..")

	try :
		svrsock.close()
	except : pass


if __name__ == "__main__":
	if ( len(sys.argv) < 2 ):
		print "%s, version %s" % (sys.argv[0], VERSION)
		print 'usage : %s confFile [port]' % sys.argv[0]
		sys.exit()

	if len(sys.argv) > 2:
		SERVER_PORT = int(sys.argv[2])
		MDIR = MDIR + "_" + str(SERVER_PORT)
	
	if os.path.exists(MDIR) == False:
		try :
			os.mkdir(MDIR)
		except Exception, err :
			__LOG__.Exception(err)
			sys.exit()

	CONF_FILE = sys.argv[1]

	if os.path.exists(CONF_FILE) == False :
		print 'Error : %s not exists' % CONF_FILE
		sys.exit()

	conf = ConfigParser.ConfigParser()
	conf.read(CONF_FILE)

	if conf.has_section("CONF") and conf.has_option("CONF", "LOGFILE"):
		fileName = conf.get("CONF", "LOGFILE")
		Log.Init( Log.CRotatingLog( fileName, 10000000, 3 ))
	else:
		Log.Init(Log.CStandardErrorLog());

	try : main()
	except : __LOG__.Exception()
