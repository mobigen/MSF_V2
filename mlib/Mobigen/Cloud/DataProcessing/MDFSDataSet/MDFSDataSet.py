#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import MDFSDataSetLog
from mdfslib.mdfs_protocol_pb2 import Response
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

class MDFSDataSet :
	def __init__(self, mdfs_client, mdfs_file, **args) :
		self.mdfs_client   = mdfs_client
		self.cur_file	 = None
		self.prev_file	 = None
		self.args        = args

		try : self.mode = args["Mode"]
		except : self.mode = "r"
		
		if (self.mode in ("a", "w")) :
			self.mdfs_file = mdfs_file + ".cds"
		else :
			self.mdfs_file = mdfs_file

		mdfs_dir = os.path.dirname(self.mdfs_file)
		if (self.mdfs_client.peek(mdfs_dir) == Response.NONE) :
			self.mdfs_client.mkdir(mdfs_dir)

		self.cur_ds	   = self.create_new_dataset()

	def create_new_dataset(self) :
		return MDFSDataSetLog.MDFSDataSetLog(self.mdfs_file, self.mdfs_client, **self.args)

	def put(self, raw_data, opt="") :
		return self.cur_ds.put(raw_data, opt)

	def next(self) :
		for (data, opt) in self.cur_ds.get() :
			yield (data, opt)

	def close(self) :
		try : self.cur_ds.close()
		except : pass

	def __del__(self) :
		self.close()
