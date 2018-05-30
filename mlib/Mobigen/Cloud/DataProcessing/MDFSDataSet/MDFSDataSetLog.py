# -*- coding: utf-8 -*-

import re
import os
import sys
import time
import struct
from mdfslib.mdfs_protocol_pb2 import Response
from socket import timeout

HEADER_SIZE = 24

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

def data_pack(data_len, opt) :
	return struct.pack("!Q16s", data_len, "%16s" % opt)

def data_unpack(data_info) :
	data_len, opt = struct.unpack("!Q16s", data_info)
	return (data_len, opt)

class MDFSDataSetLog :
	def __init__(self, file_name, mdfs_client, **args) :
		try : self.mode = args["Mode"]
		except : self.mode = "r"

		try : self.buf_size = args["BufSize"]
		except : self.buf_size = 0

		try : self.opt_filter = re.compile(args["OptionFilter"])
		except : self.opt_filter = None

		self.mdfs_client = mdfs_client
		self.data_file_name = file_name

		self.buf_data	  = []
		self.cur_data_info = None
		self.data_offset   = 0
		self.data_file_len = 0

		if (self.mode == "w") :
			if (self.mdfs_client.peek(self.data_file_name) == Response.FILE) :
				self.mdfs_client.rm(self.data_file_name)
			self.fd_data = self.mdfs_client.open(self.data_file_name, "w")
		elif (self.mode == "a") :
			if (self.mdfs_client.peek(self.data_file_name) == Response.FILE) :
				self.fd_data = self.mdfs_client.open(self.data_file_name, "a")
			else :
				self.fd_data = self.mdfs_client.open(self.data_file_name, "w")
		else :
			self.fd_data = self.mdfs_client.open(self.data_file_name, "r")
			self.data_file_len = self.mdfs_client.getsize(self.data_file_name)


	def put(self, data, opt="") :
		data = str(data)
		data_len = len(data)
		data_info = data_pack(data_len, opt)

		put_data = data_info + data

		if (self.buf_size == 0) :
			self.write_data(put_data)
		else :
			self.buf_data.append(put_data)
			if (self.buf_size == len(self.buf_data)) :
				self.write_data("".join(self.buf_data))
				self.buf_data = []

		self.data_offset += HEADER_SIZE + data_len
		return self.data_offset

	def filter(self, opt) :
		ret = False
		if (not self.opt_filter or self.opt_filter.search(opt)) :
			ret = True
		return ret

	def get(self) :
		while (True) :
			cur_offset = self.fd_data.tell()
			if (cur_offset + HEADER_SIZE > self.data_file_len) : break
			self.cur_data_info = self.fd_data.read(HEADER_SIZE)

			data_len, opt = data_unpack(self.cur_data_info)

			cur_offset = self.fd_data.tell()
			if (cur_offset + data_len > self.data_file_len) : break
			data = self.fd_data.read(data_len)

			if (self.filter(opt)) : pass
			else : continue

			yield (opt, data)

	def write_data(self, data) :
		self.fd_data.write(data)
		self.fd_data.flush()
		#while (data) :
		#	put_bytes = self.fd_data.write(data)
		#	data = data[put_bytes:]

	def close(self) :
		log(" MDFSDataSetLog close!!")
		if (self.mode in ("a", "w")) :
			if (len(self.buf_data) > 0) :
				self.write_data("".join(self.buf_data))
				self.buf_data = []

		self.fd_data.close()

	def __del__(self) :
		try : self.close()
		except : pass
