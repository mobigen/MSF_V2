from bs4 import BeautifulSoup

from lib.interface.iparser import iparser

import datetime
import os
import sys
import re

from lib.scrapy.exporters import CsvItemExporter, IrisItemExporter, IrisLoadExporter
from lib.scrapy.items import CommonItem, CommonField

from lib.pretreatment.textmine import textmine

import ast


class news_mining(iparser):
	"""
		PARSER NEWS_MINING
	"""
	name = 'NEWS_MINING'

	def __init__(self, *args, **kwargs):
		super(news_mining, self).__init__(*args, **kwargs)

		if self.conf.has_option(self.section, 'output_path'):
			self.output_path = self.conf.get(self.section, 'output_path')
			if not os.path.exists(self.output_path):
				try:
					os.makedirs(self.output_path)
				except:
					pass

			self.output_name = '%s_%s.dat' % (os.path.splitext(os.path.basename(sys.argv[0]))[0], self.name)
			self.exporter.output_filename = os.path.join(self.output_path, self.output_name)

		self.start_pdate = None

	def parse(self, item, *args, **kwargs):
		try:
			tm = textmine.textmine()
			soup = BeautifulSoup(item['body'], 'html.parser')
			text = soup.extract().get_text()

			if self.conf.has_option(self.section, 'exclude_keywords'):
				exclude_keywords = ast.literal_eval(self.conf.get(self.section, 'exclude_keywords'))
				for ex_word in exclude_keywords:
					text = text.replace(ex_word, '')

			tm_result = tm.get(text)
			# item.fields["pdate"] = CommonField()
			# item["pdate"] = datetime.datetime.now().strftime('%Y%m%d%H%M00')

			# if self.start_pdate is None:
			# 	self.start_pdate = item["pdate"]

			# item['body'] = str(item['body']).replace('\n', ' ').strip()

			# item.fields["text"] = CommonField()
			# item["text"] = text.replace('\n', ' ').strip()

			item.fields["top_sentence"] = CommonField()
			item.fields["top_word"] = CommonField()
			item.fields["sentences"] = CommonField()
			item.fields["words"] = CommonField()

			if len(tm_result) > 0 and len(tm_result[0]) > 0:
				item["top_sentence"] = str(tm_result[0][0][2]).replace('\n', ' ').strip()

			if len(tm_result) > 0 and len(tm_result[1]) > 0:
				item["top_word"] = str(tm_result[1][0][0]).replace('\n', ' ').strip()

			if len(tm_result) > 0:
				item["sentences"] = str(tm_result[0]).replace('\n', ' ').strip()
			if len(tm_result) > 1:
				item["words"] = str(tm_result[1]).replace('\n', ' ').strip()

			# self.exporter.fields_to_export = ['uuid', 'domain', 'url', 'keyword', 'top_sentence', 'top_word', 'sentences', 'words', 'text', 'body', 'date', 'section', 'pdate']
			self.exporter.fields_to_export = ['uuid', 'domain', 'url', 'keyword', 'top_sentence', 'top_word', 'sentences', 'words', 'date', 'section']

			yield item

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
