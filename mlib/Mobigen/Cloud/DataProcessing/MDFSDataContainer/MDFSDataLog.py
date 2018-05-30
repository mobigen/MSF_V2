#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
truelsy@mobigen.com
"""

import re
import os
import sys
import time
import struct
try : from mdfslib.mdfs_protocol_pb2 import Response
except : from mdfs_protocol_pb2 import Response
from socket import timeout

OVH_SIZE = 40

def error(msg) :
	try :
		sys.stderr.write( "--- error : %s\n" % msg )
		sys.stderr.flush()
	except :
		pass

def debug(msg) :
	try :
		sys.stderr.write( "*** debug : %s\n" % msg )
		sys.stderr.flush()
	except :
		pass

def log(msg) :
	try :
		sys.stderr.write( "+++ log : %s\n" % msg )
		sys.stderr.flush()
	except :
		pass

def idx_pack(rec_no, data_offset, msg_time, opt) :
	return struct.pack("!QQQ16s", rec_no, data_offset, int(msg_time), "%16s" % opt)

def idx_unpack(idx_info) :
	rec_no, data_offset, msg_time, opt = struct.unpack('!QQQ16s', idx_info)
	return (rec_no, data_offset, msg_time, opt)

def data_pack(rec_no, data_len, msg_time, opt) :
	return struct.pack("!QQQ16s", rec_no, data_len, int(msg_time), "%16s" % opt)

def data_unpack(data_info) :
	rec_no, data_len, msg_time, opt = struct.unpack('!QQQ16s', data_info)
	return (rec_no, data_len, msg_time, opt)

def get_last_idx(idx_file_len) :
	return (idx_file_len / OVH_SIZE) - 1

def recovery_idx(mdfs_client, idx_file_name) :
	idx_file_name_tmp = idx_file_name + ".tmp"
	data_file_name = os.path.splitext(idx_file_name)[0]

	fd_data = mdfs_client.open(data_file_name, "r")

	if (mdfs_client.peek(idx_file_name) != Response.NONE) :
		mdfs_client.rm(idx_file_name)

	fd_idx_tmp = mdfs_client.open(idx_file_name_tmp, "w")

	data_offset = 0
	serial_num  = 0
	buf		 = []

	while (True) :
		try :
			ovh = fd_data.randomread(OVH_SIZE)
			if (len(ovh) != OVH_SIZE) : break

			rec_no, data_len, msg_time, opt = data_unpack(ovh)

			if (serial_num != rec_no) :
				fd_data.close()
				fd_idx_tmp.close()
				print "data file correpted, recnoInDataFile=%s, serialNum=%s" % (rec_no, serial_num)
				break

			idx_info = idx_pack(rec_no, data_offset, msg_time, opt)
		
			buf.append(idx_info)

			data_offset += OVH_SIZE + data_len
			serial_num  += 1

			if (serial_num % 1000 == 0) :
				print "%s data processed.." % serial_num
				fd_idx_tmp.write("".join(buf))
				fd_idx_tmp.flush()
				buf = []

			tmp = fd_data.randomread(data_len)
		except Exception, err :
			error(err.__str__())
			break
		
	if (len(buf) != 0) :
		fd_idx_tmp.write("".join(buf))
		fd_idx_tmp.flush()

	fd_data.close()
	fd_idx_tmp.close()

	mdfs_client.mv(idx_file_name_tmp, idx_file_name)
	print "*** idxfile(%s) recovery OK, secno(%d)" % (idx_file_name, serial_num) 


def recovery_data(mdfs_client, data_file_name) :
	data_file_name_tmp = data_file_name + ".tmp"
	fd_data = mdfs_client.open(data_file_name, "r")
	fd_data_tmp = mdfs_client.open(data_file_name_tmp, "w")

	data_offset = 0
	serial_num  = 0
	buf		 = []

	while (True) :
		ovh = fd_data.randomread(OVH_SIZE)
		if (len(ovh) != OVH_SIZE) : break

		rec_no, data_len, msg_time, opt = data_unpack(ovh)

		if (serial_num != rec_no) :
			fd_data.close()
			fd_data_tmp.close()
			print "data file correpted, recnoInDataFile=%s, serialNum=%s" % (rec_no, serial_num)
			break

		data = fd_data.randomread(data_len)

		if (len(data) != data_len) :
			fd_data.close()
			fd_data_tmp.close()
			print "data file correpted, len(data)=%s, data_len=%s" % (len(data), data_len)
			break

		data_info = data_pack(serial_num, data_len, msg_time, opt)
		fd_data_tmp.write(data_info + data)
		fd_idx_tmp.flush()
		serial_num += 1

		if (serial_num % 1000 == 0) :
			print "%s data processed.." % serial_num

	fd_data.close()
	fd_data_tmp.close()

	mdfs_client.mv(data_file_name, data_file_name + ".org")
	mdfs_client.mv(data_file_name_tmp, data_file_name)

	print "*** datafile(%s) recovery OK, secno(%d)" % (data_file_name, serial_num) 

class MDFSDataLog :
	def __init__(self, file_name, mdfs_client, **args) :
		try : self.mode = args["Mode"]
		except : self.mode = "r"

		try : self.buf_size = args["BufSize"]
		except : self.buf_size = 0

		try : self.wait_data_sec = args["WaitDataSec"]
		except : self.wait_data_sec = 0.1

		try : self.read_block_timeout = args["ReadBlockTimeout"]
		except : self.read_block_timeout = 0

		try : self.opt_filter = re.compile(args["OptionFilter"])
		except : self.opt_filter = None

		self.mdfs_client	= mdfs_client
		self.idx_file_name  = file_name + ".idx"
		self.data_file_name = file_name

		# unlock file (2012.02.21 mega)
		if (self.mdfs_client.peek(self.data_file_name) == Response.FILE) : self.mdfs_client.unlock(self.data_file_name)
		if (self.mdfs_client.peek(self.idx_file_name) == Response.FILE) : self.mdfs_client.unlock(self.idx_file_name)

		self.rec_no		= 0
		self.buf_idx	   = []
		self.buf_data	  = []
		self.cur_data_info = ""
		self.cur_raw_data  = ""
		self.data_offset   = 0
		self.data_file_len = 0

		if (self.mode == "w") :
			if (self.mdfs_client.peek(self.data_file_name) == Response.FILE) : self.mdfs_client.rm(self.data_file_name)
			if (self.mdfs_client.peek(self.idx_file_name) == Response.FILE) : self.mdfs_client.rm(self.idx_file_name)
			self.fd_data = self.mdfs_client.open(self.data_file_name, "w")
			self.fd_idx  = self.mdfs_client.open(self.idx_file_name, "w")
		elif (self.mode == "a") :
			if (self.mdfs_client.peek(self.data_file_name) == Response.FILE \
					and self.mdfs_client.peek(self.idx_file_name) == Response.FILE) :
				self.fd_data = self.mdfs_client.open(self.data_file_name, "r")
				self.fd_idx  = self.mdfs_client.open(self.idx_file_name, "r")
				self.recover_writer()
				self.fd_data.close()
				self.fd_data = self.mdfs_client.open(self.data_file_name, "a")
				self.fd_idx.close()
				self.fd_idx  = self.mdfs_client.open(self.idx_file_name, "a")
			elif (self.mdfs_client.peek(self.data_file_name) == Response.FILE \
					and self.mdfs_client.peek(self.idx_file_name) == Response.NONE) :
				self.fd_data = self.mdfs_client.open(self.data_file_name, "r")
				self.recover_writer()
				self.fd_data.close()
				self.fd_data = self.mdfs_client.open(self.data_file_name, "a")
				self.fd_idx  = self.mdfs_client.open(self.idx_file_name, "a")
			elif (self.mdfs_client.peek(self.data_file_name) == Response.NONE \
					and self.mdfs_client.peek(self.idx_file_name) == Response.FILE) :
				self.mdfs_client.rm(self.idx_file_name)
				self.fd_data = self.mdfs_client.open(self.data_file_name, "w")
				self.fd_idx  = self.mdfs_client.open(self.idx_file_name, "w")
			elif (self.mdfs_client.peek(self.data_file_name) == Response.NONE \
					and self.mdfs_client.peek(self.idx_file_name) == Response.NONE) :
				self.fd_data = self.mdfs_client.open(self.data_file_name, "w")
				self.fd_idx  = self.mdfs_client.open(self.idx_file_name, "w")
		else :
			while (True) :
				if (self.mdfs_client.peek(self.data_file_name) == Response.NONE \
						or self.mdfs_client.peek(self.idx_file_name) == Response.NONE) :
					log("%s, %s file not exist, so sleep 60 loop" % (self.data_file_name, self.idx_file_name))
					time.sleep(60)
					continue
				self.fd_data = self.mdfs_client.open(self.data_file_name, "r")
				self.fd_idx  = self.mdfs_client.open(self.idx_file_name, "r")
				self.data_file_len = self.mdfs_client.getsize(self.data_file_name)
				break

	def recover_writer(self) :
		if (self.mdfs_client.peek(self.idx_file_name) == Response.NONE) :
			idx_file_len = 0
		else :
			idx_file_len = self.mdfs_client.getsize(self.idx_file_name)

		last_idx = get_last_idx(idx_file_len)
		if (last_idx == -1) :
			rec_no, data, msg_time, opt = (-1, "", "0000000000", "")
		else :
			rec_no, data, msg_time, opt = self.get(last_idx)
			debug("rec_no (%d)" % rec_no)

		self.rec_no = rec_no + 1
		self.data_offset = self.fd_data.tell()
		#debug(self.data_offset)

		buf = []
		b_recovery = False
		fd_idx_tmp = self.mdfs_client.open(self.idx_file_name + ".rec", "w")

		while (True) :
			cur_data_offset = self.fd_data.tell()
			old_data_offset = cur_data_offset

			data_file_len   = self.mdfs_client.getsize(self.data_file_name)

			#debug("cur_data_offset(%s)" % cur_data_offset)
			#debug("data_file_len  (%s)" % data_file_len)
			if (cur_data_offset + OVH_SIZE <= data_file_len) :
				self.cur_data_info = self.fd_data.randomread(OVH_SIZE)
			else :
				log("Index file(%s) status OK!" % self.idx_file_name)
				break

			rec_no, data_len, msg_time, opt = data_unpack(self.cur_data_info)

			cur_data_offset = self.fd_data.tell()
			data_file_len   = self.mdfs_client.getsize(self.data_file_name)

			if (cur_data_offset + data_len <= data_file_len) :
				tmp = self.fd_data.randomread(data_len)   # move file pointer [ fd.seek(data_len, 1) ]
				idx_info = idx_pack(rec_no, old_data_offset, msg_time, opt)
				buf.append(idx_info)
				self.rec_no = rec_no + 1
				self.data_offset = self.fd_data.tell()

				if (rec_no % 1000 == 0) :
					fd_idx_tmp.write("".join(buf))
					fd_idx_tmp.flush()
					b_recovery = True
					log ("recno(%s) recovery processed!" % (rec_no))
					buf = []
			else :
				self.fd_data.seek(old_data_offset)
				break

		if (len(buf) != 0) :
			fd_idx_tmp.write("".join(buf))
			fd_idx_tmp.flush()
			b_recovery = True
			log ("recno(%s) recovery processed!" % (rec_no))

		if (b_recovery) :
			fd_idx_tmp.close()
			self.mdfs_client.rm(self.idx_file_name)
			self.mdfs_client.mv(self.idx_file_name + ".rec", self.idx_file_name)
		else :
			fd_idx_tmp.close()
			self.mdfs_client.rm(self.idx_file_name + ".rec")

		#self.fd_idx.seek(self.fd_idx.tell())
		#self.fd_data.seek(self.fd_data.tell())

		log ("Index file(%s) check OK!, last recno(%s)" % (self.idx_file_name, rec_no))

	def write_data(self, data) :
		#while (data) :
		#	put_bytes = self.fd_data.write(data)
		#	data = data[put_bytes:]
		self.fd_data.write(data)
		self.fd_data.flush()

	def write_idx(self, idx) :
		#while (idx) :
		#	put_bytes = self.fd_idx.write(idx)
		#	idx = idx[put_bytes:]
		self.fd_idx.write(idx)
		self.fd_idx.flush()

	def put(self, data, msg_time="00000000000000", opt="") :
		data = str(data)
		data_len = len(data)

		idx_info  = idx_pack(self.rec_no, self.data_offset, msg_time, opt)
		data_info = data_pack(self.rec_no, data_len, msg_time, opt)

		put_data = data_info + data

		if (self.buf_size == 0) :
			self.write_data(put_data)
			self.write_idx(idx_info)
		else :
			self.buf_data.append(put_data)
			self.buf_idx.append(idx_info)
			#debug("bufsize(%d) datsize(%d)" % (self.buf_size, len(self.buf_idx)))
			if (self.buf_size == len(self.buf_idx)) :
				self.write_data("".join(self.buf_data))
				self.write_idx("".join(self.buf_idx))

				self.buf_data = []
				self.buf_idx  = []
		
		self.rec_no += 1
		self.data_offset += OVH_SIZE + data_len
		return self.rec_no - 1

	def set(self, key) :
		rec_no, data_offset, msg_time, opt = self.get_idx(key)
		# TODO : compare filesize with data_offset?
		self.fd_data.seek(data_offset)
		#cur_pos = self.fd_data.tell()
		#if (data_offset > cur_pos) :
		#	raise Exception, \
		#			"data file out of range: data_offset(%s) > cur_pos(%s)" \
		#			% (data_offset, cur_pos)
	
	def get(self, key) :
		self.set(key)
		return self.next()

	def get_idx(self, key) :
		idx_offset = key * OVH_SIZE
		# TODO : compare filesize with data_offset?
		self.fd_idx.seek(idx_offset)
		#cur_pos = self.fd_idx.tell()
		#if (idx_offset > cur_pos) :
		#	raise Exception, \
		#			"idx out of range: idx_offset(%s) > cur_pos(%s)" \
		#			% (idx_offset, cur_pos)
		
		(rec_no, data_offset, msg_time, opt) = self.next_idx()
		if (rec_no != key) :
			raise Exception, \
					"key idxRecNo mismatch: key = %s, idxRecNo = %s" \
					% (key, rec_no)

		return (rec_no, data_offset, msg_time, opt)

	def next_idx(self) :
		idx_info = self.fd_idx.randomread(OVH_SIZE)
		if (len(idx_info) < OVH_SIZE) :
			raise Exception, "idx out of range"

		(rec_no, data_offset, msg_time, opt) = idx_unpack(idx_info)
		return (rec_no, data_offset, msg_time, opt)

	def filter(self, opt) :
		ret = False
		if (not self.opt_filter or self.opt_filter.search(opt)) :
			ret = True
		return ret

	def next(self) :
		wait_count = 0
		if (self.cur_data_info == "") : cur_info_size = 0
		else : cur_info_size = len(self.cur_data_info)

		if (cur_info_size < OVH_SIZE) :
			read_bytes = OVH_SIZE - cur_info_size
			tmp_info = None
			while (True) :
				tmp_info = self.fd_data.randomread(read_bytes)
				if (tmp_info) :
					self.cur_data_info += tmp_info
					tmp_info_size = len(tmp_info)
					if (tmp_info_size < read_bytes) :
						read_bytes = read_bytes - tmp_info_size
						continue
					else :
						break

				if (self.read_block_timeout == 0) :
					raise timeout, "no header to read 1"
				elif (wait_count > self.read_block_timeout) :
					#debug("raise timeout")
					raise timeout, "no header to read 2"
				else :
					wait_count += self.wait_data_sec
					#debug("wait_count(%d) wait_data_sec(%d)" % (wait_count, self.wait_data_sec))
					time.sleep(self.wait_data_sec)

		(rec_no, data_len, msg_time, opt) = data_unpack(self.cur_data_info)

		#debug("opt (%s)" % opt)
		if (not self.filter(opt)) :
			cur_pos = self.fd_data.tell()
			#debug("opt(%s) cur_pos(%d), data_len(%d)" % (opt, cur_pos, data_len))
			self.fd_data.seek(cur_pos + data_len)
			rec_no, raw_data, msg_time, opt = (None, None, None, None)
		else :
			tmp_data = None
			if (self.cur_raw_data == "") : read_bytes = data_len
			else : read_bytes = data_len - len(self.cur_raw_data)

			while (True) :
				tmp_data = self.fd_data.randomread(read_bytes)
				if (tmp_data) :
					self.cur_raw_data += tmp_data
					tmp_data_size = len(tmp_data)
					if (tmp_data_size < read_bytes) :
						read_bytes = read_bytes - tmp_data_size
						continue
					else :
						break

				if (self.read_block_timeout == 0) :
					raise timeout, "no header to read 3"
				elif (wait_count > self.read_block_timeout) :
					raise timeout, "no header to read 4"
				else :
					wait_count += self.wait_data_sec
					time.sleep(self.wait_data_sec)
		
			raw_data = self.cur_raw_data

		self.cur_data_info = ""
		self.cur_raw_data  = ""

		return (rec_no, raw_data, msg_time, opt)


	def close(self) :
		log(" MDFSDataLog close!!")
		if (self.mode in ("a", "w")) :
			if (len(self.buf_idx) > 0) :
				self.write_data("".join(self.buf_data))
				self.write_idx("".join(self.buf_idx))

				self.buf_data = []
				self.buf_idx  = []

		try : self.fd_data.close()
		except Exception, err : error(err.__str__())

		try : self.fd_idx.close()
		except Exception, err : error(err.__str__())

	def __del__(self) :
		try : self.close()
		except : pass

