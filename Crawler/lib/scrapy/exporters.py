import os
import csv
import re
import io
from datetime import datetime, timedelta
import math
import pprint
import marshal
import warnings
import pickle
import msgpack
from xml.sax.saxutils import XMLGenerator
import fs
import fs.copy
from bs4 import BeautifulSoup

from scrapy.utils.serialize import ScrapyJSONEncoder
from scrapy.utils.python import to_bytes, to_unicode, is_listlike
from scrapy.item import BaseItem
from scrapy.exceptions import ScrapyDeprecationWarning

import logging

logger = logging.getLogger(__name__)


class BaseItemExporter:

	def __init__(self, *, dont_fail=False, **kwargs):
		self._kwargs = kwargs
		self._configure(kwargs, dont_fail=dont_fail)

	def _configure(self, options, dont_fail=False):
		"""Configure the exporter by poping options from the ``options`` dict.
		If dont_fail is set, it won't raise an exception on unexpected options
		(useful for using with keyword arguments in subclasses ``__init__`` methods)
		"""
		self.encoding = options.pop('encoding', None)
		self.fields_to_export = options.pop('fields_to_export', None)
		self.export_empty_fields = options.pop('export_empty_fields', False)
		self.indent = options.pop('indent', None)
		if not dont_fail and options:
			raise TypeError("Unexpected options: %s" % ', '.join(options.keys()))

	def export_item(self, item):
		raise NotImplementedError

	def serialize_field(self, field, name, value):
		serializer = field.get('serializer', lambda x: x)
		return serializer(value)

	def start_exporting(self):
		pass

	def finish_exporting(self):
		pass

	def _get_serialized_fields(self, item, default_value=None, include_empty=None):
		"""Return the fields to export as an iterable of tuples
		(name, serialized_value)
		"""
		if include_empty is None:
			include_empty = self.export_empty_fields
		if self.fields_to_export is None:
			if include_empty and not isinstance(item, dict):
				field_iter = item.fields.keys()
			else:
				field_iter = item.keys()
		else:
			if include_empty:
				field_iter = self.fields_to_export
			else:
				field_iter = (x for x in self.fields_to_export if x in item)

		for field_name in field_iter:
			if field_name in item:
				field = {} if isinstance(item, dict) else item.fields[field_name]
				value = self.serialize_field(field, field_name, item[field_name])
			else:
				value = default_value

			yield field_name, value

	def make_pdate(self, _dt, _range):

		year = int((_dt).strftime('%Y%m%d%H%M')[:4])
		month = int((_dt).strftime('%Y%m%d%H%M')[4:6])
		day = int((_dt).strftime('%Y%m%d%H%M')[6:8])
		hour = int((_dt).strftime('%Y%m%d%H%M')[8:10])
		min = int((_dt).strftime('%Y%m%d%H%M')[10:12])

		rang_total_min = _range.total_seconds() / 60
		rang_total_hour = _range.total_seconds() / 60 / 60
		rang_total_day = _range.total_seconds() / 60 / 60 / 24
		rang_total_month = _range.total_seconds() / 60 / 60 / 24 / 30
		rang_total_year = _range.total_seconds() / 60 / 60 / 24 / 365

		try:
			if rang_total_min >= 1 and rang_total_min <= 60:
				tr = math.trunc(min / math.trunc(rang_total_min))
				min = tr * math.trunc(rang_total_min)
			elif rang_total_min > 60:
				min = 0

			if rang_total_hour >= 1 and rang_total_hour <= 24:
				tr = math.trunc(hour / math.trunc(rang_total_hour))
				hour = tr * math.trunc(rang_total_hour)
			elif rang_total_hour > 24:
				hour = 0

			if rang_total_day >= 1 and rang_total_day < 30:
				tr = math.trunc(day / math.trunc(rang_total_day))
				day = tr * math.trunc(rang_total_day)
			elif rang_total_day >= 30:
				day = 1

			if rang_total_month >= 1 and rang_total_month < 12:
				tr = math.trunc(month / math.trunc(rang_total_month))
				month = tr * math.trunc(rang_total_month)
			elif rang_total_month >= 12:
				month = 1

			if rang_total_year >= 1:
				tr = math.trunc(year / math.trunc(rang_total_year))
				year = tr * math.trunc(rang_total_year)

		except Exception as ex:
			print(ex)

		return datetime(year=year, month=month, day=day, hour=hour, minute=min)


