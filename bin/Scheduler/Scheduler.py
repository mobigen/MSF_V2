#!/usr/bin/env python
#-*- coding:utf-8 -*-

import re
import os
import sys
import time
import signal
import ConfigParser
import logging

import Mobigen.Common.Log as Log

from apscheduler.scheduler import Scheduler

#logging.basicConfig()

SHUTDOWN = False

def shutdown(signum=0, frame=0) :
		global SHUTDOWN
		SHUTDOWN = True

		signal.signal(signal.SIGTERM, shutdown)  # Sig Terminate : 15
		signal.signal(signal.SIGINT, shutdown)	 # Sig Inturrupt : 2
		signal.signal(signal.SIGHUP, shutdown)	# Sig HangUp : 1
		signal.signal(signal.SIGPIPE, shutdown)	# Sig Broken Pipe : 13


def main() :
		cfg = ConfigParser.ConfigParser()
		cfg.read(sys.argv[2])
		log_dir = cfg.get("GENERAL","LOG_DIR")
		log_name= os.path.join(log_dir,str(os.path.basename(sys.argv[0])))+"_"+sys.argv[1]+".log"
		Log.Init(Log.CRotatingLog(log_name, 1000000, 9))
		__LOG__.Trace("=============================================================")
		__LOG__.Trace("		  Module start")
		__LOG__.Trace("=============================================================")

		time_list = config(cfg)
		scheduler(time_list)
		while True :
				try :
						time.sleep(10)
				except :
						__LOG__.Exception()
						break


def config(cfg) :
		cfg.read(sys.argv[2])
		sec = sys.argv[1]
		time_list=[]
		time_list.append(cfg.get(sec,'YEAR'))
		time_list.append(cfg.get(sec,'MONTH'))
		time_list.append(cfg.get(sec,'DAY'))
		time_list.append(cfg.get(sec,'WEEK'))
		time_list.append(cfg.get(sec,'DAY_OF_WEEK'))
		time_list.append(cfg.get(sec,'HOUR'))
		time_list.append(cfg.get(sec,'MINUTE'))
		time_list.append(cfg.get(sec,'SECOND'))
		for i in range(len(time_list)) :
				if time_list[i] == '' :
						time_list.pop(i)
						time_list.insert(i,None)
		return time_list


def scheduler(time_list):
		sched = Scheduler()
		sched.start()

		sched.add_cron_job(printTime,
												year			= time_list[0],
												month	   = time_list[1],
												day					 = time_list[2],
												week			= time_list[3],
												day_of_week = time_list[4],
												hour			= time_list[5],
												minute		  = time_list[6],
												second		  = time_list[7],
												)
		time.sleep(5)

def printTime() :
		cfg = ConfigParser.ConfigParser()
		cfg.read(sys.argv[2])
		sec = sys.argv[1]
		output = cfg.get(sec,'OUTPUT')
		out_str = time.strftime(output, time.localtime(time.time()))
		sys.stdout.write(out_str+"\n")
		sys.stdout.flush()
		__LOG__.Trace("Std Out : %s" %out_str)

if __name__ == "__main__" :
		main()
