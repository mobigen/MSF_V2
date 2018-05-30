# -*- coding: utf-8 -*-

import os
from mdfslib.mdfs_protocol_pb2 import Response
import Mobigen.Cloud.DataProcessing.MDFSDataContainer.MDFSDataContainer as MDFSDataContainer

class DCReader :
	def __init__(self, mdfs_client, read_dir, index_file, index_cycle) :
		self.mdfs_client = mdfs_client
		self.read_dir    = read_dir
		self.index_file  = index_file
		self.index_cycle = int(index_cycle)
		self.class_name  = self.__class__.__name__

		self.cdc = MDFSDataContainer.MDFSDataContainer(self.mdfs_client, self.read_dir, Mode="r")

		self.idx_ftime = None
		self.idx_recno = None

		last_time, last_no = self.get_index()
		if (last_time and last_no) :
			self.cdc.get(last_time, int(last_no))
			self.idx_ftime = last_time
			self.idx_recno = last_no
		else :
			self.cdc.get_last()


	def __del__(self) :
		self.close()

	def __iter__(self) :
		return self

	def noti(self) :
		try : return "%16s : current proctime(%s) index(%s)" % (self.class_name, self.idx_ftime, self.idx_recno)
		except Exception, err : return "%16s : error cause(%s)" % (self.class_name, str(err))

	def get_index(self) :
		try :
			if (self.mdfs_client.peek(self.index_file) == Response.FILE) :
				fd = self.mdfs_client.open(self.index_file, "r")
				line = fd.readline()
				file_time, rec_no = line.strip().split(",")
				return (file_time, rec_no)
			else :
				return (None, None)
		except :
			return (None, None)

	def put_index(self, file_time, rec_no) :
		try : self.mdfs_client.rm(self.index_file)
		except : pass
		fd = self.mdfs_client.open(self.index_file, "w")
		fd.write("%s,%d" % (file_time, rec_no))
		fd.close()

	def next(self) :
		ftime, mtime, opt, index, raw_data = self.cdc.next()

		if (index % self.index_cycle == 0) :
			self.put_index(ftime, index)
			self.idx_ftime = ftime
			self.idx_recno = index

		return (ftime, mtime, opt, index, raw_data)

	def close(self) :
		try : self.cdc.close()
		except : pass

if __name__ == "__main__" :
	from mdfslib.mdfs import MDFSClient
	from mdfslib.mdfs_protocol_pb2 import Response
	mdfs_client = MDFSClient("localhost", 8000)
	mdfs_client.login("mdfs", "mdfs")

	r = DCReader(mdfs_client, "/RAW_DATA/CollectDir", "/Index/Share.idx", "1")

	print r.next()
	print r.next()

	mdfs_client.close()
