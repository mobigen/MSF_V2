import os
import time
from lib.interface.ihandler import ihandler
import json

from lib.scrapy.items import CommonItem, CommonField

try:
	import ConfigParser
except:
	import configparser as ConfigParser

import importlib
import pkgutil
import logging

logger = logging.getLogger(__name__)


class ParserHandler(ihandler):
	def __init__(self, *args, **kwargs):
		super(ParserHandler, self).__init__(*args, **kwargs)
		self.setName('ParserHandler')

		self.parser_conf = None
		if self.parent.conf.has_option(self.parent.section, 'parser'):
			try:
				lib = __import__('bin.parsers')
				md = getattr(lib, 'parsers')
				import os, pkgutil

				for mod in list(module for _, module, _ in pkgutil.iter_modules([md.__path__._path[0]])):
					psr = __import__('bin.parsers.' + mod)
					for attr in dir(getattr(psr.parsers, mod)):
						if hasattr(getattr(getattr(psr.parsers, mod), attr), 'name'):
							if str(getattr(getattr(getattr(psr.parsers, mod), attr), 'name')).lower() == self.parent.conf.get(self.parent.section, 'parser').lower():
								self.parser = getattr(getattr(psr.parsers, mod), attr)

				if self.parent.conf.has_option(self.parent.section, 'config_file') and os.path.exists(self.parent.conf.get(self.parent.section, 'config_file')):
					self.parser_conf = ConfigParser.ConfigParser(interpolation=None)
					self.parser_conf.read(self.parent.conf.get(self.parent.section, 'config_file'))
					self.parser_conf.optionxform = str
				self.parser = self.parser(self)

			except Exception as ex:
				logger.error("ParserHandler Exception : %s", str(ex))
				self.parent.writeLog(self, str('Exception -> %s' % ex))
				self.stop_handler()
		else:
			raise Exception('PARSER Handle must have a PARSER in conf')

	def run(self):
		self.parser.start()
		self.isruning = True
		self.parent.writeLog(self, "---- ParserHandler Start ----")
		while self.isruning:
			try:
				self.management_info['queue_count'] = self.get_queue_cnt()
				if self.rpc_server:
					c_alives = [c for c in self.rpc_clients if c.is_connected]
					if len(c_alives) > 0:
						results = [c.service.get_crawl_result() for c in self.rpc_clients]
						for result in results:
							if result is not b'' and result is not None:
								self.enqueue(result)
						self.management_info['queue_count'] = self.get_queue_cnt()
					else:
						time.sleep(1)
				else:
					time.sleep(1)
			except Exception as ex:
				self.parent.writeLog(self, str('Exception -> %s' % ex))
				self.stop_handler()

	def stop_handler(self):
		try:
			if self.parser:
				self.parser.close()

			self.isruning = False
			self.parent.writeLog(self, "---- ParserHandler Stop ----")
			self.parent.end()

		except Exception as ex:
			return False
		return True