class QueueItemExporter(BaseItemExporter):
	def __init__(self, include_headers_line=True, join_multivalued=',', spider=None, **kwargs):
		super().__init__(dont_fail=True, **kwargs)
		self.spider = spider
		if not self.encoding:
			self.encoding = 'utf-8'
		self.include_headers_line = include_headers_line
		self._headers_not_written = True
		self._join_multivalued = join_multivalued

	def serialize_field(self, field, name, value):
		serializer = field.get('serializer', self._join_if_needed)
		return serializer(value)

	def _join_if_needed(self, value):
		if isinstance(value, (list, tuple)):
			try:
				return self._join_multivalued.join(value)
			except TypeError:  # list in value may not contain strings
				pass
		return value

	def export_item(self, item):
		if self.spider.runner.is_running:
			if self._headers_not_written:
				self._headers_not_written = True
				self._write_headers_and_set_fields_to_export(item)

			fields = self._get_serialized_fields(item, default_value='',
			                                     include_empty=True)

			values = list(self._build_row(x for _, x in fields))

			p_msg = msgpack.packb(values, use_bin_type=True)

			self.spider.handler.enqueue(p_msg)

	def _build_row(self, values):
		for s in values:
			try:
				yield to_unicode(s, self.encoding, errors='ignore')
			except TypeError:
				yield s

	def _write_headers_and_set_fields_to_export(self, item):
		if self.include_headers_line:
			if not self.fields_to_export:
				if isinstance(item, dict):
					# for dicts try using fields of the first item
					self.fields_to_export = list(item.keys())
				else:
					# use fields declared in Item
					self.fields_to_export = list(item.fields.keys())
			row = list(self._build_row(self.fields_to_export))


class CsvItemExporter(BaseItemExporter):
	name = 'CSV'

	def __init__(self, conf=None, section=None, include_headers_line=True, join_multivalued=',', **kwargs):
		super().__init__(dont_fail=True, **kwargs)
		if not self.encoding:
			self.encoding = 'utf-8'
		self.include_headers_line = include_headers_line

		self._headers_not_written = True
		self._join_multivalued = join_multivalued

		self.conf = conf
		self.section = section
		if self.conf:
			conf_list = [k.lower() for k, v in self.conf.items(self.section)]
			req_conf_list = ['output_filepath']
			set_req = set(req_conf_list)
			set_in = set(conf_list)
			missing = list(sorted(set_req - set_in))
			if len(missing) > 0:
				raise Exception(' %s is missing in config' % missing)
		else:
			raise Exception('CsvItemExporter need config')
		self.output_filename = None

	def start_exporting(self):
		if not self.output_filename:
			output_path = self.conf.get(self.section, 'output_filepath')

			if not os.path.exists(output_path):
				try:
					os.makedirs(output_path)
				except:
					pass
			self.output_filename = os.path.join(output_path, datetime.now().strftime('%Y%m%d%H%M%S.dat'))

		self.file = open(self.output_filename, 'wb')
		self.stream = io.TextIOWrapper(
			self.file,
			line_buffering=False,
			write_through=True,
			encoding=self.encoding,
			newline=''
		)
		self.csv_writer = csv.writer(self.stream)

	def finish_exporting(self):
		self.file.close()

	def serialize_field(self, field, name, value):
		serializer = field.get('serializer', self._join_if_needed)
		return serializer(value)

	def _join_if_needed(self, value):
		if isinstance(value, (list, tuple)):
			try:
				return self._join_multivalued.join(value)
			except TypeError:  # list in value may not contain strings
				pass
		return value

	def export_item(self, item):
		if self._headers_not_written:
			self._headers_not_written = False
			self._write_headers_and_set_fields_to_export(item)

		fields = self._get_serialized_fields(item, default_value='',
		                                     include_empty=True)
		values = list(self._build_row(x for _, x in fields))
		self.csv_writer.writerow(values)

	def _build_row(self, values):
		for s in values:
			try:
				yield to_unicode(s, self.encoding)
			except TypeError:
				yield s

	def _write_headers_and_set_fields_to_export(self, item):
		if self.include_headers_line:
			if not self.fields_to_export:
				if isinstance(item, dict):
					# for dicts try using fields of the first item
					self.fields_to_export = list(item.keys())
				else:
					# use fields declared in Item
					self.fields_to_export = list(item.fields.keys())
			row = list(self._build_row(self.fields_to_export))
			self.csv_writer.writerow(row)


