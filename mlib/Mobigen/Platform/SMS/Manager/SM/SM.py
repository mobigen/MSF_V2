# coding: utf-8

import time, re
import threading
import Socket as Socket
import Mobigen.Common.Log as Log ; Log.Init()

class SM (threading.Thread):
	def __init__(self, ip, port, nodeId) :
		threading.Thread.__init__(self) 
		self.ip = ip
		self.agent_port = port
		self.sock = None
		self.nodeId = nodeId

		#PR      2008-04-22 17:40:00
		self.start_p = re.compile("\S+\s+(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})")

		self.hashParse = {}
		self.hashParse['CPUPerf']    = self.CPUPerf
		self.hashParse['DiskPerf']   = self.DiskPerf
		self.hashParse['MemoryPerf'] = self.MemoryPerf

		self.curInfo = {}
		self.curInfo['TIME'] = "00000000000000"

	def run(self) :
		self.Proc()

	def dbUpdate(self, sql):
		'''
		SYS_NODE_INFO = "%s/SYS_NODE_INFO.DAT" % Default.M6_MASTER_DATA_DIR

		try:
			backend = Backend([SYS_NODE_INFO])
			conn = backend.GetConnection()
			cursor = conn.cursor()

			cursor.execute(sql)

			conn.commit()

			cursor.close()

			backend.Disconnect()
			backend = None
		except:
			pass
		'''

	def NodeStatusSet(self, status) :
		sql = """UPDATE SYS_NODE_INFO SET 
			SYS_STATUS = '%s'
			WHERE NODE_ID = %s
		""" % ( status, self.nodeId)
		__LOG__.Watch(sql)

		self.dbUpdate( sql )


	def Update(self) :
		__LOG__.WatchEx(self.curInfo)


		sql = """UPDATE SYS_NODE_INFO SET 
			UPDATE_TIME = '%s',
			CPU_USAGE = %.2f,
			DISK_USAGE = %.2f,
			MEM_USAGE = %.2f
			WHERE NODE_ID = %s
		""" % ( self.curInfo['TIME'], \
				self.curInfo["CPU"], 
				self.curInfo["DISK"], 
				self.curInfo["MEM"], 
				self.nodeId)
		__LOG__.Watch(sql)
		self.dbUpdate( sql )

		sql = """UPDATE SYS_NODE_INFO SET 
			SYS_STATUS = 'VALID'
			WHERE NODE_ID = %s AND SYS_STATUS in ('VALID', 'READY')
		""" % ( self.nodeId)
		__LOG__.Watch(sql)
		self.dbUpdate( sql )

		strTime = self.curInfo['TIME']
		self.curInfo = {}
		self.curInfo['TIME'] =strTime

	def Proc(self) :

		retryCount = 1
		while True :
			try :
				self.AgentConnect()
				retryCount = 1
				self.DataProc()

			except self.sock.SocketTimeoutException:
				self.NodeStatusSet("INVALID")

			except :
				__LOG__.Exception()
				retryCount = retryCount + 1

			if(retryCount%5==0):
				self.NodeStatusSet("INVALID")

			time.sleep(30)

	def AgentConnect(self) :
		self.sock = Socket.Socket()
		self.sock.Connect(self.ip, self.agent_port)

		msg = self.sock.Readline(False, 5) # WELCOME
		if (msg[0] != '+') : raise Exception, "Welcome Error !!!"

		self.sock.SendMessage("USER admin\r\n")
		msg = self.sock.Readline(False, 5) 
		if (msg[0] != '+') : raise Exception, "Auth Error !!!"

		self.sock.SendMessage("PASS admin.\r\n")
		msg = self.sock.Readline(False, 5) 
		if (msg[0] != '+') : raise Exception, "Password Error !!!"
		__LOG__.Trace( "AgentConnect... ok" );
	
	def DataProc(self) :
		start_p = self.start_p
		
		isStart = False
		msg_list = []

		insert_time = time.time()
		while True :
			msg = self.sock.Readline(False, 600)
			msg = msg.strip()
			if len(msg) == 0 :
				if time.time() > insert_time + 600:
					# scagent가 다시 살리는 시간이 1분
					raise self.sock.SocketTimeoutException, "10 min timeout.."
				continue

			m = start_p.match( msg ) 
			if not isStart and m: 
				strTime = "".join(m.groups())
				strTime = strTime[:-1] + '0'
				if( strTime != self.curInfo['TIME'] )  : self.curInfo = {}
				self.curInfo['TIME'] = strTime
				isStart = True

			if isStart: msg_list.append( msg )

			if isStart and msg == "COMPLETED": 
				isStart = False
				self.Parse( msg_list )
				msg_list = []

			if len(self.curInfo) == 4 :
				insert_time = time.time()
				self.Update()
			

	def Parse(self, msgList) : 
		(type, desc) = re.split("\s", msgList[1], 1)
		__LOG__.Trace( "Parse...[%s]" % type )
		if not self.hashParse.has_key(type)  : return
		self.hashParse[type](msgList)
		
	def CPUPerf(self, msgList) :
		#__LOG__.Watch( msgList )
		for line in msgList :
			if line[:5]!="total" : continue
			#list = re.split("0x1e", line)
			#__LOG__.Watch(  line )
			list = line.split()
			self.curInfo['CPU'] = float(list[1])

	def MemoryPerf(self, msgList) :
		#__LOG__.Watch(  msgList )
		list = msgList[4].split()
		self.curInfo["MEM"] = float(list[2])

	def DiskPerf(self, msgList) :
		partitionTotalSizeList = []
		partitionUsedSizeList = []
		for line in msgList: 
			list = line.split()
			if len(list) < 3: continue
			'''
			확인 필요...
			SM_DATA_MOUNT = {0:"/data"}
			if list[0] in SM_DATA_MOUNT[self.nodeId]: 
				partitionTotalSizeList.append( float(list[1]) )
				partitionUsedSizeList.append( float(list[2]) )
			'''
		try: avgUsage = sum(partitionUsedSizeList) / float(sum(partitionTotalSizeList)) * 100
		except: avgUsage = 0.0
		self.curInfo["DISK"] = avgUsage

