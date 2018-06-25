#! /bin/env python
#coding:utf8

from threading import Thread
from Queue import Queue
from socket import error
from re import compile
from ConfigParser import *
#from os import *
import subprocess
import time
import paramiko
import sys
import signal
import Mobigen.Common.Log as Log

SHUTDOWN = False
def shutdown(sigNum, frame):
	global SHUTDOWN
	SHUTDOWN = True
	sys.stderr.write("Catch Signal :%s" % sigNum)
	sys.stderr.flush()

signal.signal(signal.SIGTERM, shutdown) # sigNum 15 : Terminate
signal.signal(signal.SIGINT, shutdown)  # sigNum  2 : Interrupt
signal.signal(signal.SIGHUP, shutdown)  # sigNum  1 : HangUp
signal.signal(signal.SIGPIPE, shutdown) # sigNum 13 : Broken Pipe


class ServerWatch(object):
	def __init__(self, ip, username, password, password2, port=22):
		self.ip =ip
		self.uname = username
		self.pw = password
		self.pw2 = password2
		self.port = int(port)
		self.client = paramiko.SSHClient()
		self.OKFlag = "OK"

	def SSHClinetConnection(self):
		client = self.client
		client.load_system_host_keys()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			client.connect(self.ip, username=self.uname, password=self.pw, port=self.port, timeout=10)
		except:
			client.connect(self.ip, username=self.uname, password=self.pw2, port=self.port, timeout=10)

	def commandDISK(self):
		stdin, stdout, stderr = self.client.exec_command('df -m')
		dlist = []
		for line in stdout:
			line = line.strip()
			dlist.append(line.split())
		
		#get total list
		rl =[]
		for idx in range(1, len(dlist)):
			if len(dlist[idx])==1:
				rl.append(dlist[idx]+dlist[idx+1])
			elif len(dlist[idx])==6:
				rl.append(dlist[idx])
		del(dlist)

		#get total, use, free, usage value
		result = []
		for i in range(len(rl)):
			total = int(rl[i][2])+int(rl[i][3])
			tmp =[]
			for j in [5,1,2,3,4]:
				if j==1:
					tmp.append(str(total)) #total = use+free
				elif j==4:
					tmp.append(str(int(rl[i][2])*100/total)) #usage percent = use / total
				else:
					tmp.append(rl[i][j])
			result.append({'STATUS':'OK','VALUE':tmp})
			del(tmp)
		del(rl)
		return result

	def commandSWAP(self):
		stdin, stdout, stderr = self.client.exec_command('free -m')
		slist =[]
		for line in stdout:
			line = line.strip()
			slist.append(line.split())
		result =[]
		used = int(slist[3][2])
		free = int(slist[3][3])
		total = used + free
		result.append(str(total))
		result.append(str(used))
		result.append(str(free))
		result.append(str(used*100/total))
		retdic={'STATUS':'OK','VALUE':result}
		return retdic

	def commandLOAD_AVG(self):
		result=[]
		stdin, stdout, stderr = self.client.exec_command('uptime')
		patt = compile(r"[0-9]?\.[0-9]{2}")
		for line in stdout:
			loadavg = patt.findall(line)
		result.append(loadavg[0])
		result.append(loadavg[1])
		result.append(loadavg[2])
		retdic={'STATUS':'OK','VALUE':result}
		return retdic
	
	def commandMEMORY(self):
		stdin, stdout, stderr = self.client.exec_command('free -m')
		flist =[]
		
		for line in stdout:
			line = line.strip()
			flist.append(line.split())

		#total = used + free + buffers + cached
		total = int(flist[1][2])+int(flist[1][3])+int(flist[1][5])+int(flist[1][6])
		#real free memory = free + buffers + cached
		free_memory = int(flist[1][3])+int(flist[1][5])+int(flist[1][6])
		#real use memory = total - (free + buffers + cached)
		use_memory = total - free_memory
		#real usage percent = (use_memory+free_memory)/use_memory
		usage_percent = use_memory*100 / total

		result =[]
		result.append(str(total))
		result.append(str(use_memory))
		result.append(str(free_memory))
		result.append(str(usage_percent)[:2])
		retdic={'STATUS':'OK','VALUE':result}
		return retdic

	def commandHOSTNAME(self):
		hlist=[]
		stdin, stdout, stderr = self.client.exec_command('cat /proc/sys/kernel/hostname')
		for line in stdout:
			line = line.strip()
			hlist.append(line)
		retdic={'VALUE':hlist}
		return retdic

	def run(self):
		infodic=dict()
		try:
			self.SSHClinetConnection()
			infodic['HOSTNAME']=self.commandHOSTNAME()
			infodic['STATUS']=self.OKFlag
			infodic['LOAD_AVG']=self.commandLOAD_AVG()
			infodic['DISK']=self.commandDISK()
			infodic['MEMORY']=self.commandMEMORY()
			infodic['SWAP']=self.commandSWAP()
			self.client.close()
			return infodic

		#password나 useraname이 잘못되었을 경우
		except paramiko.AuthenticationException as e:
			self.OKFlag = "NOK"
			infodic['STATUS']=self.OKFlag
			shell = "cat /etc/hosts | awk '{if(/"+self.ip+"/){print $2}}'"
			p = subprocess.Popen(shell,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			hostname = p.stdout.readline()
			hostname = hostname.strip()
			infodic['HOSTNAME']={'VALUE': [hostname]}
			self.client.close()
			__LOG__.Exception()
			return infodic
		#port 나 ip가 잘못되었을 경우
		except error as e:
			self.OKFlag = "NOK"
			infodic['STATUS']=self.OKFlag
			shell = "cat /etc/hosts | awk '{if(/"+self.ip+"/){print $2}}'"
			p = subprocess.Popen(shell,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			hostname = p.stdout.readline()
			hostname = hostname.strip()
			infodic['HOSTNAME']={'VALUE': [hostname]}
			self.client.close()
			__LOG__.Exception()
			return infodic
		#SSH접속 자체가 안될 경우
		except paramiko.SSHException as e:
			self.OKFlag = "NOK"
			infodic['STATUS']=self.OKFlag
			shell = "cat /etc/hosts | awk '{if(/"+self.ip+"/){print $2}}'"
			p = subprocess.Popen(shell,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			hostname = p.stdout.readline()
			hostname = hostname.strip()
			infodic['HOSTNAME']={'VALUE': [hostname]}
			self.client.close()
			__LOG__.Exception()
			return infodic

class JobProcess(object):
	def __init__(self, svrobjlist):
		self.data_q = Queue([])
		self.THREADPOOL = 10
		self.total = dict()
		self.putdata(svrobjlist)
		
	def job_process(self,th_id):
		while not SHUTDOWN:
			try:
				ip,obj = self.data_q.get_nowait()
				__LOG__.Trace('thread get : %s ' % th_id)
			except:
				__LOG__.Trace("thread %s is done" % th_id)
				break
			self.total[ip] = obj.run()
			time.sleep(0.1)

	def putdata(self, svrobjlist):
		for ip,svrobj in svrobjlist:
			self.data_q.put((ip,svrobj))

	def makeThreadlist(self):
		th_list = list()
		for i in range(self.THREADPOOL):
			th_obj = Thread(target=self.job_process, args=[i])
			th_list.append(th_obj)
		return th_list

	def run(self):
		th_list = self.makeThreadlist()
		for th_obj in th_list:
			th_obj.start()
		for th_obj in th_list:
			th_obj.join()
		__LOG__.Trace("[Collect]SERVER RESOURCE END_______________________")
		return self.total

class ServerResource(object):
	def __init__(self, getconfigparser):
		self.config = getconfigparser
	
	def getConfParser(self):
		conflist = list()
		conf_dict = dict()
		type_list = ['SSH_PORT','USER','PASSWD','PASSWD2']

		for rsc_ip in self.config.get('RESOURCES','SERVER_LIST').split(','):
			conf_dict['IP'] =rsc_ip
			for type in type_list:
				try:
					conf_dict[type] = self.config.get(rsc_ip,type)
				except:
					conf_dict[type] = self.config.get('RESOURCES',type)

					
			conflist.append((conf_dict['IP'], conf_dict['SSH_PORT'], conf_dict['USER'], conf_dict['PASSWD'], conf_dict['PASSWD2']))
		__LOG__.Trace(conflist)
		return conflist
	
	def run(self):	
		svrlist =[]
		__LOG__.Trace("[Collect]SERVER RESOURCE START_____________________")
		infolist = self.getConfParser()
		for tup in infolist:
			svr_obj = ServerWatch(tup[0],tup[2],tup[3],tup[4],tup[1])
			svrlist.append((tup[0],svr_obj))
		__LOG__.Trace(svrlist)
		jp_obj = JobProcess(svrlist)
		return jp_obj.run()