class PickleItemExporter(BaseItemExporter):
	name = 'PICKLE'

	def __init__(self, file, protocol=2, **kwargs):
		super().__init__(**kwargs)
		self.file = file
		self.protocol = protocol

	def export_item(self, item):
		d = dict(self._get_serialized_fields(item))
		pickle.dump(d, self.file, self.protocol)


class JsonItemExporter(BaseItemExporter):
	name = 'JSON'

	def __init__(self, file, **kwargs):
		super().__init__(dont_fail=True, **kwargs)
		self.file = file
		# there is a small difference between the behaviour or JsonItemExporter.indent
		# and ScrapyJSONEncoder.indent. ScrapyJSONEncoder.indent=None is needed to prevent
		# the addition of newlines everywhere
		json_indent = self.indent if self.indent is not None and self.indent > 0 else None
		self._kwargs.setdefault('indent', json_indent)
		self._kwargs.setdefault('ensure_ascii', not self.encoding)
		self.encoder = ScrapyJSONEncoder(**self._kwargs)
		self.first_item = True

	def _beautify_newline(self):
		if self.indent is not None:
			self.file.write(b'\n')

	def start_exporting(self):
		self.file.write(b"[")
		self._beautify_newline()

	def finish_exporting(self):
		self._beautify_newline()
		self.file.write(b"]")

	def export_item(self, item):
		if self.first_item:
			self.first_item = False
		else:
			self.file.write(b',')
			self._beautify_newline()
		itemdict = dict(self._get_serialized_fields(item))
		data = self.encoder.encode(itemdict)
		self.file.write(to_bytes(data, self.encoding))


class XmlItemExporter(BaseItemExporter):
	name = 'XML'

	def __init__(self, file, **kwargs):
		self.item_element = kwargs.pop('item_element', 'item')
		self.root_element = kwargs.pop('root_element', 'items')
		super().__init__(**kwargs)
		if not self.encoding:
			self.encoding = 'utf-8'
		self.xg = XMLGenerator(file, encoding=self.encoding)

	def _beautify_newline(self, new_item=False):
		if self.indent is not None and (self.indent > 0 or new_item):
			self.xg.characters('\n')

	def _beautify_indent(self, depth=1):
		if self.indent:
			self.xg.characters(' ' * self.indent * depth)

	def start_exporting(self):
		self.xg.startDocument()
		self.xg.startElement(self.root_element, {})
		self._beautify_newline(new_item=True)

	def export_item(self, item):
		self._beautify_indent(depth=1)
		self.xg.startElement(self.item_element, {})
		self._beautify_newline()
		for name, value in self._get_serialized_fields(item, default_value=''):
			self._export_xml_field(name, value, depth=2)
		self._beautify_indent(depth=1)
		self.xg.endElement(self.item_element)
		self._beautify_newline(new_item=True)

	def finish_exporting(self):
		self.xg.endElement(self.root_element)
		self.xg.endDocument()

	def _export_xml_field(self, name, serialized_value, depth):
		self._beautify_indent(depth=depth)
		self.xg.startElement(name, {})
		if hasattr(serialized_value, 'items'):
			self._beautify_newline()
			for subname, value in serialized_value.items():
				self._export_xml_field(subname, value, depth=depth + 1)
			self._beautify_indent(depth=depth)
		elif is_listlike(serialized_value):
			self._beautify_newline()
			for value in serialized_value:
				self._export_xml_field('value', value, depth=depth + 1)
			self._beautify_indent(depth=depth)
		elif isinstance(serialized_value, str):
			self.xg.characters(serialized_value)
		else:
			self.xg.characters(str(serialized_value))
		self.xg.endElement(name)
		self._beautify_newline()


