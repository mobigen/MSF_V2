# -*- coding: utf-8 -*-
#!/bin/env python

import datetime
import re
import signal
import sys
import getopt
import time

import Mobigen.Common.Log as Log

from Noti.IrisData import *
from Noti.ServerData import *

import mysql.connector

SHUTDOWN = True
def shutdown(sigNum, frame):
	SHUTDOWN = False
	sys.stderr.write("Catch Signal : %s" % sigNum)
	sys.stderr.flush()

signal.signal(signal.SIGTERM,shutdown) # sigNum 15 : Terminate
signal.signal(signal.SIGINT, shutdown)  # sigNum  2 : Interrupt
signal.signal(signal.SIGHUP, shutdown)  # sigNum  1 : HangUp
signal.signal(signal.SIGPIPE,shutdown) # sigNum 13 : Broken Pipe

class NotiDB(object) :
	def __init__(self, conf_parser, dict_obj, collect_name):
		self.config = conf_parser
		self.raw_dict = dict_obj
		self.collect_name = collect_name
	
	def get_db_config(self) :
		try :
			config_db_ip = self.config.get('DB','DB_IP')
			config_db_id = self.config.get('DB','DB_ID')
			config_db_pwd = self.config.get('DB','DB_PWD')
			config_db_name = self.config.get('DB','DB_NAME')
			
			try : config_db_port = self.config.getint('DB','DB_PORT')
			except : config_db_port = 3306

			return (config_db_ip, config_db_id, config_db_pwd, config_db_name, config_db_port)
		except :
			__LOG__.Exception()

	def run(self):

		iris_list = list()
		server_list = list()

		try:
			#ip를 key 기준으로 나눈다.
			for ip in sorted(self.raw_dict.keys()) :
				if self.raw_dict[ip]['STATUS']=='NOK' :
					__LOG__.Trace("Connection NOK :: ip = %s " % ip)
					continue
				if 'IRIS' in self.raw_dict[ip].keys() :
					iris_list.append(ip)
				if 'DISK' in self.raw_dict[ip].keys()  :
					server_list.append(ip)

			
			db_flag = True
			sqls = []
			create_sqls = []
			table_objs = GetTableName(self.config, self.collect_name)  #get tuple : (table_name, table_contents)
				
			
			if len(iris_list) > 0 :
				Iris = IrisData(self.raw_dict, self.config, iris_list)
				mergelist = Iris.get_iris_data()
				create_sqls.append(table_objs.create_iris_status())

				for iris_sts in mergelist :
					__LOG__.Trace(iris_sts, mergelist)
					table_name, table_content = table_objs.insert_iris_status()
					sqls.append(table_content + "'" + "', '".join(iris_sts) + "')")
				__LOG__.Trace("[Noti]IRIS END__________________")
			
			if len(server_list) > 0 : 
				Server = ServerData(self.raw_dict, self.config, server_list)
				cpulist, memlist, swaplist, disklist = Server.get_server_data()
				
				create_sqls.append(table_objs.create_server_resource())
				create_sqls.append(table_objs.create_disk_resource())

				for ip in sorted(cpulist) :
					table_name, table_content = table_objs.insert_server_resource()
					sqls.append(table_content + "'" + "', '".join(cpulist[ip]) + "', '" + "', '".join(memlist[ip][2:]) + "', '" + "', '".join(swaplist[ip][2:]) + "')")
				
				for ip in sorted(disklist) :
					for disksts in disklist[ip] :
						table_name, table_content = table_objs.insert_server_disk_resource()
						sqls.append(table_content + "'" + "', '".join(disksts) + "')")
					
				for sql in sqls :
					__LOG__.Trace(sql)
					
				__LOG__.Trace("[Noti]SERVERRESOURCE END_________________")

			db_ip, db_id, db_pwd, db_name, db_port = self.get_db_config()
			
			
			try :
				conn = mysql.connector.connect(host=db_ip, user=db_id, password=db_pwd, database=db_name, port=db_port)
			except :
					__LOG__.Exception()

			if conn.is_connected() : 
				try :
					cursor = conn.cursor()
				except :
					__LOG__.Exception()
					return 
	
				#show tables
				for cre_sql in create_sqls : 
					try :
						table_name, table_content = cre_sql
						table_stat = 'SHOW TABLES LIKE "%s"' % table_name
						cursor.execute(table_stat)
						result = cursor.fetchone()
						if not result : #there are no tables
							cursor.execute(table_content)	
							__LOG__.Trace("TABLE CREATE %s" % table_name)
					except :
						__LOG__.Exception()	
						return
				#insert sql
				for sql in sqls :
					__LOG__.Trace(sql)
					try :
						cursor.execute(sql)
					except :
						__LOG__.Exception()
						return
				try :
					conn.commit()
					__LOG__.Trace('Commit MariaDB Complete...')
				except :
					__LOG__.Exception()
					return

				try :
					cursor.close()
				except :
					__LOG__.Exception()
			else :
				__LOG__.Trace('Connect Fail Maria DB...')

			try :
				conn.close()
			except :
				__LOG__.Exception()
		
		except:
			__LOG__.Exception()

