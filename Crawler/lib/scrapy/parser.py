from lib.scrapy.items import CommonItem

import datetime
import tldextract
from urllib.parse import urlparse


class CommonParser:
	@classmethod
	def parse(cls, response):
		ext = tldextract.extract(urlparse(response.url).netloc)
		item = CommonItem()
		item.setdefault('date', datetime.datetime.now().strftime("%Y%m%d%H%M"))
		item.setdefault('url',response.url)
		item.setdefault('domain', ext.registered_domain)
		item.setdefault('body', response.body)
		item.setdefault('encoding', response.encoding)
		yield item
