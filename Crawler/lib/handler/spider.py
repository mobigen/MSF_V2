import os
import sys
import time
import msgpack

from lib.interface.ihandler import ihandler

from scrapy import spiderloader
from scrapy.crawler import Crawler
from scrapy import signals
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

from twisted.internet import default

import json
from threading import Thread
import datetime

import ast

try:
	import ConfigParser
except:
	import configparser as ConfigParser

import signal
import logging

logger = logging.getLogger(__name__)


class SpiderHandler(ihandler):
	def __init__(self, *args, **kwargs):
		super(SpiderHandler, self).__init__(*args, **kwargs)
		self.setName('SpiderHandler')
		self.spider_conf = None
		self.spider_runners = list()
		if self.parent.conf.has_option(self.parent.section, 'spiders'):
			if self.parent.conf.has_option(self.parent.section, 'config_file') and os.path.exists(self.parent.conf.get(self.parent.section, 'config_file')):
				self.spider_conf = ConfigParser.ConfigParser(interpolation=None)
				self.spider_conf.read(self.parent.conf.get(self.parent.section, 'config_file'))
				self.spider_conf.optionxform = str
			else:
				logger.error("Spider do not have config_file")
			if self.parent.conf.has_option(self.parent.section, 'schedule'):
				self.schedule_info['pattern'] = ast.literal_eval(self.parent.conf.get(self.parent.section, 'schedule'))
		else:
			raise Exception('SPIDER TYPE must have SPIDERS')

	def run(self):
		self.isruning = True
		os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'lib.scrapy.settings')
		self.parent.writeLog(self, "---- SpiderHandler Start ----")
		keep_data = False
		data = b''

		while self.isruning:
			try:
				self.management_info['queue_count'] = self.get_queue_cnt()

				c_alives = [c for c in self.rpc_clients if c.is_connected]
				if len(c_alives) > 0:
					if not keep_data:
						data = self.dequeue()
					if data is not b'':
						# p_msg = msgpack.packb(data, use_bin_type=True)
						send_results = [c for c in c_alives if c.service.put_crawl_result(data) == 'ok']
						if len(send_results) > 0:
							keep_data = False
						else:
							keep_data = True
							time.sleep(1)
							continue
					else:
						time.sleep(1)
						continue
				else:
					time.sleep(1)

			except Exception as ex:
				logger.error("SpiderHandler Exception : %s", str(ex))
				self.parent.writeLog(self, str('Exception -> %s' % ex))
				self.stop_handler()

	def stop_handler(self):
		try:
			SpiderRunner.stop(self)
			self.isruning = False
			self.parent.writeLog(self, "---- SpiderHandler Stop ----")
			self.parent.end()

		except Exception as ex:
			logger.error("SpiderHandler Exception : %s", str(ex))
			pass

	def start_crawl(self):
		try:
			SpiderRunner.start(self)
		except Exception as ex:
			logger.error("SpiderHandler Exception : %s", str(ex))
			return False
		return True

	def stop_crawl(self):
		try:
			SpiderRunner.stop(self)
		except Exception as ex:
			logger.error("SpiderHandler Exception : %s", str(ex))
			return False
		return True