import unittest

class TestSM(unittest.TestCase):

	def setUp(self):
		self.disk = """PR      2008-04-22 17:40:00
DiskPerf        Disk Performance Monitoring!!
ACTIVE
Instance        TOTAL_SIZE(KB)  USED_SIZE(KB)   USAGE(%)
/       20315844        3486052 18.09
/proc   0       0       0.00
/sys    0       0       0.00
/dev/pts        0       0       0.00
/DATA   473086160       349844  0.08
/boot   497829  29486   6.25
/dev/shm        4155196 0       0.00
/home   403508896       3832092 1.00
/tmp    16253924        177168  1.15
/var    16253956        441308  2.86
/var/lib/nfs/rpc_pipefs 0       0       0.00
COMPLETED
""".split("\n")

		self.memory = """PR      2008-04-22 17:40:00
MemoryPerf      Memory Performance Monitoring!!
ACTIVE
TotalPhysicalMemory(KB) FreePhysicalMemory(KB)  PhysicalMemoryUsage(%)  TotalSwapMemory(KB)     FreeSwapMemory(KB)      SwapMemoryUsage(%)  PageScan(Count) PageOut(Count)  SwapOut(Count)
8310392 8004220 3.68    16779852        16779852        0.00    0       0       0
COMPLETED
""".split("\n")

		self.cpu = """PR      2008-04-22 17:40:00
CPUPerf CPU Performance Monitoring!!
ACTIVE
INSTANCE        USER(%) KERNEL(%)       CPU(%)  WAIT(%) IDLE(%)
cpu0    1.00    0.00    0.00    0.00    100.00
cpu1    2.00    0.00    0.00    0.00    100.00
cpu2    3.00    0.00    0.00    0.00    100.00
cpu3    4.00    0.00    0.00    0.00    100.00
total   5.00    0.00    0.00    0.00    100.00
COMPLETED
""".split("\n")

	def test_Parse(self):
		th = SM(None, None)

		th.CPUPerf(self.cpu)
		th.MemoryPerf(self.memory)
		th.DiskPerf(self.disk)

		self.assertEqual( th.curInfo["CPU"],  5.0  )
		self.assertEqual( th.curInfo["DISK"], 0.08 )
		self.assertEqual( th.curInfo["MEM"],  3.68 )

		# 5.0 0.08 3.68
		#print ""
		#print th.curInfo["CPU"], th.curInfo["DISK"], th.curInfo["MEM"]

if __name__ == "__main__" :

	unittest.main()

