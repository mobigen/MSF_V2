#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import copy
import time
import socket
import ConfigParser
import Mobigen.Common.Log as Log; Log.Init()

class DictClient :
	def __init__(self, cfg, dict_name, table_name) :
		self.env = {}
		for k, v in cfg.items("Dict") :
			self.env[k.lower()] = v
		
		self.sock = None
		self.sockfd = None

		self.dict_name = dict_name
		self.table_name = table_name

		try : self.dict_type = self.env["dict type"]
		except : self.dict_type = "dict"

		self.connect()

	def __del__(self) :
		self.disconnect()

	def close(self) :
		self.disconnect()

	def connect(self) :
		dict_list = self.env.get(self.dict_name).split(",")

		for dict in dict_list :
			try : ip, port = dict.split(":")
			except : continue
			try :
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.settimeout(3)
				sock.connect((ip, int(port)))
				sockfd = sock.makefile()
				break
			except :
				sock = None
				sockfd = None
				continue

		self.sock = sock
		self.sockfd = sockfd

		if (self.sock == None or self.sockfd == None) :
			raise Exception, "dict connect fail.."

		if (self.dict_type == "adict") :
			dummy = self.sockfd.readline()

	def disconnect(self) :
		if (self.sockfd != None) :
			try :
				self.sockfd.close()
				self.sockfd = None
			except :
				pass

		if (self.sock != None) :
			try :
				self.sock.close()
				self.sock = None
			except :
				pass
		

	def mget(self, key_list) :
		if (self.sock == None or self.sockfd == None) :
			return None

		if (self.dict_type == "adict") :
			tmp_list = []
			for el in key_list : tmp_list.append("%s,,0" % el)
			command = "mget,%s,%s\r\n" % (self.table_name, ",".join(tmp_list))
		else :
			command = "mgt,%s,%s\n" % (self.table_name, ",".join(key_list))

		try : self.sock.sendall(command)
		except : return None

		ret = None
		retry = 0
		while (retry < 5) :
			try :
				ret = self.sockfd.readline()
				break
			except socket.timeout :
				retry += 1
			except :
				break

		if (ret == None) : return ret

		ret_list = ret.strip().split(",")

		if (self.dict_type == "adict") :
			key_hash = {}
			for el in ret_list :
				if (el == "ok") : continue
				if (el == "none") : continue
				key, val = el.split("|", 1)
				key_hash[key] = val
		
			val_list = []
			for key in key_list :
				val = key_hash.get(key)
				if (val) : val_list.append(val)
				else : val_list.append("")
			return val_list
		else :
			return ret_list[1:]


class CorrelationCore :
	def __init__(self, section, conf, type = None) :
		self.section = section

		self.cfg = ConfigParser.ConfigParser()
		self.cfg.read(conf)

		self.type = type

		self.env = {}

		self.summary_dir = None
		self.column_order = None

		for k, v in self.cfg.items(self.section) :
	#	{
			k = k.lower()

			if (k == "key column index" or \
				k == "value column index") :
				continue

			if (k == "summary dir") :
				self.summary_dir = v
				continue

			if (self.type and not k.startswith(self.type)) :
				continue

			if (k.find("column order") >= 0) :
				self.column_order = map(int, re.split("\s*,\s*", v))
				continue

			if (not self.env.has_key(k)) :
				self.env[k] = []

			self.env[k].append(v)
	#	}

		self.buffer = []

		if (not os.path.exists(self.summary_dir)) :
			os.makedirs(self.summary_dir)

	def __del__(self) : 
		self.close()

	def close(self) :
		if (len(self.buffer) > 0) :
			self.buffer = []
	
	def sfio(self, line) :
		line_split = line.strip().split(",", 1)

		if (len(line_split) < 1) : return
		
		cmd = line_split.pop(0).upper()

		if (cmd == "PUT") :
			self.put(line_split[0])
		elif (cmd == "SVF") :
			try : file_prefix, data_prefix = line_split[0].strip().split(",")
			except : return
			return self.svf(file_prefix, data_prefix)

	def put(self, line) :
		self.buffer.append(line)

	def svf(self, file_prefix, data_prefix) :
		file_name = os.path.join(self.summary_dir, file_prefix + "_" + self.section + ".csv")
		fd = open(file_name + ".tmp", "w")
		for line in self.buffer :
			if (data_prefix) :
				line = data_prefix + "," + line
			fd.write(line + "\n")
		fd.close()

		os.rename(file_name + ".tmp", file_name)
		return file_name

	def correlation(self) :
		buffer = copy.copy(self.buffer)

		list_length = len(buffer)

		key_list = self.env.keys()
		key_list.sort()

		for el in key_list :
	#	{
			for sel in self.env.get(el) :
				parse = sel.split(",")

				dict_name = parse[0]
				lookup_count = int(parse[1])
				table_name = parse[2]
				key_idx = int(parse[3])
				val_count = int(parse[4])
				try : val_delimiter = parse[5]
				except : val_delimiter = None

				client = DictClient(self.cfg, dict_name, table_name)

				tmp_buffer = []

				for i in range(0, list_length, lookup_count) :
			#	{
					tmp_key_list = []
					tmp_val_list = []

					for line in buffer[i:i+lookup_count] :
						if (type(line) == list) : line_split = line
						else : line_split = line.split(",")
						tmp_key_list.append(line_split[key_idx])
						tmp_val_list.append(line_split)

					ret = client.mget(tmp_key_list)
					if (not ret) : continue

					# DICT에서 조회한 결과를 line 마지막에 추가한다.
					for j in range(0, len(ret)) :
						line_split = tmp_val_list[j]
						lookup_val = ret[j].strip()

						if (val_delimiter == None) :
							line_split.append(lookup_val)
						else :
							if (lookup_val == "") : line_split += [""] * val_count
							else : line_split += lookup_val.split(val_delimiter)

						tmp_buffer.append(line_split)
			#	}

				client.close()

				if (len(tmp_buffer) > 0) :
					buffer = tmp_buffer
		#	}

		# column 순서 재정의
		for i in range(0, list_length) :
			new_line = ",".join(map(buffer[i].__getitem__, self.column_order))
			self.buffer[i] = new_line

	def get_buffer(self) :
		return self.buffer
