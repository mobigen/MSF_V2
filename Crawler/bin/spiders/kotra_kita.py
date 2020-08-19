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


class KotraKita(ispider):
	"""

	"""

	name = 'KOTRA_KITA'

	def __init__(self, *args, **kwargs):
		super(KotraKita, self).__init__(*args, **kwargs)
		self.max_pageIndex = 20
		self.pageUnit = 20

		self.param = {
			"searchOpenYn": "",
			"searchReqType": "SCH",
			"pageIndex": 1,
			"category6CodeId": "",
			"category4CodeId": "",
			"seq": "0",
			"nIndex": "1",
			"check1box": "ALL",
			"check2box": "ALL",
			"check3box": "ALL",
			"check4box": "ALL",
			"category6": "",
			"category7": "",
			"category4": "",
			"category5": "",
			"termDate": "1",
			"startdate": "",
			"enddate": "",
			"dateY": "",
			"searchKeyword": "",
			"orderType": "regOrder",
			"pageUnit": self.pageUnit
		}
		self.content_url = "https://www.kita.net/mberJobSport/bsnsReqstSchdul/cmmrcSportBsnsCldr/cmmrcSportBsnsSchdul/cmmrcSportBsnsSchdulDetail.do"
		self.start_urls = ['https://www.kita.net/mberJobSport/bsnsReqstSchdul/cmmrcSportBsnsCldr/cmmrcSportBsnsSchdul/cmmrcSportBsnsSchdulList.do']
		self.method = 'GET'

	def start_requests(self):
		for url in self.start_urls:
			for i in range(self.max_pageIndex):
				self.param['pageIndex'] = 1 + i
				yield Request(url + (('?' + urllib.parse.urlencode(self.param)) if self.param else ''), self.parse, method=self.method, encoding='utf-8',
				              cb_kwargs={'section': self.section, 'url': url})

	def parse(self, response, section, url):  
		ext = tldextract.extract(urlparse(response.url).netloc)
		domain = ext.registered_domain

		for a in response.css('div.boardList > ul > li > a::attr(href)').getall():
			seq = a.replace("javascript:fn_detail('", "").split(',')[1].replace(")", "")
			param = {
				'seq':seq
			}
			yield response.follow(self.content_url + (('?' + urllib.parse.urlencode(param)) if param else ''), self.parse_content, method=self.method, encoding='utf-8',
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

			item["body"] = response.body

			item.fields["section"] = CommonField()
			item["section"] = section

			yield item
		except Exception as ex:
			pass
