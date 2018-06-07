#!/bin/env python
#!-*- coding:utf-8 -*-

import sys
import signal
import ConfigParser
import time
import datetime
import os

import Mobigen.Common.Log as Log
import API.M6 as M6
import MariaDB

G_SHUTDOWN = True

def Shutdown(sigNum = 0, frame = 0) :
	global G_SHUTDOWN
	__LOG__.Trace("Recv Signal (%s)" % sigNum)
	G_SHUTDOWN = False

signal.signal(signal.SIGTERM, Shutdown)  # Sig Terminate : 15
signal.signal(signal.SIGINT, Shutdown)   # Sig Inturrupt : 2
signal.signal(signal.SIGHUP, Shutdown)  # Sig HangUp : 1
signal.signal(signal.SIGPIPE, Shutdown) # Sig Broken Pipe : 13

class MakeIrisLoaderFile() :
	def __init__(self) :

		self.SECTION = sys.argv[1]

		self.GetParser()
		self.SetLog()
		self.GetConfig()

	def GetParser(self) :
		try:
			self.PARSER = ConfigParser.ConfigParser()
			if os.path.exists(sys.argv[2]): self.PARSER.read(sys.argv[2])
			else: self.PARSER = None
		except:
			print 'GetParser Error'
			self.PARSER = None

		if self.PARSER is None:
			print 'GetParser Error \n usage : %s ConfigFile' % ( sys.argv[0] )
			sys.exit()

	def SetLog(self) :

		#default Log
		self.logFilePath = 'Log'
		self.logFileSize = 1000000
		self.logFileCount = 10

		if (self.PARSER != None) :
			if self.PARSER.get('Log','LogFilePath') != '' :
				self.logFilePath = self.PARSER.get('Log','LogFilePath')

			self.logFileSize = self.PARSER.get('Log','LogFileSize')
			self.logFileCount = self.PARSER.get('Log','LogFileCount')

			if not os.path.exists(self.logFilePath) :
				os.makedirs(self.logFilePath)

			LOG_NAME = '%s/%s_%s.log' % (self.logFilePath, os.path.basename(sys.argv[0])[:-3], self.SECTION)
			Log.Init(Log.CRotatingLog(os.path.expanduser(LOG_NAME), int(self.logFileSize), int(self.logFileCount)))


	def GetConfig(self) :
		try :
			self.SAVE_PATH = self.PARSER.get(self.SECTION, 'SAVE_PATH')
			self.STARTDATE = self.PARSER.get(self.SECTION, 'STARTDATE')
			self.ENDDATE = self.PARSER.get(self.SECTION, 'ENDDATE')
			self.DELAY_SECOND = self.PARSER.getint(self.SECTION, 'DELAY_SECOND')
			self.SAVE_SEPARATE = self.PARSER.get(self.SECTION, 'SAVE_SEPARATE')
			self.GAP_SECOND = self.PARSER.getint(self.SECTION, 'GAP_SECOND')
			self.QUERY = self.PARSER.get(self.SECTION, 'QUERY')
			self.KEY_INDEX = self.PARSER.getint(self.SECTION, 'KEY_INDEX')

			try : self.SPLIT_CNT = self.PARSER.getint(self.SECTION, 'SPLIT_CNT')
			except : self.SPLIT_CNT = -1

			try : ksidx = self.PARSER.getint(self.SECTION, 'KEY_START_INDEX')
			except : ksidx = None
			try : keidx = self.PARSER.getint(self.SECTION, 'KEY_END_INDEX')
			except : keidx = None
			try : vsidx = self.PARSER.getint(self.SECTION, 'VALUE_START_INDEX')
			except : vsidx = None
			try : veidx = self.PARSER.getint(self.SECTION, 'VALUE_END_INDEX')
			except : veidx = None

			self.KEY_SLICE = slice(ksidx,keidx)
			self.VALUE_SLICE = slice(vsidx,veidx)

			__LOG__.Trace(self.KEY_SLICE)
			__LOG__.Trace(self.VALUE_SLICE)
			if not os.path.exists(self.SAVE_PATH) :
				os.makedirs(self.SAVE_PATH)

		except :
			__LOG__.Exception()
			sys.exit()

	def run(self) :

		__LOG__.Trace('Start Iris Loader File!!')

		if len(self.STARTDATE) == 0 : pd = datetime.datetime.strptime((datetime.datetime.now().strftime('%Y%m%d%H%M00')),'%Y%m%d%H%M00')
		else : pd = datetime.datetime.strptime(self.STARTDATE,'%Y%m%d%H%M%S')

		global G_SHUTDOWN

		while G_SHUTDOWN :
			try :
				spd =  pd.strftime('%Y%m%d%H%M00')

				#종료시간 확인
				if len(self.ENDDATE) != 0 and spd >= self.ENDDATE:
					__LOG__.Trace('Partition Date[spd] >= End Date[self.ENDDATE]')
					time.sleep(60)
					continue

				nd =  datetime.datetime.now()
				#파티션 Delay 확인
				if pd + datetime.timedelta(seconds=self.DELAY_SECOND) > nd :
					__LOG__.Trace('Delay Date[%s] > Now[%s]' % (pd + datetime.timedelta(seconds=self.DELAY_SECOND),nd))
					time.sleep(1)
					continue

				db = MariaDB.MariaDB(self.PARSER)

				PartitionDate = nd.strftime('%Y%m%d%H%M00')

				#파티션 / WhereDate
				sql = self.QUERY % (spd)
				data = db.executeGetData(sql)

				#Key Index[0]

				fdList = []
				for i in range(10) :
					fd = open(os.path.join(self.SAVE_PATH, '%s_%s.csv' % (i, spd)), 'w')
					fdList.append(fd)

				for row in data :
					Key = row[self.KEY_INDEX][self.KEY_SLICE]
					Partition = spd
					stemp = Partition + self.SAVE_SEPARATE + Key + self.SAVE_SEPARATE
					__LOG__.Trace(stemp)
					tempData = stemp + self.SAVE_SEPARATE.join(str(v) for v in row[self.VALUE_SLICE])
					if self.SPLIT_CNT != -1 :
						if len(tempData.split(self.SAVE_SEPARATE)) != self.SPLIT_CNT :
							__LOG__.Trace(tempData)
							tempData = self.SAVE_SEPARATE.join(v for v in tempData.split(self.SAVE_SEPARATE)[:self.SPLIT_CNT]) + ' '.join(v for v in tempData.split(self.SAVE_SEPARATE)[self.SPLIT_CNT:])
							__LOG__.Trace(tempData)

					__LOG__.Trace(tempData)
					fdList[int(Key)].write(tempData + '\n')

				for fd in fdList :
					fd.close()
					__LOG__.Trace('file://%s\n' % fd.name)
					sys.stdout.write('file://%s\n' % fd.name)
					sys.stdout.flush()
					sys.stderr.write('\n')
					sys.stderr.flush()

				pd += datetime.timedelta(seconds=self.GAP_SECOND)

			except :
				__LOG__.Exception()
				break

if __name__ == "__main__" :

	if len(sys.argv) != 3 :
		print '%s Section ConfigPath' % sys.argv[0]
		sys.exit()

	obj = MakeIrisLoaderFile()
	obj.run()

	__LOG__.Trace("PROCESS END...\n")
