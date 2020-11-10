import datetime
from lib.interface.ispider import ispider
import urllib
from lib.scrapy.request import Request
from lib.scrapy.items import CommonItem, CommonField

from urllib.parse import urlparse
import tldextract
import ast


class NaverSpider(ispider):
	"""
	NaverSpider 
	"""

	name = 'NAVER'

	def __init__(self, *args, **kwargs):
		super(NaverSpider, self).__init__(*args, **kwargs)
		self.search_url = "https://search.naver.com/search.naver"
		self.where = ''
		self.query = ''
		self.limit_length = 100
		if self.conf.has_option(self.section, 'category'):
			self.where = self.conf.get(self.section, 'category')
		if self.conf.has_option(self.section, 'keywords'):
			self.keywords = ast.literal_eval(self.conf.get(self.section, 'keywords'))
		if self.conf.has_option(self.section, 'limit_length'):
			self.limit_length = self.conf.get(self.section, 'limit_length')

		start = 0
		while (start - 1) * 10 < int(self.limit_length):
			if self.keywords:
				for keyword in self.keywords:
					params = {}
					params['where'] = self.where
					params['query'] = keyword
					params['start'] = start * 10
					query_string = urllib.parse.urlencode(params)
					self.start_urls.append(self.search_url + "?" + query_string)
			start = start + 1

	def start_requests(self): 
		for idx, url in enumerate(self.start_urls):
			keyword = urllib.parse.parse_qs(url)['query'][0]
			yield Request(url, self.parse, cb_kwargs={'keyword': keyword})

	def parse(self, response, keyword):
		for url in response.css('a.news_tit::attr(href)').getall():
			yield response.follow(url, self.content_parse, cb_kwargs={'keyword': keyword})

	def content_parse(self, response, keyword):
		try:
			ext_domain = tldextract.extract(urlparse(response.url).netloc)
			item = CommonItem()
			item["date"] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
			item["url"] = response.url
			item["domain"] = ext_domain.registered_domain
			item["body"] = response.body
			item["encoding"] = response.encoding
			item.fields["section"] = CommonField()
			item["section"] = self.section

			item.fields["keyword"] = CommonField()
			item["keyword"] = keyword

			yield item
		except Exception as ex:
			self.handler.management_info['current_exception'] = str(ex)
			self.handler.management_info['spider_err_count'] = self.handler.management_info['spider_err_count'] + 1
			pass