class SpiderRunner:
	def __init__(self, handler: SpiderHandler = None, spider_name: str = '', *args, **kwargs):
		try:
			os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'lib.scrapy.settings')
			self.name = spider_name
			self.handler = handler
			settings = get_project_settings()

			spider_loader = spiderloader.SpiderLoader.from_settings(settings)
			self.spider = Crawler(spider_loader.load(spider_name), settings)
			self.spider.signals.connect(self.engine_started, signal=signals.engine_started)
			self.spider.signals.connect(self.engine_stopped, signal=signals.engine_stopped)
			self.spider.signals.connect(self.spider_opened, signal=signals.spider_opened)
			self.spider.signals.connect(self.spider_closed, signal=signals.spider_closed)
			self.spider.signals.connect(self.spider_error, signal=signals.spider_error)
			self.spider.signals.connect(self.request_dropped, signal=signals.request_dropped)
			self.spider.signals.connect(self.item_scraped, signal=signals.item_scraped)
			self.spider.signals.connect(self.item_error, signal=signals.item_error)
			self.spider.signals.connect(self.item_dropped, signal=signals.item_dropped)
			self.spider.signals.connect(self.item_passed, signal=signals.item_passed)

			self.is_running = False
			self.handler.management_info['spiders'].append({'spider_name': spider_name})
			self.set_default_management_info(spider_name)
			self.management_info['execute_count'] = 0
			configure_logging()

		except Exception as ex:
			logger.error(self, str("---- SpiderRunner %s Err ---- %s" % (self.name, ex)))
			self.handler.parent.writeLog(self, str("---- SpiderRunner %s Err ---- %s" % (self.name, ex)))

	def set_default_management_info(self, spider_name: str = ''):
		self.management_info = next((s for s in self.handler.management_info['spiders'] if s["spider_name"] == spider_name), None)
		if self.management_info:
			self.management_info['item_scraped'] = 0
			self.management_info['item_error'] = 0
			self.management_info['item_dropped'] = 0
			self.management_info['item_passed'] = 0
		pass

	def engine_started(self):
		logger.error("SpiderRunner engine_started")
		try:
			self.spider.spider.runner = self
			if self.spider.spider and hasattr(self.spider.spider, 'engine_started'):
				self.spider.spider.engine_started()

			self.handler.parent.writeLog(self, str("---- Spider %s engine_started ----" % self.name))
			self.management_info['execute_count'] = self.management_info['execute_count'] + 1
			self.management_info['current_starttime'] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
			self.is_running = True
			self.management_info['is_running'] = True
			self.set_default_management_info(self.name)
			pass
		except Exception as ex:
			logger.error("SpiderRunner Exception : %s", str(ex))

	def engine_stopped(self):
		logger.error("SpiderRunner engine_stopped")
		try:
			if self.spider.spider and hasattr(self.spider.spider, 'engine_stopped'):
				self.spider.spider.engine_stopped()
			self.handler.parent.writeLog(self, str("---- Spider %s engine_stopped ----" % self.name))
			self.management_info['current_endtime'] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
			self.is_running = False
			self.management_info['is_running'] = False

			running_spiders = [x for x in self.handler.spider_runners if x.spider.crawling]
			if len(running_spiders) == 0:
				from twisted.internet import reactor
				if reactor.running:
					reactor.stop()
					import sys
					del sys.modules['twisted.internet.reactor']
					from twisted.internet import reactor
					default.install()
			pass
		except Exception as ex:
			logger.error("SpiderRunner Exception : %s", str(ex))

	def spider_opened(self):
		self.handler.parent.writeLog(self, str("---- Spider %s opened ----" % self.name))
		pass

	def spider_closed(self):
		self.handler.parent.writeLog(self, str("---- Spider %s closed ----" % self.name))
		pass

	def spider_error(self, *args, **kwargs):
		self.handler.parent.writeLog(self, str("---- Spider %s Err ----" % self.name))
		SpiderRunner.stop(self.handler)
		pass

	def request_dropped(self, *args, **kwargs):
		pass

	@classmethod
	def start(cls, handler):
		try:
			for sr in handler.spider_runners:
				if not sr.spider.crawling and not sr.is_running:
					try:
						sr.spider.crawl(handler)
					except Exception as ex:
						logger.error("SpiderRunner Exception : %s", str(ex))

			from twisted.internet import reactor

			if not reactor.running:
				cls._thread = Thread(target=reactor.run,
				                     name='spiders_reactor',
				                     kwargs={'installSignalHandlers': False})

				cls._thread.daemon = False
				cls._thread.start()
		except Exception as ex:
			logger.error("SpiderRunner Exception : %s", str(ex))
		pass

	@classmethod
	def stop(cls, handler, spider_name: str = None):
		try:
			if spider_name:
				sr = next((s for s in handler.spider_runners if s.name == spider_name), None)
				if sr and sr.spider.crawling and not sr.is_running:
					sr.spider.engine.crawler.stop()
					sr.is_running = False
					sr.management_info['is_running'] = False
			else:
				for sr in handler.spider_runners:
					if sr and sr.spider.crawling and sr.is_running:
						sr.spider.engine.crawler.stop()
						sr.is_running = False
						sr.management_info['is_running'] = False
		except Exception as ex:
			logger.error("SpiderRunner Exception : %s", str(ex))
		pass

	def item_scraped(self, *args, **kwargs):
		self.management_info['item_scraped'] = self.management_info.get('item_scraped') + 1
		pass

	def item_error(self, *args, **kwargs):
		self.management_info['item_error'] = self.management_info.get('item_error') + 1
		pass

	def item_dropped(self, *args, **kwargs):
		self.management_info['item_dropped'] = self.management_info.get('item_dropped') + 1
		pass

	def item_passed(self, *args, **kwargs):
		self.management_info['item_passed'] = self.management_info.get('item_passed') + 1
		pass
