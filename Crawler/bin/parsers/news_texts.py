from bs4 import BeautifulSoup

from lib.interface.iparser import iparser

import datetime
import os
import sys
import re
import numpy as np

from lib.scrapy.exporters import CsvItemExporter, IrisItemExporter, IrisLoadExporter
from lib.scrapy.items import CommonItem, CommonField

from lib.pretreatment.textmine import textmine

import ast


class news_mining(iparser):
	"""
		PARSER NEWS_TEXTS
	"""
	name = 'NEWS_TEXTS'

	def __init__(self, *args, **kwargs):
		super(news_mining, self).__init__(*args, **kwargs)
		self.start_pdate = None

	def parse(self, item, *args, **kwargs):
		self.exporter.fields_to_export = ['uuid', 'domain', 'url', 'word', 'word_point', 'date', 'section', 'pdate']
		try:
			tm = textmine.textmine()
			soup = BeautifulSoup(item['body'], 'html.parser')
			text = soup.extract().get_text()

			if self.conf.has_option(self.section, 'exclude_keywords'):
				exclude_keywords = ast.literal_eval(self.conf.get(self.section, 'exclude_keywords'))
				for ex_word in exclude_keywords:
					text = text.replace(ex_word, '')

			tm_result = tm.get(text)

			if len(tm_result) > 0 and len(tm_result[1]) > 0:
				for word in tm_result[1]:
					new_item = CommonItem()
					new_item.fields["uuid"] = CommonField()
					new_item = CommonItem()
					new_item.fields["domain"] = CommonField()
					new_item = CommonItem()
					new_item.fields["url"] = CommonField()
					new_item = CommonItem()
					new_item.fields["word"] = CommonField()
					new_item = CommonItem()
					new_item.fields["word_point"] = CommonField()
					new_item = CommonItem()
					new_item.fields["date"] = CommonField()
					new_item = CommonItem()
					new_item.fields["section"] = CommonField()
					new_item = CommonItem()
					new_item.fields["pdate"] = CommonField()
					new_item["encoding"] = item["encoding"]
					new_item["uuid"] = item["uuid"]
					new_item["domain"] = item["domain"]
					new_item["url"] = item["url"]
					new_item["word"] = word[0]
					new_item["word_point"] = str(word[1])
					new_item["date"] = item["date"]
					new_item["section"] = item["section"]
					new_item["pdate"] = datetime.datetime.now().strftime('%Y%m%d%H%M00')

					if self.start_pdate is None:
						self.start_pdate = new_item["pdate"]

					yield new_item
		except Exception as ex:
			print(ex)

	def close_parser(self):
		if self.exporter:
			self.exporter.finish_exporting()
		self.parser_opened = False
		msg = str('%s %s %s' % (self.name, self.start_pdate, datetime.datetime.now().strftime('%Y%m%d%H%M00')))
		sys.stdout.write(msg + '\n')
		sys.stdout.flush()
		sys.stderr.write(msg + '\n')
		sys.stderr.flush()
		pass
