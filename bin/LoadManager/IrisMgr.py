#!/home/e2es/bin/python
# -*- coding: utf-8 -*-

import sys
import os, glob, re
import time
import threading
import API.M6 as M6
from DBMgr import DBMgr
import Mobigen.Common.Log as Log; Log.Init()

class LoadThread(threading.Thread):
	def __init__(self, irisMgr, csvFile, ctlFile):
		threading.Thread.__init__(self)

		self.IRIS_MGR	= irisMgr
		self.CSV_FILE 	= csvFile
		self.CTL_FILE 	= ctlFile


	def run(self):
		conn = M6.Connection(self.IRIS_MGR.IRIS_HOST, self.IRIS_MGR.ID, self.IRIS_MGR.PWD)
		cur = conn.cursor()
		cur.SetFieldSep(self.IRIS_MGR.COLSEP)
		cur.SetRecordSep(self.IRIS_MGR.ROWSEP)

		csvFile = self.CSV_FILE.split('/')[-1]

		try:
			fileName = csvFile.rsplit('.', 1)[0]
			m = re.search("(\w+)_(\w+)_(\w+)", fileName)

			table = m.group(1)
			pat = m.group(2)
			key = m.group(3)

			print "(%s)(%s)(%s)(%s)\n" % (table, pat, key, self.CSV_FILE)

			retMessage = cur.Load(table, key, pat, self.CTL_FILE, self.CSV_FILE)
			if "+OK SUCCESS" in retMessage.strip():
				mvFile = "%s/%s" % (self.IRIS_MGR.LOAD_DONE_DIR, csvFile)
				os.rename(self.CSV_FILE, mvFile)
			else:
				__LOG__.Trace("%s" % retMessage.strip())
				mvFile = "%s/%s" % (self.IRIS_MGR.ERR_ETC_DIR, csvFile)
				os.rename(self.CSV_FILE, mvFile)

		except Exception, err:
			__LOG__.Exception()
			mvFile = "%s/%s" % (self.IRIS_MGR.ERR_LOAD_DIR, csvFile)
			os.rename(self.CSV_FILE, mvFile)

		finally:
			if cur != None:
				cur.Close()
			if conn != None:
				conn.close()

			self.IRIS_MGR.FILE_COUNT += 1

			'''
			if self.IRIS_MGR.FILE_COUNT == self.IRIS_MGR.MAX_FILE_COUNT :
				os.remove(self.CTL_FILE)
			'''

			# increments the counter
			self.IRIS_MGR.LOAD_SEMA.release()
			__LOG__.Trace("LOAD_SEMA.release()")


class IrisMgr(DBMgr):
	DEFAULT_PORT = 5050

	def __init__(self, dbConf, dir):
		DBMgr.__init__(self, dbConf, dir)

		self.IRIS_HOST 	= "%s:%s" % (self.DBMS_IP, self.DBMS_PORT)
		self.COLUMN		= self.DB_CONF["IRIS"]["COLUMN"]

		threadCount = 1
		try:
			threadCount	= int(self.DB_CONF["IRIS"]["LOAD_THREAD_COUNT"])
		except:
			__LOG__.Exception()

		self.LOAD_SEMA 	= threading.BoundedSemaphore(threadCount)


	def makeCtlFile(self):
		fp = None
		ctlFile = None
		try:
			ctlFile = "%s.ctl" % (self.TABLE)
			fp = open(ctlFile, "w")

			columns = self.COLUMN.split(",")
			for oneColumn in columns:
				oneColumn = oneColumn.strip()
				fp.write("%s%s" % (oneColumn, self.ROWSEP))

		finally:
			if fp != None:
				fp.close()

		return fp.name

	def load(self):
		conn = None
		cur = None

		ctlFile = self.makeCtlFile()

		sTime = time.time()

		fileList = glob.glob("%s/%s*.csv" % (self.LOAD_DIR, self.TABLE))
		fileList.sort()

		self.MAX_FILE_COUNT = len(fileList)
		self.FILE_COUNT = 0

		for oneFile in fileList:
			# decrements the counter
			self.LOAD_SEMA.acquire()
			__LOG__.Trace("LOAD_SEMA.acquire()")

			loadThread = LoadThread(self, oneFile, ctlFile)
			loadThread.start()

		processingTime = time.time() - sTime

		__LOG__.Trace("%s Loading time : %0.3f\n" % (self.__class__.__name__, processingTime))

		#os.remove(ctlFile)

	def execute(self, sql):
		conn = M6.Connection(self.IRIS_HOST, self.ID, self.PWD)
		cur = conn.cursor()
		cur.SetFieldSep(self.COLSEP)
		cur.SetRecordSep(self.ROWSEP)

		cur.Execute(sql)

		return (conn, cur)

	def isSplit(self):
		return True

	def getDefaultPort(self):
		return self.DEFAULT_PORT

def main(dbConf):
	irisMgr = IrisMgr(dbConf)
	#irisMgr.load()
	irisMgr.unload("./test.sql")

def usage():
	sys.stderr.write("Usage: %s	db_conf\n" % sys.argv[0])
	sys.exit()

if __name__ == "__main__":
	if len(sys.argv) < 2:
		usage()

	main(sys.argv[1])
	'''
	try :
		main(sys.argv[1])
	except Exception, err :
		sys.stderr.write('ERROR: %s\n' % str(err))
	'''
