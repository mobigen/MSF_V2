from bs4 import BeautifulSoup

from lib.interface.iparser import iparser

import datetime
import os
import sys
import re

from lib.scrapy.exporters import CsvItemExporter, IrisItemExporter, IrisLoadExporter
from lib.scrapy.items import CommonItem, CommonField

from pyquery import PyQuery

import uuid


class kotra_amazon(iparser):
	"""
		Kotra_Amazon Parser
	"""
	name = 'KOTRA_AMAZON'

	def __init__(self, *args, **kwargs):
		super(kotra_amazon, self).__init__(*args, **kwargs)
		# self.exporter.output_filename =  os.path.join(self.conf.get(self.section, 'output_filepath'),datetime.datetime.now().strftime('%Y%m%d%H%M%S1111.dat'))


	def parse(self, item, *args, **kwargs):
		try:
			self.exporter.fields_to_export = ['uuid', 'domain', 'url', 'body', 'date', 'section', 'pdate']
			self.exporter.insert_query = "INSERT INTO	TB_CRAWLING (UUID,DOMAIN,URL,BODY,DATE,SECTION,PDATE) VALUES ('{uuid}', '{domain}', '{url}', '{body}', '{date}', '{section}', '{pdate}');"

			newbody = {}
			soup = BeautifulSoup(item['body'], features="lxml")

			category = soup.select_one('h1.a-size-large.a-spacing-medium.zg-margin-left-15.a-text-bold').extract().get_text()

			cont_items = soup.select('span.aok-inline-block.zg-item')

			for i in cont_items:
				newitem = CommonItem()
				newitem.fields['body'] = CommonField()
				newitem.fields['date'] = CommonField()
				newitem.fields['domain'] = CommonField()
				newitem.fields['spider_name'] = CommonField()
				newitem.fields['url'] = CommonField()
				newitem.fields['uuid'] = CommonField()
				newitem.fields['section'] = CommonField()
				newitem.fields["pdate"] = CommonField()

				title = BeautifulSoup(str(i), features="lxml").select_one('div.p13n-sc-truncate').extract().get_text()
				price = BeautifulSoup(str(i), features="lxml").select_one('span').extract().get_text()
				img = BeautifulSoup(str(i), features="lxml").select_one('img').attrs['src']
				
				newbody['category'] = str(category)
				newbody['title'] = str(title)
				newbody['price'] = str(price)
				newbody['image'] = str(img)

				newitem['body'] = re.escape(str(newbody)).replace("'", " ").replace(",", " ").replace('"', ' ').replace('{', ' ').replace('}', ' ')
				newitem['date'] = item['date']
				newitem['domain'] = item['domain']
				newitem['spider_name'] = item['spider_name']
				newitem['url'] = item['url']
				newitem['uuid'] = str(uuid.uuid1())
				newitem['section'] = item['section']
				newitem['pdate'] = datetime.datetime.now().strftime('%Y%m%d%H%M00')

				yield newitem

		except Exception as ex:
			print(ex)
