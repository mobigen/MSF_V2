import datetime
from lib.interface.ispider import ispider
import urllib
from lib.scrapy.request import Request, SeleniumRequest
from lib.scrapy.items import CommonItem, CommonField

from urllib.parse import urlparse
import tldextract
import ast
from shutil import which


class Kotra_AmazonSpider(ispider):
	"""
	Kotra_AmazonSpider
	"""

	name = 'KOTRA_AMAZON'

	custom_settings = {
		'COOKIES_ENABLED': 'True',
		'COOKIES_DEBUG': 'True',
		'SPIDER_MIDDLEWARES': {'lib.scrapy.middlewares.SeleniumMiddleware': 543},
		'DOWNLOADER_MIDDLEWARES': {'lib.scrapy.middlewares.SeleniumMiddleware': 543},
		'SELENIUM_DRIVER_NAME': 'chrome',
		'SELENIUM_DRIVER_EXECUTABLE_PATH': '/home/crawler/crawler/lib/chromedriver_linux64/chromedriver',
		'SELENIUM_DRIVER_ARGUMENTS': ['--headless'],
	}

	def __init__(self, *args, **kwargs):
		super(Kotra_AmazonSpider, self).__init__(*args, **kwargs)

		self.search_url = "https://www.amazon.com/gp/bestsellers/?ref_=nav_cs_bestsellers"
		self.start_urls.append(self.search_url)


	def start_requests(self):
		for url in self.start_urls:
			yield SeleniumRequest(url=url, callback=self.category_parse, dont_filter=True)
			
	def category_parse(self, response):
		for url in response.css('div#zg').css('ul#zg_browseRoot').css('a::attr(href)').getall():
			yield response.follow(url, callback=self.content_parse_50)

	def content_parse_50(self, response):
		try:
			params = {}
			params['pg'] = 2
			query_string = urllib.parse.urlencode(params)
			yield response.follow(url=response.url + "?" + query_string, callback=self.content_parse_100)
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

	def content_parse_100(self, response):
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
