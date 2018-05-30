#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
truelsy@mobigen.com
"""

import re
import os
import sys
import time
import MDFSDataLog
try : from mdfslib.mdfs_protocol_pb2 import Response
except : from mdfs_protocol_pb2 import Response
from socket import timeout

def error(msg) :
	try :
		sys.stderr.write("--- error : %s\n" % msg)
		sys.stderr.flush()
	except : 
		pass

def debug(msg) :
	try :
		sys.stderr.write("*** debug : %s\n" % msg)
		sys.stderr.flush()
	except : 
		pass

def log(msg) :
	try :
		sys.stderr.write("+++ log : %s\n" % msg)
		sys.stderr.flush()
	except : 
		pass

class MDFSDataContainer :
	def __init__(self, mdfs_client, mdfs_dir, **args) :
		self.mdfs_client   = mdfs_client
		self.mdfs_dir	  = mdfs_dir
		self.b_first_put   = True
		self.b_next_file   = False
		self.cur_file_time = "00000000000000"
		self.cur_db		= None
		self.args		  = args
		self.next_file_buf = []

		try : self.keep_hour = args["KeepHour"]
		except : self.keep_hour = 24

		try : self.interval_hour = args["FileTimeInterval"]
		except : self.interval_hour = -1

		try : self.mode = args["Mode"]
		except : self.mode = "r"

		try : self.read_block_timeout = args["ReadBlockTimeout"]
		except : self.read_block_timeout = 0

		try : self.wait_data_sec = args["WaitDataSec"]
		except : self.wait_data_sec = 0.1

		try : self.next_file_check_sec = args["NextFileCheckSec"]
		except : self.next_file_check_sec = 10

		try : self.no_data_count = args["NoDataReturnCount"]
		except : self.no_data_count = 0

		self.next_file_check_count = 0

		if (self.mdfs_client.peek(mdfs_dir) == Response.NONE) :
			self.mdfs_client.mkdir(mdfs_dir)

		if (self.mode == "a") :
			last_file_time, last_rec_no = self.get_last_file_time_recno()
			if (last_file_time != None) :
				self.cur_file_time = last_file_time
				file_name = self.make_file_name(last_file_time)
				self.cur_db = self.create_new_db(file_name)

	def make_file_time(self, msg_time) :
		return msg_time[:10] + "0000"

	def make_file_time_by_file_name(self, file_name) :
		base_name = os.path.basename(file_name)
		return base_name[:10] + "0000"

	def make_file_name(self, file_time) :
		return os.path.join(self.mdfs_dir, file_time + ".cdb")

	def make_file_name_list(self) :
		file_name_list = self.get_file_name_list()
		cur_file_name = self.make_file_name(self.cur_file_time)
		for file_name in file_name_list :
			if (file_name > cur_file_name) :
				self.next_file_buf.append(file_name)
		log("next file buf %s" % self.next_file_buf)

	def make_idx_file_name(self, file_name) :
		return "%s.idx" % file_name

	def create_new_db(self, file_name) :
		return MDFSDataLog.MDFSDataLog(file_name, self.mdfs_client, **self.args)

	def get_first_file_time_recno(self) :
		file_name_list = self.get_file_name_list()
		if (len(file_name_list) == 0) : return (None, None)
		first_file_name = file_name_list[0]
		first_file_time = self.make_file_time_by_file_name(first_file_name)
		return (first_file_time, 0)

	def get_last_file_time_recno(self) :
		file_name_list = self.get_file_name_list()
		if (len(file_name_list) == 0) : return (None, None)

		last_file_name = file_name_list[-1]
		idx_file_name  = self.make_idx_file_name(last_file_name)
		idx_file_len   = self.mdfs_client.getsize(idx_file_name)
		last_rec_no	= MDFSDataLog.get_last_idx(idx_file_len)
		last_file_time = self.make_file_time_by_file_name(last_file_name)

		if (last_rec_no < 0) : last_rec_no = 0

		return (last_file_time, last_rec_no)

	def get_file_name_list(self) :
		pattern = re.compile(r"20\d{12}.cdb.idx$")
		tmp_file_list = self.mdfs_client.ls(self.mdfs_dir)
		file_list = []
		for file in tmp_file_list :
			if (file.type != Response.FILE) : continue
			if (not pattern.match(file.path)) : continue
			#debug(file.path)
			tmp_file = os.path.join(self.mdfs_dir, os.path.splitext(file.path)[0])
			file_list.append(tmp_file)
		file_list.sort()
		return file_list

	def get_next_file_time(self) :
		return self.make_file_time_by_file_name(self.next_file_buf.pop(0))

	def is_exist_next_file(self) :
		if (len(self.next_file_buf) > 0) :
			return True

		if (self.next_file_check_count > self.next_file_check_sec) :
			self.make_file_name_list()
			self.next_file_check_count = 0
		else :
			self.next_file_check_count += self.wait_data_sec

		if (self.read_block_timeout) : self.make_file_name_list()

		if (len(self.next_file_buf) > 0) : return True
		return False

	def remove_data(self) :
		m = re.search('^(\d{4})(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)$', self.cur_file_time)
		jul_fmt_str  = "%s-%s-%s %s:%s:%s" % (m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6))
		jul_time	 = time.mktime(time.strptime(jul_fmt_str, "%Y-%m-%d %H:%M:%S"))
		rm_file_time = time.strftime('%Y%m%d%H0000', time.localtime(jul_time - (3600 * self.keep_hour)))
		rm_file_name = self.make_file_name(rm_file_time)
		
		file_name_list = self.get_file_name_list()
		for file_name in file_name_list :
			if (file_name < rm_file_name) :
				log("remove file (%s)" % file_name)
				if (self.mdfs_client.peek(file_name) == Response.FILE) :
					self.mdfs_client.rm(file_name)
				idx_file_name = self.make_idx_file_name(file_name)
				if (self.mdfs_client.peek(idx_file_name) == Response.FILE) :
					self.mdfs_client.rm(idx_file_name)


	def put(self, msg_time, raw_data, opt_data="") :
		file_time = self.make_file_time(msg_time)
		if (file_time > self.cur_file_time) :
			if (self.interval_check(file_time, self.cur_file_time)) :
				self.cur_file_time = file_time
				file_name = self.make_file_name(file_time)
				if (self.cur_db) : self.cur_db.close()
				self.cur_db = self.create_new_db(file_name)
				self.remove_data()
			else :
				log("out of time range data!! interval(%s) cur_file_time(%s) msg_time(%s)" \
						% (self.interval_hour, self.cur_file_time, msg_time))
				return -1

		#debug("raw_data(%s)" % raw_data)
		#debug("msg_time(%s)" % msg_time)
		#debug("opt_data(%s)" % opt_data)
		return self.cur_db.put(raw_data, msg_time, opt_data)

	def interval_check(self, new_time, cur_time) :
		try :
			if (self.interval_hour == -1 or cur_time == "00000000000000") :
				return True

			ntime = time.mktime(time.strptime(new_time[:10],'%Y%m%d%H'))
			ctime = time.mktime(time.strptime(cur_time[:10],'%Y%m%d%H'))
			interval = (ntime - ctime) / 3600
			if (interval <= self.interval_hour) : return True
			else : return False
		except :
			return False

	def get(self, file_time, rec_no=0) :
		file_time = self.make_file_time(file_time)
		if (file_time != self.cur_file_time) :
			self.cur_file_time = file_time
			file_name = self.make_file_name(file_time)
			if (self.cur_db) : self.cur_db.close()
			self.cur_db = self.create_new_db(file_name)

		#debug("cur_file_time(%s) filename(%s) recno(%s)" % (self.cur_file_time, file_name, rec_no))
		try :
			key, value, msg_time, opt = self.cur_db.get(rec_no)
			return self.cur_file_time, msg_time, opt, key, value
		except Exception, err :
			raise Exception, "no data to read (%s)" % str(err)
		   # raise Exception, str(err)

	def get_first(self) :
		file_time, rec_no = self.get_first_file_time_recno()
		return self.get(file_time, rec_no)

	def get_last(self) :
		file_time, rec_no = self.get_last_file_time_recno()
		return self.get(file_time, rec_no)

	def next(self) :
		wait_count = 0
		while (True) :
			try :
				if (self.cur_db == None) :
					last_file_time, last_rec_no = self.get_last_file_time_recno()
					if (last_file_time == None) :
						raise timeout, "last file is null"
					else :
						self.cur_file_time = last_file_time
						file_name = self.make_file_name(last_file_time)
						self.cur_db = self.create_new_db(file_name)
						return self.get(last_file_time, last_rec_no)
				else :
					key, value, msg_time, opt = self.cur_db.next()
					if (key == None) : continue
					return self.cur_file_time, msg_time, opt, key, value
			except timeout, err :
				if (self.b_next_file == False) :
					if (self.is_exist_next_file()) :
						self.b_next_file = True
						continue
					else :
						if (self.no_data_count > 0) :
							wait_count += self.wait_data_sec
							time.sleep(self.wait_data_sec)
							if (wait_count > self.no_data_count) :
								return (self.cur_file_time, None, None, None, "no data to read")

						if (self.read_block_timeout == 0) :
							time.sleep(self.wait_data_sec)
							continue
						else :
							raise timeout, err.__str__()
				else :  # switch next file
					self.cur_file_time = self.get_next_file_time()
					file_name = self.make_file_name(self.cur_file_time)
					log("change next file (%s)" % file_name)
					if (self.cur_db) : self.cur_db.close()
					self.cur_db = self.create_new_db(file_name)
					self.b_next_file = False
					continue
			except Exception, err :
				error("next exception cause( %s )" % str(err))
				if (str(err) == "(103, u'path does not exist')") : return self.get_first()

	def close(self) :
		log(" MDFSDataContainer close!!")
		try : self.cur_db.close()
		except : pass

	def __del__(self) :
		self.close()