class GetTableName(object) :
	def __init__(self, conf_parser, table_name) :
		self.config = conf_parser
		self.table_name = table_name
		if self.get_dbname_config()==False :
			__LOG__.Trace("You must write the table name in config file!!!!!!!!!!!!!!!!!")
			raise Exception()

	def get_dbname_config(self) :
		if 'ServerResource' in self.table_name : 
			try : self.table_disk_resource_name = self.config.get('DB','TABLENAME_DISK_RESOURCE')
			except : return False
				#self.table_disk_resource_name = 'tb_disk_resource_%s' % time.strftime('%y_%m_%d_%I_%M')
			
			try : self.table_server_resource_name = self.config.get('DB','TABLENAME_SERVER_RESOURCE')
			except : return False
				#self.table_server_resource_name = 'tb_server_resource_%s' % time.strftime('%y_%m_%d_%I_%M')	
		if 'IrisStatus' in self.table_name :
			try : self.table_iris_status_name = self.config.get('DB','TABLENAME_IRIS_STATUS')
			except : return False
			#self.table_iris_status_name = 'tb_iris_status_%s' % time.strftime('%y_%m_%d_%I_%M')
		
	def	create_disk_resource(self) :
		SQL_CRE_SERVER_DISK_RESOURCE = """
		CREATE TABLE %s (
			INS_TIME DATETIME NOT NULL,
			IPADDR VARCHAR(16) NOT NULL,
			HOSTNAME VARCHAR(64) NULL DEFAULT NULL,
			MOUNT_ON VARCHAR(32) NOT NULL,
			MBLOCKS VARCHAR(8) NULL DEFAULT NULL,
			DISK_USED VARCHAR(8) NULL DEFAULT NULL,
			DISK_AVAILABLE VARCHAR(16) NULL DEFAULT NULL,
			DISK_USAGE VARCHAR(16) NULL DEFAULT NULL,
			PRIMARY KEY (INS_TIME, IPADDR, MOUNT_ON)
		)
		COLLATE=utf8_general_ci
		ENGINE=InnoDB;
		""" % self.table_disk_resource_name
		return self.table_disk_resource_name, SQL_CRE_SERVER_DISK_RESOURCE
		
	def create_server_resource(self) :
		SQL_CRE_SERVER_RESOURCE = """
		CREATE TABLE %s (
			INS_TIME DATETIME NOT NULL,
			IPADDR VARCHAR(16) NOT NULL,
			HOSTNAME VARCHAR(64) NULL DEFAULT NULL,
			CPULOADAVG_1M VARCHAR(8) NULL DEFAULT NULL,
			CPULOADAVG_5M VARCHAR(8) NULL DEFAULT NULL,
			CPULOADAVG_15M VARCHAR(8) NULL DEFAULT NULL,
			MEM_TOTAL VARCHAR(16) NULL DEFAULT NULL,
			MEM_USED VARCHAR(16) NULL DEFAULT NULL,
			MEM_AVAILABLE VARCHAR(16) NULL DEFAULT NULL,
			MEM_USAGE VARCHAR(16) NULL DEFAULT NULL,
			SWAP_TOTAL VARCHAR(16) NULL DEFAULT NULL,
			SWAP_USED VARCHAR(16) NULL DEFAULT NULL,
			SWAP_AVAILABLE VARCHAR(16) NULL DEFAULT NULL,
			SWAP_USAGE VARCHAR(16) NULL DEFAULT NULL,
			PRIMARY KEY (INS_TIME, IPADDR)
		)
		COLLATE=utf8_general_ci
		ENGINE=InnoDB;
		"""	 % self.table_server_resource_name
		return self.table_server_resource_name, SQL_CRE_SERVER_RESOURCE

	def create_iris_status(self) :
		SQL_CRE_IRIS_STATUS = """
		CREATE TABLE %s (
			INS_TIME DATETIME NOT NULL,
			IPADDR VARCHAR(16) NOT NULL,
			HOSTNAME VARCHAR(64) NULL DEFAULT NULL,
			NODE_ID VARCHAR(16) NOT NULL,
			SYS_STATUS VARCHAR(16) NULL DEFAULT NULL,
			ADM_STATUS VARCHAR(16) NULL DEFAULT NULL,
			UPDATE_TIME VARCHAR(16) NULL DEFAULT NULL,
			CPU VARCHAR(8) NULL DEFAULT NULL,
			LOADAVG VARCHAR(8) NULL DEFAULT NULL,
			MEM_P VARCHAR(8) NULL DEFAULT NULL,
			MEM_F VARCHAR(8) NULL DEFAULT NULL,
			DISK VARCHAR(8) NULL DEFAULT NULL,
			PRIMARY KEY (INS_TIME, IPADDR)
		)
		COLLATE=utf8_general_ci
		ENGINE=InnoDB;
		""" % self.table_iris_status_name
		return self.table_iris_status_name, SQL_CRE_IRIS_STATUS
		
	def insert_server_disk_resource(self) :
		SQL_INS_SERVER_DISK_RESOURCE = """
		INSERT INTO %s (
			INS_TIME, 
			IPADDR, 
			HOSTNAME, 
			MOUNT_ON, 
			MBLOCKS, 
			DISK_USED, 
			DISK_AVAILABLE, 
			DISK_USAGE)
		VALUES (
			NOW(), 
		""" % self.table_disk_resource_name
		return self.table_disk_resource_name, SQL_INS_SERVER_DISK_RESOURCE
	
	def insert_server_resource(self) :
		SQL_INS_SERVER_RESOURCE = """
		INSERT INTO %s (
			INS_TIME, 
			IPADDR, 
			HOSTNAME, 
			CPULOADAVG_1M, 
			CPULOADAVG_5M, 
			CPULOADAVG_15M, 
			MEM_TOTAL, 
			MEM_USED, 
			MEM_AVAILABLE, 
			MEM_USAGE, 
			SWAP_TOTAL, 
			SWAP_USED, 
			SWAP_AVAILABLE, 
			SWAP_USAGE)
		VALUES (
			NOW(), 
		"""	% self.table_server_resource_name
		return self.table_server_resource_name, SQL_INS_SERVER_RESOURCE
	def insert_iris_status(self) :
		SQL_INS_IRIS_STATUS = """
		INSERT INTO %s (
			INS_TIME, 
			IPADDR, 
			HOSTNAME, 
			NODE_ID, 
			SYS_STATUS, 
			ADM_STATUS, 
			UPDATE_TIME, 
			CPU, 
			LOADAVG, 
			MEM_P, 
			MEM_F, 
			DISK)
		VALUES (
			NOW(), 
		""" % self.table_iris_status_name
		return self.table_iris_status_name, SQL_INS_IRIS_STATUS

def atoi(text):
	return int(text) if text.isdigit() else text
def natural_keys(text):
	key= [atoi(c) for c in re.split('(\d+)', text)]
	return key
if __name__=='__main__':
	lm = LogMoniterHTML()
	lm.run()
