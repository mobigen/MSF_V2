#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import mce
import sys
import time
import signal
import DCReader
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

# mce handler
class MCEHandler(mce.Handler.Handler) :
	def __init__(self) :
		self.server = None
		self.reader = None

	def set(self, server, reader) :
		self.server = server
		self.reader = reader

	def handle_alv(self) :
		if (self.server and self.reader) :
			msg = self.server.noti()
			mce.info_msg(msg)

			msg = self.reader.noti()
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


def main(args, index_cycle, is_local) :
	prog_name, \
	listen_port, \
	read_dir, \
	index_file, \
	mdfs_ip, \
	mdfs_port, \
	mdfs_id, \
	mdfs_passwd = args

	# initialize mce
	mce_handler = None
	if (not is_local) :
		mce_handler = MCEHandler()
		mce.init(prog_name, handler = mce_handler, portinfo = {"listenport" : int(listen_port)})

	# login mdfs
	mdfs_client = MDFSClient(mdfs_ip, int(mdfs_port))
	mdfs_client.login(mdfs_id, mdfs_passwd)

	# create index directory
	index_dir = os.path.dirname(index_file)
	if (mdfs_client.peek(index_dir) == Response.NONE) :
		mdfs_client.mkdir(index_dir)


	reader = DCReader.DCReader(mdfs_client, read_dir, index_file, index_cycle)

	server = ListenServer.ListenServer(listen_port, reader, is_local)
	server.daemon = True
	server.start()

	if (mce_handler != None) :
		mce_handler.set(server, reader)

	while (not SHUTDOWN) : time.sleep(1)

	server.shutdown = True
	server.join()

def usage() :
	print "usage : %s [-li] prog_name listen_port mdfs_read_dir mdfs_index_file mdfs_ip mdfs_port mdfs_id mdfs_passwd" % sys.argv[0]
	print "       option :"
	print "             -l : local mode"
	print "             -i : index cycle. <default is 10>"
	print "ex    : %s -i100 ParserShaerOut 51000 /RallyDir/CUDR /Index/Share.idx 0.0.0.0 8000 mdfs mdfs" % sys.argv[0]
	sys.exit(-1)

if __name__ == "__main__" :
	import getopt
	opt_list, args = getopt.getopt(sys.argv[1:], "li:")
	index_cycle = 10
	is_local    = False
	for opt, val in opt_list :
		if (opt == "-i") : index_cycle = int(val)
		if (opt == "-l") : is_local = True

	if (MCE_TEST_MODE) :
		#args = ("SCDRParserShareOut", "51001", "/Rally/Collect/SCDR", "/Index/ShareOut/SCDRShareOut.idx", \
		#		"192.168.1.8", "8000", "mdfs", "mdfs")
		args = ("CUDRParserShareOut", "51000", "/Rally/Collect/CUDR", "/Index/ShareOut/CUDRShareOut.idx", \
				"192.168.1.8", "8000", "mdfs", "mdfs")
	else :
		if (len(args) < 8) : usage()

	main(args, index_cycle, is_local)
