#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
truelsy@mobigen.com
"""

import os
import sys
import mce
import time
import signal
import collections
import DCWriter
import ListenServer
from mdfslib.mdfs import MDFSClient
from mdfslib.mdfs_protocol_pb2 import Response

#MCE_TEST_MODE = False
MCE_TEST_MODE = True

SHUTDOWN = False

def signal_handler(snum, sfrm) :
	global SHUTDOWN
	SHUTDOWN = True

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT , signal_handler)
signal.signal(signal.SIGHUP , signal_handler)
signal.signal(signal.SIGPIPE, signal_handler)

class MCEHandler(mce.Handler.Handler) :
	def __init__(self) :
		self.th_list = []

	def handle_set(self, th_list) :
		self.th_list = th_list

	def handle_alv(self) :
		if (len(self.th_list) > 0) :
			for th in self.th_list :
				noti_msg = th.noti()
				noti_msg = noti_msg.split("|^|")
				for msg in noti_msg :
					mce.info_msg(msg)
			mce.info_msg("")
		return None

	def handle_stp(self) :
		global SHUTDOWN
		SHUTDOWN = True
		mce.info_msg("mce handler stop!!")

	def handle_mov(self) :
		global SHUTDOWN
		SHUTDOWN = True
		mce.info_msg("mce handler move!!")



def main(args, buf_size, dc_mode, is_local) :
	queue_name, \
	listen_port, \
	output_dir, \
	mdfs_ip, \
	mdfs_port, \
	mdfs_id, \
	mdfs_passwd = args

	mce_handler = None
	# initialize mce
	if (not is_local) :
		mce_handler = MCEHandler()
		mce.init(queue_name, handler = mce_handler, portinfo = {"listenport" : int(listen_port)})

	# login mdfs
	mdfs_client = MDFSClient(mdfs_ip, int(mdfs_port))
	mdfs_client.login(mdfs_id, mdfs_passwd)

	if (mdfs_client.peek(output_dir) == Response.NONE) :
		mdfs_client.mkdir(output_dir)

	# create queue
	deq = collections.deque()

	th_list = []

	server = ListenServer.ListenServer(listen_port, deq)
	server.setDaemon(True)
	server.start()
	th_list.append(server)

	writer = DCWriter.DCWriter(mdfs_client, output_dir, buf_size, dc_mode, deq)
	writer.setDaemon(True)
	writer.start()
	th_list.append(writer)

	if (mce_handler != None) :
		mce_handler.handle_set(th_list)

	while (not SHUTDOWN) :
		time.sleep(1)

	for th in th_list : th.shutdown = True

	for th in th_list : th.join()

def usage() :
	print "usage : %s [-lbm] prog_name listen_port mdfs_output_dir mdfs_ip mdfs_port mdfs_id mdfs_passwd" % sys.argv[0]
	print "		option :"
	print "				-l : local mode"
	print "				-b : DataContainer write buffer size. <default is 0>"
	print "				-m : DataContainer write mode. 'a' is append, 'w' is write mode. <default is 'a'>"
	print "ex	: %s -b3 -ma CUDRCollectWatcher 50000 /Rally/Collect/CUDR 192.168.1.8 8000 mdfs mdfs" % sys.argv[0]
	sys.exit(-1)

if __name__ == "__main__" :
	import getopt
	opt_list, args = getopt.getopt(sys.argv[1:], "lb:m:")
	buf_size = 0
	dc_mode  = "a"
	is_local = False
	for opt_key, opt_val in opt_list :
		if (opt_key == "-b") : buf_size = int(opt_val)
		if (opt_key == "-m") : dc_mode  = opt_val
		if (opt_key == "-l") : is_local = True

	if (MCE_TEST_MODE) : 
		#args = ("SCDRCollectWatcher", "50001", "/Rally/Collect/SCDR", "192.168.1.8", "8000", "mdfs", "mdfs")
		args = ("CUDRCollectWatcher", "50000", "/Rally/Collect/CUDR", "192.168.1.8", "8000", "mdfs", "mdfs")
	else :
		if (len(args) < 7) : usage()

	main(args, buf_size, dc_mode, is_local)
