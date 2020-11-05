import scrapy
from scrapy import signals


class ispider(scrapy.Spider):
	def __init__(self, handler, *args, **kwargs):
		super(ispider, self).__init__(*args, **kwargs)
		self.handler = handler
		if self.handler.spider_conf:
			self.conf = self.handler.spider_conf
		self.section = self.handler.parent.section
		self.handler.management_info['spider_err_count'] = 0

	def engine_started(self): 
		pass

	def engine_stopped(self):
		pass

	def start_requests(self):
		raise NotImplementedError("start_requests not Implemented")

	def parse(self, response):
		pass
