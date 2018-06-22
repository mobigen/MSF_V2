#!/home/eva/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import time
import ConfigParser
import cx_Oracle
from DBMgr import DBMgr
import Mobigen.Common.Log as Log

class OracleMgr(DBMgr) :
	DEFAULT_PORT = 1521

	def __init__(self, dbConf, dir) :
		DBMgr.__init__(self, dbConf, dir)

		self.ORA_URL		= "%s:%s/%s" % (self.DBMS_IP, self.DBMS_PORT, self.DBMS_DB)

		self.LOADER			= self.DB_CONF["DBMS"]["ORACLE_LOADER"]
		self.CTRL_ORACLE	= self.DB_CONF["DBMS"]["CONTROL_FILE_ORACLE"]	
		self.LOG_FILE		= self.DB_CONF["DBMS"]["LOG_FILE"]	

	def load(self) :
		sTime = time.time()
		try :
			fileName = "%s/%s.csv" % (self.LOAD_DIR, self.TABLE)

			if os.path.exists(fileName) :
				try :
					cmd = "%s userid=\"%s/%s@%s\" control=\"%s\" rows=10000 log=\"%s\" readsize=10000000 bindsize=10000000 errors=999999999 data=\"%s\"" % (self.LOADER, self.ID, self.PWD, self.ORA_URL, self.CTRL_ORACLE, self.LOG_FILE, fileName)
					print cmd
					ret = os.system(cmd)
					# 성공
					if ret == 0 :
						mvFile = "%s/%s.csv" % (self.LOAD_DONE_DIR, self.TABLE)
						os.rename(fileName, mvFile)
					# 실패
					else :
						mvFile = "%s/%s.csv" % (self.ERR_ETC_DIR, self.TABLE)
						os.rename(fileName, mvFile)

				except :
					__LOG__.Exception()

					mvFile = "%s/%s.csv" % (self.ERR_LOAD_DIR, self.TABLE)
					os.rename(fileName, mvFile)
			else :
				raise IOError("%s does not exists\n" % (fileName))

		finally :
			processingTime = time.time() - sTime
			__LOG__.Trace("%s Loading time : %0.3f\n" % (self.__class__.__name__, processingTime))

	def execute(self, sql) :
		conn = cx_Oracle.connect(self.ID, self.PWD, self.ORA_URL)
		cur = conn.cursor()
		cur.execute(sql)

		return (conn, cur)

	def getDefaultPort(self) :
		return self.DEFAULT_PORT

def main(dbConf) :
	oracleMgr = OracleMgr(dbConf)
	oracleMgr.unload("./test.sql")

def usage() :
	sys.stderr.write("Usage: %s db_conf\n" % sys.argv[0])
	sys.exit()

if __name__ == "__main__" :
	if len(sys.argv) < 2 :
		usage()

	main(sys.argv[1])
