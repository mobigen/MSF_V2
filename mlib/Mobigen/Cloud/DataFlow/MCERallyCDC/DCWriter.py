# -*- coding: utf-8 -*-

import sys
import time
import threading
from traceback import *
import Mobigen.Cloud.DataProcessing.MDFSDataContainer.MDFSDataContainer as MDFSDataContainer

class DCWriter(threading.Thread) :
	def __init__(self, mdfs_client, output_dir, buf_size, dc_mode, deq) :
		threading.Thread.__init__(self)

		self.mdfs_client = mdfs_client
		self.output_dir  = output_dir
		self.deq         = deq
		self.buf_size    = buf_size

		self.shutdown    = False
		self.dc_mode     = dc_mode
		self.last_data   = None

		self.class_name  = self.__class__.__name__

	def noti(self) :
		try : status_msg = "%16s : remain data count (%d)" % (self.class_name, len(self.deq))
		except Exception, err : status_msg = "%16s : error cause (%s)" % (self.class_name, str(err))
		data_msg = "%16s : last data (%s)" % (self.class_name, self.last_data)
		return status_msg + "|^|" + data_msg

	def run(self) :
		cdc = MDFSDataContainer.MDFSDataContainer(self.mdfs_client, \
												self.output_dir, \
												Mode=self.dc_mode, \
												BufSize=self.buf_size)

		while (not self.shutdown) :
			try :
				if (len(self.deq) == 0) :
					time.sleep(0.1)
					continue
				data = self.deq.pop()
				msg_time, opt, raw_data = data.split(",", 2)
				cdc.put(msg_time, raw_data, opt[:16])
				self.last_data = data
			except :
				etype, value, tb = sys.exc_info()
				print_exception(etype, value, tb)
				time.sleep(1)
				continue

		try : cdc.close()
		except : pass


if __name__ == "__main__" :
	from mdfslib.mdfs import MDFSClient
	from mdfslib.mdfs_protocol_pb2 import Response
	mdfs_client = MDFSClient("localhost", 8000)
	mdfs_client.login("mdfs", "mdfs")

	import collections
	deq = collections.deque()

	dcw = DCWriter(mdfs_client, "/RAW_DATA/CollectDir", 0, "a", deq)
	dcw.daemon = True
	dcw.start()

	for i in range(0, 100) :
		deq.appendleft("20111207200000,rawdata,opt")

	while (True) :
		if (len(deq) > 0) :
			time.sleep(0.5)
			continue
		break

	dcw.shutdown = True
	
	dcw.join()