class IrisItemExporter(BaseItemExporter):
	name = 'IRIS'



	def __init__(self, conf=None, section=None, insert_query=None, include_headers_line=True, join_multivalued=',', **kwargs):
		super().__init__(dont_fail=True, **kwargs)
		if not self.encoding:
			self.encoding = 'utf-8'
		self.include_headers_line = include_headers_line
		self._headers_not_written = True
		self._join_multivalued = join_multivalued
		self.conf = conf
		self.insert_query = insert_query
		self.section = section
		if self.conf:
			conf_list = [k.lower() for k, v in self.conf.items(self.section)]
			req_conf_list = ['iris_host', 'iris_id', 'iris_passwd', 'iris_database', 'iris_direct']
			set_req = set(req_conf_list)
			set_in = set(conf_list)
			missing = list(sorted(set_req - set_in))
			if len(missing) > 0:
				raise Exception(' %s is missing in config' % missing)
		else:
			raise Exception('IrisItemExporter need config')

		self.fs = None
		self.current_pdt = None
		pass

	def start_exporting(self):
		try:
			import lib.M6 as M6
		except:
			logger.error('IrisLoadExporter can not import M6')
		self.conn = M6.Connection(self.conf.get(self.section, 'iris_host'), self.conf.get(self.section, 'iris_id'), self.conf.get(self.section, 'iris_passwd'),
		                          Direct=True if self.conf.get(self.section, 'iris_direct').upper() is 'TRUE' else False, Database=self.conf.get(self.section, 'iris_database'))
		self.cursor = self.conn.Cursor()

	def finish_exporting(self):
		self.cursor.Close()
		self.conn.close()

	def serialize_field(self, field, name, value):
		serializer = field.get('serializer', self._join_if_needed)
		return serializer(value)

	def _join_if_needed(self, value):
		if isinstance(value, (list, tuple)):
			try:
				return self._join_multivalued.join(value)
			except TypeError:  # list in value may not contain strings
				pass
		return value

	def export_item(self, item):
		try:
			if self._headers_not_written:
				self._headers_not_written = True
				self._write_headers_and_set_fields_to_export(item)

			fields = self._get_serialized_fields(item, default_value='',
			                                     include_empty=True)

			self.insert_query = self.insert_query.format(**item.__dict__['_values'])

			i_rslt = self.cursor.Execute2(to_unicode(self.insert_query, self.encoding, errors='ignore'))
			if '+OK' not in i_rslt:
				logger.error('Inserting row into IRIS Failed')
		except Exception as ex:
			logger.error("IrisItemExporter  Exception : %s", str(ex))

	def _build_row(self, values):
		for s in values:
			try:
				yield to_unicode(s, self.encoding, errors='ignore')
			except TypeError:
				yield s

	def _write_headers_and_set_fields_to_export(self, item):
		if self.include_headers_line:
			if not self.fields_to_export:
				if isinstance(item, dict):
					# for dicts try using fields of the first item
					self.fields_to_export = list(item.keys())
				else:
					# use fields declared in Item
					self.fields_to_export = list(item.fields.keys())
			row = list(self._build_row(self.fields_to_export))


