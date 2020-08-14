from bs4 import BeautifulSoup

from lib.interface.iparser import iparser

from lib.scrapy.items import CommonItem, CommonField

import datetime

import re


class kotra_kita(iparser):
	"""
		KOTRA의 KITA 사이트 크롤링을 위한 PARSER
	"""

	name = 'KOTRA_KITA'

	def __init__(self, *args, **kwargs):
		super(kotra_kita, self).__init__(*args, **kwargs)
		if self.conf.has_option(self.section, 'sections'):
			self.sections = self.conf.get(self.section, 'sections').split(',')

	def parse(self, item, *args, **kwargs):
		try:
			self.exporter.fields_to_export = ['uuid', 'domain', 'url', 'body', 'date', 'section', 'pdate']
			data_reg_dt = datetime.datetime.now().strftime('%Y%m%d%H%M00')
			iris_prttn = data_reg_dt[:8] + '000000'
			if item['section'] in self.sections:
				reduce_flag = False
				iris_key = 0
				reduce_idx = []
				if self.conf.has_option(item['section'], 'reduce_idx'):
					reduce_idx = self.conf.get(item['section'], 'reduce_idx').split(',')
					reduce_flag = True
				if self.conf.has_option(item['section'], 'iris_key'):
					iris_key = self.conf.get(item['section'], 'iris_key')

				soup = BeautifulSoup(item['body'], 'html.parser')
				row = None
				for tr in soup.select('tr'):
					tmp = [td.text.strip() for td in tr.select('td')]
					if reduce_flag:
						row = [tmp[int(idx)] for idx in reduce_idx] + [iris_key, data_reg_dt]
					else:
						row = tmp + [iris_key, data_reg_dt]
				if row :
					item['body'] =  re.escape(('%s' % '|^|'.join(map(str, row)))).replace("'", " ").replace(",", " ").replace('"', ' ').replace('{', ' ').replace('}', ' ')
					print(item['body'] )
					yield item
		except Exception as ex:
			print(ex)

	def convert_item(self, data):
		item = kitaItem()
		item['uuid'] = data[0]
		item['spider_name'] = data[1]
		item['date'] = data[2]
		item['domain'] = data[3]
		item['url'] = data[4]
		item['body'] = data[5]
		return item


class kitaItem(CommonItem):
	section = CommonField()
