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

import json


class kotra_worldbank(iparser):
	"""
		KOTRA의 Worldbank 사이트 크롤링을 위한 PARSER
	"""
	name = 'KOTRA_WORLDBANK'

	def __init__(self, *args, **kwargs):
		super(kotra_worldbank, self).__init__(*args, **kwargs)
		self.gdp_url = self.conf.get(self.section, 'gdp_url')
		self.pop_url = self.conf.get(self.section, 'pop_url')
		self.gdp_res = None
		self.pop_res = None
		self.header_list = [col.strip() for col in self.conf.get(self.section, 'header').split(',')]

	def parse(self, item, *args, **kwargs):
		try:
			item.fields["pdate"] = CommonField()
			item["pdate"] = datetime.datetime.now().strftime('%Y%m%d%H%M00')
			self.data_reg_dt = datetime.datetime.now().strftime('%Y%m%d%H%M00')
			self.exporter.fields_to_export = ['uuid', 'domain', 'url', 'body', 'date', 'section', 'pdate']
			self.exporter.insert_query = "INSERT INTO	TB_CRAWLING (UUID,DOMAIN,URL,BODY,DATE,SECTION,PDATE) VALUES ('{uuid}', '{domain}', '{url}', '{body}', '{date}', '{section}', '{pdate}');"

			if self.gdp_url == item['url'] :
				self.gdp_res = item['body']
			elif self.pop_url == item['url']:
				self.pop_res = item['body']

			if  self.pop_res and self.gdp_res:

				pop_dict = {}

				for dicts in json.loads(self.pop_res)[1]:
					NAT_CD = dicts['country']['id'].strip()
					NAT_NAME = dicts['country']['value'].strip()
					ISO_WD3_NAT_CD = dicts['countryiso3code'].strip()
					BASE_YR = dicts['date'].strip()
					POPLTN_VAL = dicts['value']

					pop_dict.setdefault('|'.join(map(str, [NAT_CD, NAT_NAME, ISO_WD3_NAT_CD])), {}).setdefault(BASE_YR, POPLTN_VAL)

				# print('%s\n' % '|^|'.join(map(str, self.header_list)))
				
				for dicts in json.loads(self.gdp_res)[1]:

					NAT_CD = dicts['country']['id'].strip()
					NAT_NAME = dicts['country']['value'].strip()
					ISO_WD3_NAT_CD = dicts['countryiso3code'].strip()
					BASE_YR = dicts['date'].strip()
					GDP_VAL = dicts['value']

					try:
						POPLTN_VAL = pop_dict['|'.join(map(str, [NAT_CD, NAT_NAME, ISO_WD3_NAT_CD]))][BASE_YR]
					except:
						POPLTN_VAL = ''

					res_line = [NAT_CD, NAT_NAME, ISO_WD3_NAT_CD, BASE_YR, GDP_VAL, POPLTN_VAL, self.data_reg_dt]
					# print('%s\n' % '|^|'.join(map(str, res_line)))

					item['body'] = '%s' % '|^|'.join(map(str, res_line))
					yield item
					del pop_dict['|'.join(map(str, [NAT_CD, NAT_NAME, ISO_WD3_NAT_CD]))][BASE_YR]

				for dicts in pop_dict:
					for BASE_YR in pop_dict[dicts]:
						# __LOG__.Watch(dicts)
						# __LOG__.Watch(BASE_YR)
						# __LOG__.Watch(pop_dict[dicts][BASE_YR])

						POPLTN_VAL = pop_dict[dicts][BASE_YR]
						NAT_CD, NAT_NAME, ISO_WD3_NAT_CD = dicts.split('|')
						GDP_VAL = ''

						res_line = [NAT_CD, NAT_NAME, ISO_WD3_NAT_CD, BASE_YR, GDP_VAL, POPLTN_VAL, self.data_reg_dt]
						# print('%s\n' % '|^|'.join(map(str, res_line)))
						item['body'] = '%s' % '|^|'.join(map(str, res_line))
						yield item
						
				self.gdp_res = None
				self.pop_res = None 

		except Exception as ex:
			print(ex)