class IrisLoadExporter(BaseItemExporter):
	name = 'IRIS_LOAD' 

	def __init__(self, conf=None, section=None, include_headers_line=True, join_multivalued=',', **kwargs):
		super().__init__(dont_fail=True, **kwargs)
		if not self.encoding:
			self.encoding = 'utf-8'
		self.include_headers_line = include_headers_line
		self._headers_not_written = True
		self._join_multivalued = join_multivalued
		self.conf = conf
		self.section = section
		if self.conf:
			conf_list = [k.lower() for k, v in self.conf.items(self.section)]
			req_conf_list = ['iris_load_ctl_file', 'iris_load_table', 'iris_host', 'iris_id', 'iris_passwd', 'iris_database', 'iris_direct', 'iris_loadingrange', 'iris_partitionrange']
			set_req = set(req_conf_list)
			set_in = set(conf_list)
			missing = list(sorted(set_req - set_in))
			if len(missing) > 0:
				raise Exception(' %s is missing in config' % missing)
		else:
			raise Exception('IrisLoadExporter need config')

		self.fs = None
		self.current_pdt = None
		pass

	def start_exporting(self):
		self.fs = fs.open_fs('mem://')

	def finish_exporting(self):
		while len(self.fs.listdir('/')) > 0:
			self.load_iris()
		self.current_pdt = None
		self.fs.close()

	def serialize_field(self, field, name, value):
		serializer = field.get('serializer', self._join_if_needed)
		return serializer(value)

	def _join_if_needed(self, value):
		if isinstance(value, (list, tuple)):
			try:
				return self._join_multivalued.join(value)
			except TypeError:  # list in value may not contain strings
				pass
		return value

	def load_iris(self):
		try:
			import lib.M6 as M6
		except:
			logger.error('IrisLoadExporter can not import M6')
		conn = M6.Connection(self.conf.get(self.section, 'iris_host'), self.conf.get(self.section, 'iris_id'), self.conf.get(self.section, 'iris_passwd'),
		                     Direct=True if self.conf.get(self.section, 'iris_direct').upper() is 'TRUE' else False, Database=self.conf.get(self.section, 'iris_database'))
		c = conn.Cursor()
		try:
			field_sep = ''
			record_sep = '\n'
			c.SetFieldSep(field_sep)
			c.SetRecordSep(record_sep)
			for csv_file in self.fs.walk.files(filter=['*.csv']):
				file_name = os.path.splitext(os.path.basename(csv_file))[0]
				table_key = file_name.split('^')[0:1][0]
				table_part = file_name.split('^')[1:2][0]

				loadProperty = M6.LoadProperty()
				ctl_file_size = os.path.getsize(self.conf.get(self.section, 'iris_load_ctl_file'))
				data_file_size = len(self.fs.getbytes(csv_file))
				sendMsg = "%s %s,%s,%s,%s,%s,%s\r\n" % (
					"IMPORT", self.conf.get(self.section, 'iris_load_table'), table_key, table_part, ctl_file_size, data_file_size,
					loadProperty.to_str())
				c.sock.SendMessage(sendMsg)

				with open(self.conf.get(self.section, 'iris_load_ctl_file')) as ctl:
					c.sock.SendMessage(ctl.read(ctl_file_size))
				with self.fs.open(csv_file) as reminder_file:
					c.sock.SendMessage(reminder_file.read(data_file_size))
				rst = str('%s  %s' % (csv_file, c.sock.Readline()))
				# logger.error('======>load result - >' +rst)
				if rst.startswith(csv_file + '  +OK SUCCESS.'):
					pass
				else:
					logger.error("Load fail break: %s" % rst)
					self.is_continue = False
					break
				self.fs.remove(csv_file)
		except Exception as ex:
			logger.error("Except: %s" % ex)
		finally:
			c.Close()
			conn.close()

	def export_item(self, item):
		try:
			pdt = self.make_pdate(datetime.now(), timedelta(minutes=int(self.conf.get(self.section, 'iris_loadingrange'))))

			if self._headers_not_written:
				self._headers_not_written = True
				self._write_headers_and_set_fields_to_export(item)

			fields = self._get_serialized_fields(item, default_value='',
			                                     include_empty=True)

			values = list(self._build_row(x for _, x in fields))

			if self.current_pdt is None:
				self.current_pdt = pdt
			fs_file = str('%s^%s.csv' % (self.section, pdt.strftime('%Y%m%d%H%M%S')))

			with self.fs.open(fs_file, 'a+t', encoding='utf-8') as f:
				field_sep = ''
				record_sep = '\n'
				f.write(field_sep.join(values) + record_sep)

			# logger.error('----:->' + fs_file + '  : ' + str(len(self.fs.getbytes(fs_file))))
			if self.current_pdt != pdt:
				self.load_iris()
				self.current_pdt = pdt

		except Exception as ex:
			logger.error("Except: %s" % ex)

	def _build_row(self, values):
		for s in values:
			try:
				yield to_unicode(s, self.encoding)
			except TypeError:
				yield s

	def _write_headers_and_set_fields_to_export(self, item):
		if self.include_headers_line:
			if not self.fields_to_export:
				if isinstance(item, dict):
					# for dicts try using fields of the first item
					self.fields_to_export = list(item.keys())
				else:
					# use fields declared in Item
					self.fields_to_export = list(item.fields.keys())
			row = list(self._build_row(self.fields_to_export))


