import threading
import time
from lib.scrapy.items import CommonItem, CommonField

import lib.scrapy.exporters as exporters


class iparser(threading.Thread):
	def __init__(self, handler, *args, **kwargs):
		threading.Thread.__init__(self)
		self.handler = handler
		self.conf = None
		if self.handler.parser_conf:
			self.conf = self.handler.parser_conf
		self.section = self.handler.parent.section
		self.exporter = None
		self.exporter_cls = None
		self.parser_opened = False
		if self.conf and 'exporter' in [k.lower() for k, v in self.conf.items(self.section)]:
			md = __import__('lib.scrapy.exporters')
			for ex in dir(md.scrapy.exporters):
				cls = getattr(md.scrapy.exporters, ex)
				if hasattr(cls, 'name'):
					if getattr(cls, 'name').lower() == self.conf.get(self.section, 'exporter').lower():
						self.exporter_cls = cls

		if self.exporter_cls:
			self.handler.management_info['parser_exporter'] = self.conf.get(self.section, 'exporter').lower()
			if self.exporter_cls == exporters.IrisItemExporter:
				conf_list = [k.lower() for k, v in self.conf.items(self.section)]
				self.exporter = self.exporter_cls(conf=self.conf, section=self.section)
			elif self.exporter_cls == exporters.IrisLoadExporter:
				self.exporter = self.exporter_cls(conf=self.conf, section=self.section)
			elif self.exporter_cls == exporters.CsvItemExporter:
				self.exporter = self.exporter_cls(conf=self.conf, section=self.section)
			elif self.exporter_cls == exporters.ElasticSearchExporter:
				self.exporter = self.exporter_cls(conf=self.conf, section=self.section)
			elif self.exporter_cls == exporters.PostgreSqlExporter:
				self.exporter = self.exporter_cls(conf=self.conf, section=self.section)

	def run(self):
		if not self.exporter:
			raise Exception('parser need to define exporter')

		self.isruning = True
		idle_time = 0
		while self.isruning:
			self.handler.management_info['parser_opened'] = self.parser_opened
			if self.handler.get_queue_cnt() > 0:
				idle_time = 0
				if not self.parser_opened:
					self.open_parser()
				data = self.handler.dequeue()
				if data is not b'' and data is not None:
					import msgpack
					u_msg = msgpack.unpackb(data, raw=False)
					item = CommonItem()
					for k, v in u_msg[-1].items():
						if 'fields_info' != v:
							item.fields[v] = CommonField()
							item[v] = u_msg[int(k)]
					if self.exporter:
						try:
							parse_generator = self.parse(item)
							if parse_generator:
								for p in parse_generator:
									self.exporter.export_item(p)
									self.handler.management_info['export_count'] = self.handler.management_info['export_count'] + 1


						except Exception as ex:
							self.handler.management_info['current_exception'] = str(ex)
							self.handler.management_info['export_err_count'] = self.handler.management_info['export_err_count'] + 1

			else:
				idle_time = idle_time + 1
				if idle_time > 60 and self.parser_opened:
					self.close_parser()
				time.sleep(1)

	def open_parser(self):
		if self.exporter:
			self.exporter.start_exporting()
		self.parser_opened = True

		pass

	def parse(self, response):
		raise NotImplementedError("parse not Implemented")

	def close_parser(self):
		if self.exporter:
			self.exporter.finish_exporting()
		self.parser_opened = False
		pass
