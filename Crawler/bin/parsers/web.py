from bs4 import BeautifulSoup

from lib.interface.iparser import iparser

import datetime
import os
import sys
import re

from lib.scrapy.exporters import CsvItemExporter, IrisItemExporter, IrisLoadExporter
from lib.scrapy.items import CommonItem, CommonField


class web(iparser):
	"""
		PARSER Sample
	"""
	name = 'WEB'

	def __init__(self, *args, **kwargs):
		super(web, self).__init__(*args, **kwargs)

		if self.conf.has_option(self.section, 'output_path'):
			self.output_path = self.conf.get(self.section, 'output_path')
			if not os.path.exists(self.output_path):
				try:
					os.makedirs(self.output_path)
				except:
					pass

			self.output_name = '%s_%s.dat' % (os.path.splitext(os.path.basename(sys.argv[0]))[0], self.name)
			self.exporter.output_filename = os.path.join(self.output_path, self.output_name)

	def parse(self, item, *args, **kwargs):
		try:
			item.fields["pdate"] = CommonField()
			item["pdate"] = datetime.datetime.now().strftime('%Y%m%d%H%M00')
			item['body'] = re.escape(item['body']) .replace("'", "''").replace(",", " ").replace('\n',' ')

			self.exporter.fields_to_export = ['uuid', 'domain', 'url', 'body', 'date', 'section', 'pdate']
			# self.exporter.insert_query = "INSERT INTO	TB_CRAWLING (UUID,DOMAIN,URL,BODY,DATE,SECTION,PDATE) VALUES ('{uuid}', '{domain}', '{url}', '{body}', '{date}', '{section}', '{pdate}');"
			self.exporter.insert_query = "insert into	tb_crawling (uuid,domain,url,body,date,section,pdate) values ('{uuid}', '{domain}', '{url}', '{body}', '{date}', '{section}', '{pdate}');"
		 
			yield item

		except Exception as ex:
			print(ex)