class ElasticSearchExporter(BaseItemExporter):
	name = 'ELASTICSEARCH' 
	try:
		from elasticsearch import Elasticsearch
	except:
		logger.error('ElasticSearchExporter can not import Elasticsearch')

	def __init__(self, conf=None, section=None, include_headers_line=True, join_multivalued=',', **kwargs):
		super().__init__(dont_fail=True, **kwargs)
		if not self.encoding:
			self.encoding = 'utf-8'

		json_indent = self.indent if self.indent is not None and self.indent > 0 else None
		self._kwargs.setdefault('indent', json_indent)
		self._kwargs.setdefault('ensure_ascii', not self.encoding)
		self.encoder = ScrapyJSONEncoder(**self._kwargs)

		self.conf = conf
		self.section = section
		if self.conf:
			conf_list = [k.lower() for k, v in self.conf.items(self.section)]
			req_conf_list = ['host_ip', 'port', 'index_range']
			set_req = set(req_conf_list)
			set_in = set(conf_list)
			missing = list(sorted(set_req - set_in))
			if len(missing) > 0:
				raise Exception(' %s is missing in config' % missing)
		else:
			raise Exception('ElasticSearchExporter need config')
		self.es = None
		pass

	def start_exporting(self):
		# es = Elasticsearch(
		# 	['localhost:443', 'other_host:443'],
		# 	# turn on SSL
		# 	use_ssl=True,
		# 	# make sure we verify SSL certificates
		# 	verify_certs=True,
		# 	# provide a path to CA certs on disk
		# 	ca_certs='/path/to/CA_certs'

		self.es = Elasticsearch(hosts=str('%s:%s') % (self.conf.get(self.section, 'host_ip'), self.conf.get(self.section, 'port')))

	def finish_exporting(self):
		self.es.close()

	def serialize_field(self, field, name, value):
		serializer = field.get('serializer', self._join_if_needed)
		return serializer(value)

	def _join_if_needed(self, value):
		if isinstance(value, (list, tuple)):
			try:
				return self._join_multivalued.join(value)
			except TypeError:  # list in value may not contain strings
				pass
		return value

	def export_item(self, item):
		try:
			pdt = self.make_pdate(datetime.now(), timedelta(minutes=int(self.conf.get(self.section, 'index_range'))))
			itemdict = dict(self._get_serialized_fields(item))
			data = self.encoder.encode(itemdict)
			self.es.index(index=pdt.strftime('%Y%m%d%H%M%S'), doc_type=item['section'], id=item['uuid'], body=data)
		except Exception as ex:
			logger.error("Except: %s" % ex)

	def _build_row(self, values):
		for s in values:
			try:
				yield to_unicode(s, self.encoding)
			except TypeError:
				yield s


class PostgreSqlExporter(BaseItemExporter):
	name = 'POSTGRESQL'

	try:
		import psycopg2
	except:
		logger.error('PostgreSqlExporter can not import psycopg2')


	def __init__(self, conf=None, section=None, insert_query=None, include_headers_line=True, join_multivalued=',', **kwargs):
		super().__init__(dont_fail=True, **kwargs)
		if not self.encoding:
			self.encoding = 'utf-8'
		self.include_headers_line = include_headers_line
		self._headers_not_written = True
		self._join_multivalued = join_multivalued
		self.conf = conf
		self.insert_query = insert_query
		self.section = section
		if self.conf:
			conf_list = [k.lower() for k, v in self.conf.items(self.section)]
			req_conf_list = ['host_ip', 'port', 'user', 'password', 'database']
			set_req = set(req_conf_list)
			set_in = set(conf_list)
			missing = list(sorted(set_req - set_in))
			if len(missing) > 0:
				raise Exception(' %s is missing in config' % missing)
		else:
			raise Exception('PostgreSqlExporter need config')

		pass

	def start_exporting(self):
		self.conn = psycopg2.connect(user=self.conf.get(self.section, 'user'),
		                             password=self.conf.get(self.section, 'password'),
		                             host=self.conf.get(self.section, 'host_ip'),
		                             port=self.conf.get(self.section, 'port'),
		                             database=self.conf.get(self.section, 'database'), )
		self.cursor = self.conn.cursor()

	def finish_exporting(self):
		if (self.conn):
			self.cursor.close()
			self.conn.close()

	def serialize_field(self, field, name, value):
		serializer = field.get('serializer', self._join_if_needed)
		return serializer(value)

	def _join_if_needed(self, value):
		if isinstance(value, (list, tuple)):
			try:
				return self._join_multivalued.join(value)
			except TypeError:  # list in value may not contain strings
				pass
		return value

	def export_item(self, item):
		try:
			if self._headers_not_written:
				self._headers_not_written = True
				self._write_headers_and_set_fields_to_export(item)

			fields = self._get_serialized_fields(item, default_value='',
			                                     include_empty=True)

			self.insert_query = self.insert_query.format(**item.__dict__['_values'])
			self.cursor.execute(self.insert_query)
			self.conn.commit()

		except Exception as ex:
			logger.error("PostgreSqlExporter Exception : %s", str(ex))

	def _build_row(self, values):
		for s in values:
			try:
				yield to_unicode(s, self.encoding, errors='ignore')
			except TypeError:
				yield s

	def _write_headers_and_set_fields_to_export(self, item):
		if self.include_headers_line:
			if not self.fields_to_export:
				if isinstance(item, dict):
					# for dicts try using fields of the first item
					self.fields_to_export = list(item.keys())
				else:
					# use fields declared in Item
					self.fields_to_export = list(item.fields.keys())
			row = list(self._build_row(self.fields_to_export))
