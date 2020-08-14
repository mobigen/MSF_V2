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


class TradeNavi(ispider):
	"""
	WebGetSpider CONFIG_FILE에 기술된 URLS을 GET방식으로 Request하고 동일 도메인의 하위 링크가 존재하면 모두 크롤링 합니다(recursive : True).
	"""

	name = 'KOTRA_TRADENAVI'

	def __init__(self, *args, **kwargs):
		super(TradeNavi, self).__init__(*args, **kwargs)
		self.pageNum = 1
		self.max_pageNum = 10

		self.param = {"idx": "PG0000000586",
		              "listNum": "20",
		              "pageNum": "1",
		              "seq": "",
		              "viewType": "",
		              "orderType": "",
		              "category4": "",
		              "category5": "",
		              "category6": "",
		              "category7": "",
		              "natnCd": "",
		              "schCondition": "ALL",
		              "searchKeyword": "",
		              "check1box": "ALL",
		              "check2box": "ALL",
		              "check3box": "ALL",
		              "startdate": "",
		              "enddate": "",
		              "startdate_job": "",
		              "enddate_job": ""}

		self.start_urls = []
		self.method = 'POST'
		if self.conf.has_option(self.section, 'urls'):
			self.start_urls = ast.literal_eval(self.conf.get(self.section, 'urls'))

	def start_requests(self):
		for url in self.start_urls:
			for i in range(self.max_pageNum):
				self.param['pageNum'] = str(i)
				url = 'http://www.tradenavi.or.kr/CmsWeb/viewPage.req'
				yield Request(url + (('?' + urllib.parse.urlencode(self.param)) if self.param else ''), self.parse, method=self.method, encoding='utf-8',
				              cb_kwargs={'section': self.section, 'url': url})

	def parse(self, response, section, url):
		ext = tldextract.extract(urlparse(response.url).netloc)
		domain = ext.registered_domain
		for tr in response.css('table.boardlist > tbody > tr::attr(onclick)').getall():
			param = urllib.parse.parse_qs(response.url)
			self.param['seq'] = tr.replace("javascript:fncGoView('", "").replace("')", "")
			self.param['listNum'] = param['listNum'][0]
			self.param['pageNum'] = param['pageNum'][0]
			self.param['viewType'] = 'view'
			yield response.follow(url + (('?' + urllib.parse.urlencode(self.param)) if self.param else ''), self.parse_content, method=self.method, encoding='utf-8',
			                      cb_kwargs={'section': self.section, 'url': url})

	def parse_content(self, response, section, url):
		ext = tldextract.extract(urlparse(response.url).netloc)
		domain = ext.registered_domain
		try:
			ext_domain = tldextract.extract(urlparse(response.url).netloc)
			item = CommonItem()
			item["date"] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
			item["url"] = response.url
			item["domain"] = ext_domain.registered_domain

			item["body"] = response.css('div#webContents').getall()[0] if len(response.css('div#webContents').getall()) > 0 else response.body

			item.fields["section"] = CommonField()
			item["section"] = section 

			yield item
		except Exception as ex:
			pass
