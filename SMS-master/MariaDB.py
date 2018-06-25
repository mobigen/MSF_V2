#!/usr/bin/env python
#-*- coding:utf-8 -*-

import Mobigen.Common.Log as Log
import sys
import MySQLdb

class MariaDB :
	def __init__(self, Parser) :

		self.mHost  = Parser.get('MARIADB', 'HOST')
		self.mUser  = Parser.get('MARIADB', 'USER')
		self.mPass  = Parser.get('MARIADB', 'PASS')
		self.mDatabase = Parser.get('MARIADB', 'DATABASE')
		self.mPort  = Parser.get('MARIADB', 'PORT')
		self.connectMysql()

	def __del__(self) :
		self.disconnectMysql()

	def connectMysql(self) :
		self.mysqlConn = MySQLdb.connect(self.mHost, self.mUser, self.mPass, self.mDatabase, int(self.mPort))
		self.mysqlConn.set_character_set('UTF8')
		self.mysqlCurs = self.mysqlConn.cursor()

	def disconnectMysql(self) :
		if self.mysqlCurs != None :
			try :
				self.mysqlCurs.close()
			except :
				pass

		if self.mysqlConn != None :
			try :
				self.mysqlConn.close()
			except :
				pass

		__LOG__.Trace('DB Disconnect!!')

	def executeGetData(self, sql, retry=0) :
		data = None

		try :

			__LOG__.Trace(sql)
			self.mysqlCurs.execute(sql)
			data = self.mysqlCurs.fetchall()

			return data
		except :
			retry += 1
			__LOG__.Exception()
			excInfo = str(sys.exc_info()[0])
			__LOG__.Trace(sys.exc_info())
			if excInfo.find('OperationalError') > 0 :
				#대기시간 초과로 인한 접속 끊김임으로 재접속 실행
				self.connectMysql()
				if retry < 3 :
					data = self.executeGetData(sql,retry)

		return data

	def executeQuery(self, sql, retry=0) :
		try :
			self.mysqlCurs.execute(sql)
			self.mysqlConn.commit()
			return True
		except :
			retry += 1
			__LOG__.Exception()
			__LOG__.Trace(sys.exc_info())
			excInfo = str(sys.exc_info()[0])
			if excInfo.find('OperationalError') > 0 :
				#대기시간 초과로 인한 접속 끊김임으로 재접속 실행
				self.connectMysql()
				if retry < 3 :
					return self.executeQuery(sql,retry)
				else : return False
			else :
				__LOG__.Trace("EXECUTE ERROR SQL : %s.." % sql)
				self.mysqlConn.rollback()
			return False

