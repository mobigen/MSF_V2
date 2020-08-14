#!/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

try:
	import ConfigParser
except:
	import configparser as ConfigParser

PROC_NAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]

from lib.interface.iworker import iworker

from lib.handler.spider import SpiderHandler
from lib.handler.spider import SpiderRunner
from lib.handler.parser import ParserHandler
from lib.handler.result import ResultHandler
from lib.handler.management import ManagementHandler
from lib.handler.schedule import ScheduleHandler
from lib.handler.log import LogHandler


class Worker(iworker):
	def start(self):
		__LOG__.Trace("Worker : Start")

		if self.conf.has_option(self.section, 'handler_type'):
			type = self.conf.get(self.section, 'handler_type')

			if type.lower() == 'spider':
				self.handler = SpiderHandler(self)
				self.handler.start()
				if self.conf.has_option(self.section, 'spiders'):
					for spider_name in self.conf.get(self.section, 'spiders').split(','):
						s_rnr = SpiderRunner(self.handler, spider_name)
						self.handler.spider_runners.append(s_rnr)
					SpiderRunner.start(self.handler)
			elif type.lower() == 'result':
				self.handler = ResultHandler(self)
				self.handler.start()
				pass
			elif type.lower() == 'parser':
				self.handler = ParserHandler(self)
				self.handler.start()
				pass
			elif type.lower() == 'management':
				self.handler = ManagementHandler(self)
				self.handler.start()
				pass
			elif type.lower() == 'schedule':
				self.handler = ScheduleHandler(self)
				self.handler.start()
				pass
			elif type.lower() == 'log':
				self.handler = LogHandler(self)
				self.handler.start()
				pass

		while self.handler.isruning:
			time.sleep(10)
		__LOG__.Trace("Worker : Stop")


def main():
	if len(sys.argv) < 3:
		sys.stderr.write('Usage : %s conf_file section' % PROC_NAME)
		sys.stderr.flush()
		return

	conf_file = sys.argv[1]
	section = sys.argv[2]

	conf = ConfigParser.ConfigParser()
	conf.read(conf_file)

	log_path = conf.get('GENERAL', 'LOG_PATH')

	if not os.path.exists(log_path):
		try:
			os.makedirs(log_path)
		except:
			pass

	type = 'handler'
	if conf.has_option(section, 'handler_type'):
		type = conf.get(section, 'handler_type')

	log_name = '%s_%s_%s.log' % (PROC_NAME, type, section)
	log_file = os.path.join(log_path, log_name)

	mlib_path = None
	if conf.has_option('GENERAL', 'MLIB_PATH'):
		mlib_path = conf.get('GENERAL', 'MLIB_PATH')

	if mlib_path:
		sys.path.insert(0, mlib_path)
	try:
		import Mobigen.Common.Log as Log
	except:
		raise Exception('Can not import Mobigen.Common.Log')

	log = Log.Init(Log.CRotatingLog(log_file, 10240000, 9))

	Worker(log=__LOG__, conf=conf, section=section).start()


if __name__ == "__main__":
	main()
