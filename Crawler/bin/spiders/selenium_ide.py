import datetime
from lib.interface.ispider import ispider
import urllib
from lib.scrapy.request import Request, SeleniumIDERequest
from lib.scrapy.items import CommonItem, CommonField

from urllib.parse import urlparse
import tldextract
import ast
from shutil import which

import importlib
import importlib.util
import os

from importlib.machinery import SourceFileLoader


class Selenium_IDE(ispider):
	"""
	SELENIUM IDE Export Script 호출을 위한 SPIDER
	"""

	name = 'SELENIUM_IDE'
	#
	custom_settings = {
		'COOKIES_ENABLED': 'True',
		'COOKIES_DEBUG': 'True',
		'DOWNLOADER_MIDDLEWARES': {'lib.scrapy.middlewares.SeleniumIDEMiddleware': 543},
		'SELENIUM_DRIVER_NAME': 'chrome',
		'SELENIUM_DRIVER_EXECUTABLE_PATH': '/home/mlib/crawler/lib/chromedriver_linux64/chromedriver',
		'SELENIUM_DRIVER_ARGUMENTS': ['--headless'],
	}

	def __init__(self, *args, **kwargs): 
		super(Selenium_IDE, self).__init__(*args, **kwargs)
		modules = ast.literal_eval(self.conf.get(self.section, 'modules'))
		for mod_path in modules:   
			self.start_urls.append(mod_path)

	def start_requests(self): 
		for idx, url in enumerate(self.start_urls):
			try:
				# yield url, self.parse
				ide_function = None
				md_path, md_file = os.path.split(url)
				md_name, md_ext = os.path.splitext(md_file)
				mod = SourceFileLoader(md_name, url).load_module()
				for cls_nm in mod.__dict__:
					if hasattr(getattr(mod, cls_nm), md_name):
						ide_function = getattr(getattr(mod, cls_nm), md_name)

				request = SeleniumIDERequest(ide_function=ide_function, callback=self.parse, url=url)
				yield request
			except Exception as ex:
				print('Error : %s', str(ex))

	def parse(self, response):
		try:
			ext_domain = tldextract.extract(urlparse(response.url).netloc)
			item = CommonItem()
			item["date"] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
			item["url"] = response.url
			item["domain"] = ext_domain.registered_domain
			item["body"] = response.body

			item.fields["section"] = CommonField()
			item["section"] = self.section
			yield item

		except Exception as ex:
			self.handler.management_info['current_exception'] = str(ex)
			self.handler.management_info['spider_err_count'] = self.handler.management_info['spider_err_count'] + 1
			pass
