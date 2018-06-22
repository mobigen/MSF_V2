#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import glob
import ConfigParser
import MySQLdb
from DBMgr import DBMgr
import Mobigen.Common.Log as Log

class MysqlMgr(DBMgr) :
	DEFAULT_PORT = 3306

	def __init__(self, dbConf, dir) :
		DBMgr.__init__(self, dbConf, dir)

		self.LOADER		= self.DB_CONF["DBMS"]["MYSQL_LOADER"]
		self.LOG_FILE	= self.DB_CONF["DBMS"]["LOG_FILE"]	

	def load(self) :
		sTime = time.time()
		try :
			fileName = "%s/%s.csv" % (self.LOAD_DIR, self.TABLE)

			if os.path.exists(fileName) :
				try :
					cmd = "%s -h %s -u %s -p%s --fields-terminated-by=\'%s\' --local %s %s" % (self.LOADER, self.DBMS_IP, self.ID, self.PWD, self.COLSEP, self.DBMS_DB, fileName)
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
					mvFile = "%s/%s.csv" % (self.ERR_LOAD_DIR, self.TABLE)
					os.rename(fileName, mvFile)
			else :
				raise IOError("%s does not exists\n" % (fileName))
		finally :
			processingTime = time.time() - sTime
			__LOG__.Trace("%s Loading time : %0.3f\n" % (self.__class__.__name__, processingTime))

	def execute(self, sql) :
		conn = MySQLdb.connect(host=self.DBMS_IP, port=self.DBMS_PORT, user=self.ID, passwd=self.PWD, db=self.DBMS_DB, charset=self.SRC_ENC)
		cur = conn.cursor()
		cur.execute(sql)

		return (conn, cur)

	def getDefaultPort(self) :
		return self.DEFAULT_PORT

def main(dbConf) :
	mysqlMgr = MysqlMgr(dbConf)
	mysqlMgr.unload("./test.sql")

def usage() :
	sys.stderr.write("Usage: %s db_conf\n" % sys.argv[0])
	sys.exit()

if __name__ == "__main__" :
	if len(sys.argv) < 2 :
		usage()

	main(sys.argv[1])
