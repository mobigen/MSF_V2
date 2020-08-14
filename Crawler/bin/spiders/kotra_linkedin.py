from lib.scrapy.request import Request
from scrapy.http import FormRequest
from lib.interface.ispider import ispider
from lib.scrapy.items import CommonItem, CommonField

import datetime

from scrapy.linkextractors import LinkExtractor
import fnmatch
import re
from urllib.parse import urlparse
import tldextract

import ast
import json
import urllib.parse

import logging

logger = logging.getLogger(__name__)


class Kotra_LinkedinSpider(ispider):
	"""
	WebGetSpider CONFIG_FILE에 기술된 URLS을 GET방식으로 Request하고 동일 도메인의 하위 링크가 존재하면 모두 크롤링 합니다(recursive : True).
	"""

	name = 'KOTRA_LINKEDIN'

	def __init__(self, *args, **kwargs):
		super(Kotra_LinkedinSpider, self).__init__(*args, **kwargs)
		self.recursive = False
		self.start_urls = ['https://www.linkedin.com/oauth/v2/accessToken/']
		self.method = 'POST'
		self.param = urllib.parse.urlencode({'grant_type': 'client_credentials', 'client_id': '78we7ll5x9jfgj', 'client_secret': 'SxKzWUXAVnhfDmSR'})
		

	# if self.conf.has_option(self.section, 'urls'):
	# 	self.start_urls = ast.literal_eval(self.conf.get(self.section, 'urls'))
	# if self.conf.has_option(self.section, 'recursive'):
	# 	self.recursive = ast.literal_eval(self.conf.get(self.section, 'recursive'))
	# if self.conf.has_option(self.section, 'method'):
	# 	self.method = ast.literal_eval(self.conf.get(self.section, 'method'))
	# if self.conf.has_option(self.section, 'param'):
	# 	self.param = urllib.parse.urlencode(json.loads(self.conf.get(self.section, 'param')))
	# if self.conf.has_option(self.section, 'sections'):
	# 	self.sections = self.conf.get(self.section, 'sections').split(',')
	#
	# if self.start_urls is None:
	# 	logger.info('start_urls can not be None')
	# 	print('start_urls can not be None')
	# if len(self.start_urls) == 0:
	# 	print('start_urls can not be empty')
	# logger.info('start_urls is %s' % str(self.start_urls))

	def start_requests(self):
		for url in self.start_urls:
			param_sep = '?'
			if '?' in url:
				param_sep = '&'
			yield Request(url + ((param_sep + self.param) if self.param else ''), self.parse, method=self.method)

		 
	def parse(self, response):
		ext = tldextract.extract(urlparse(response.url).netloc)
		domain = ext.registered_domain
		ext = DomainPatternLinkExtractor(domain, canonicalize=True, unique=True)
		urls = [] 

		try:
			ext_domain = tldextract.extract(urlparse(response.url).netloc)
			item = CommonItem()
			item["date"] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
			item["url"] = response.url
			item["domain"] = ext_domain.registered_domain
			item["body"] = response.body

			item.fields["section"] = CommonField()
			item["section"] = section

			yield item
		except Exception as ex:
			pass

 
