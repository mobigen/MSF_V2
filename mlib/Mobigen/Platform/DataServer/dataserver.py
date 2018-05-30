#!/usr/bin/env python
# encoding: utf-8
"""
dataserver.py

Copyright (c) 2012 Mobigen. All rights reserved.
"""

import os
import sys
import ConfigParser
import Handler as Handle
import Cache.CacheCleaner as CacheCleaner
import Cache.CacheDump as CacheDump
import Mobigen.Common.Log as Log; Log.Init()

def main() :
	
	# load config
	conf = ConfigParser.ConfigParser()
	conf.read("Config/dataserver.cnf")
	
	cachePath = conf.get("dataserver", "cache_path")
	if (not os.path.exists(cachePath)) :
		try : os.makedirs(cachePath)
		except : __LOG__.Exception(); return
		
	dumpPath = conf.get("dataserver", "dump_path")
	if (not os.path.exists(dumpPath)) :
		try : os.makedirs(dumpPath)
		except : __LOG__.Exception(); return

	from Modules.Process import writePid
	pid_file = os.path.join(conf.get("dataserver", "root_path"), \
		os.path.basename(sys.argv[0])[:-3])
	if (writePid(pid_file) == False) :
		print "dataserver is already running."
		return

	if (conf.has_option("dataserver", "log_path")) :
		log_file = os.path.join(conf.get("dataserver", "log_path"), \
			os.path.basename(sys.argv[0])[:-3] + ".log")
	else :
		log_file = os.path.join(conf.get("dataserver", "root_path"), \
			"log", os.path.basename(sys.argv[0])[:-3] + ".log")
	
	Log.Init(Log.CRotatingLog(log_file, 1000000, 10))

	__LOG__.Trace("--------------------------------------")
	__LOG__.Trace(" DATA SERVER START..")
	__LOG__.Trace("--------------------------------------")

	client_port = conf.getint("dataserver", "client_port")
	master_port = conf.getint("dataserver", "master_port")

	__LOG__.Trace("Service port %d." % client_port)
	__LOG__.Trace("Master  port %d." % master_port)

	thread_list = []

	thread_list.append(Handle.startC(client_port, conf))
	thread_list.append(Handle.startM(master_port, conf))
	thread_list.append(CacheCleaner.start(conf))
	thread_list.append(CacheDump.start(conf))

	for thread in thread_list :
		thread.setDaemon(True)
		thread.start()

	try :
		for thread in thread_list :
			thread.join()
	except :
		__LOG__.Exception()

if __name__ == "__main__" :
	main()
