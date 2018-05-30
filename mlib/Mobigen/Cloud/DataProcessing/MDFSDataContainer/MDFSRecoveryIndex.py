#!/usr/bin/env python

import sys
try : from mdfslib.mdfs import MDFSClient
except : from mdfs import MDFSClient
try : from mdfslib.mdfs_protocol_pb2 import Response
except : from mdfs_protocol_pb2 import Response
import MDFSDataLog

def usage() :
	print "usage : %s mdfs_ip mdfs_port mdfs_id mdfs_passwd recovery_idx_file" % sys.argv[0]
	print "ex    : %s localhost 8000 mdfs mdfs mega/dc_test/20111129150000.cdb.idx" % sys.argv[0]
	sys.exit()

if (len(sys.argv) < 6) : usage()

mdfs_ip, mdfs_port, mdfs_id, mdfs_pass, recover_file = sys.argv[1:]

client = MDFSClient(mdfs_ip, int(mdfs_port))
client.login(mdfs_id, mdfs_pass)

MDFSDataLog.recovery_idx(client, recover_file)

client.close()
