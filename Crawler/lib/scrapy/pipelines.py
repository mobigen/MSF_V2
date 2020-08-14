# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from __future__ import unicode_literals
from scrapy.exporters import BaseItemExporter
from scrapy.exporters import JsonItemExporter, CsvItemExporter
from scrapy.utils.python import to_bytes, to_unicode, is_listlike
import sys
import io
import os
import uuid
import datetime
import binascii
import msgpack
from lib.handler.spider import SpiderHandler
from lib.scrapy.items import CommonField
from lib.scrapy.exporters import QueueItemExporter

import logging

logger = logging.getLogger(__name__)


class JsonWriterPipeline(object):
	def open_spider(self, spider):
		file = open(spider.output_filename, 'wb')
		self.file_handle = file
		self.exporter = JsonItemExporter(file)
		self.exporter.start_exporting()

	def close_spider(self, spider):
		self.exporter.finish_exporting()
		self.file_handle.close()

		full_path = os.getcwd() + os.sep + spider.output_filename
		sys.stdout.write(full_path)
		sys.stdout.flush() 

	def process_item(self, item, spider):
		item.setdefault('uuid', str(uuid.uuid1()))
		item.setdefault('date', datetime.datetime.now().strftime("%Y%m%d%H%M"))
		self.exporter.fields_to_export = spider.fields_to_export
		for field in item.keys():
			if field not in self.exporter.fields_to_export:
				self.exporter.fields_to_export.append(field)

		self.exporter.export_item(item)
		return item


class CSVWriterPipeline(object):

	def open_spider(self, spider):
		file = open(spider.output_filename, 'wb')
		self.file_handle = file
		self.exporter = CsvItemExporter(file, delimiter='\t')
		self.exporter.start_exporting()

	def close_spider(self, spider):
		self.exporter.finish_exporting()
		self.file_handle.close()
		full_path = os.getcwd() + os.sep + spider.output_filename
		sys.stdout.write(full_path)
		sys.stdout.flush() 

	def process_item(self, item, spider):
		item.setdefault('uuid', str(uuid.uuid1()))
		item.setdefault('date', datetime.datetime.now().strftime("%Y%m%d%H%M"))
		self.exporter.fields_to_export = spider.fields_to_export
		for field in item.keys():
			if field not in self.exporter.fields_to_export:
				self.exporter.fields_to_export.append(field)
		self.exporter.export_item(item)
		return item


class QueueWriterPipeline(object):

	def open_spider(self, spider):
		self.exporter = QueueItemExporter(delimiter='\t', spider=spider)
		self.exporter.start_exporting()

	def close_spider(self, spider):
		self.exporter.finish_exporting()

	def process_item(self, item, spider):
		item.fields['fields_info'] = CommonField()
		item.fields['uuid'] = CommonField()
		item.fields['spider_name'] = CommonField()
		fields_info = {}
		for idx, val in enumerate(item.fields):
			fields_info.setdefault(str(idx), val)

		item['fields_info'] = fields_info
		item['uuid'] = str(uuid.uuid1())
		item['spider_name'] = str(spider.name)

		self.exporter.fields_to_export = item.fields.keys()
		try :
			self.exporter.export_item(item)
		except Exception as ex:
			logger.error("QueueWriterPipeline Exception : %s", str(ex))

		return item
