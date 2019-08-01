import Queue
import logging
import time
import sys
import os
import re
import datetime as dt
import traceback
import ConfigParser

from threading import Thread
from logging import handlers
from collections import defaultdict

import API.M6 as M6
from common_info import iris_conn, log_info

from java.nio.charset import StandardCharsets
from org.apache.commons.io import IOUtils
from org.apache.nifi.processor.io import StreamCallback
from org.apache.nifi.processor.io import InputStreamCallback
from org.apache.nifi.processor.io import OutputStreamCallback

def getTracebackStr():
	lines = traceback.format_exc().strip().split('\n')
	rl = [lines[-1]]
	lines = lines[1:-1]
	lines.reverse()
	nstr = ''
	for i in range(len(lines)):
		line = lines[i].strip()
		if line.startswith('File "'):
			eles = lines[i].strip().split('"')
			basename = os.path.basename(eles[1])
			lastdir = os.path.basename(os.path.dirname(eles[1]))
			eles[1] = '%s/%s' % (lastdir,basename)
			rl.append('^\t%s %s' % (nstr,'"'.join(eles)))
			nstr = ''
		else:
			nstr += line
	return '\n'.join(rl)

def exception_decorator(func):
	def wrapper(*args, **kwargs):
		try:
			result = func(*args, **kwargs)
			return result
		except:
			LOG.error(getTracebackStr())
			raise
	return wrapper

def retry_decorator(func):
	def wrapper(*args, **kwargs):
		retry_num = 0
		while True:
			try:
				result=func(*args, **kwargs)
				break
			except Exception:
				LOG.error(getTracebackStr())
				retry_num += 1
				if retry_num == 3:
					raise Exception("Failed retry 3 times")
		return result
	return wrapper

def get_conf(path):
	'''
		ConfigParser -> Dict
		conf_dict[section][option] = conf.get(section, option)
	'''
	conf = ConfigParser.ConfigParser()
	conf.read(path)
	conf_dict = {}
	for section in conf.sections():
		if section in conf_dict.keys():
			LOG.error("Duplicated section names: %s" % section)
		conf_dict[section] = dict()
		for option in conf.options(section):
			conf_dict[section][option.lower()] = conf.get(section, option)

	return conf_dict

class WriteCallback(OutputStreamCallback):
	def __init__(self, content=None):
		self.content = content
	
	def process(self, out):
		out.write(self.content)

class IrisHandler():
	def __init__(self, ip, port, user, pwd, db, timeout, direct=False):
		self.conn = False
		self.cursor = False
		self.colname_dict = {}
		self.field_sep = ','
		self.record_sep ='\n'
		self.ip = ip
		self.port = port
		self.user = user
		self.pwd = pwd
		self.db = db
		self.direct=direct
		self.timeout = int(timeout)
		self.host = "%s:%s" % (str(ip), str(port))

	@retry_decorator
	def connect(self, host, user, pwd, direct, db):
		LOG.info('%s %s %s %s %s' % (host, user, pwd, str(direct), db))
		self.conn = M6.Connection(host, str(user), str(pwd), Direct=direct, Database=str(db))
		self.cursor = self.conn.Cursor()
		self.cursor.SetFieldSep(str(self.field_sep))
		self.cursor.SetRecordSep(str(self.record_sep))
		self.cursor.SetTimeout(self.timeout)

	def disconnect():
		self.cursor.Close()
		self.conn.close()

	def set_tblnick(self, tblnick):
		self.tblnick = tblnick

	@retry_decorator
	def select(self, sql):
		self.connect(self.host, self.user, self.pwd, self.direct, self.db)
		self.cursor.Execute2(sql)
		for i, colname in enumerate(self.cursor.Metadata()['ColumnName']):
			colname_with_tbl = "%s.%s" % (self.tblnick, colname.lower())
			self.colname_dict[colname_with_tbl] = i

class QueryParser():
	def __init__(self):
		pass

	def parsing(self, query):
		p = re.compile('\s+')
		self.p_select = re.compile('select\s+(.+?)\s+from\s+')
		self.p_from = re.compile('\s+from\s+(.+?)\s+(inner join|left outer join|union)')
		self.query = p.sub(' ', query).lower()
		self.selparam_dict = self.get_selparam_dict()
		self.fromparam = self.evaluate_from()
		self.joinparam = self.evaluate_join()	

	@exception_decorator
	def get_selparam_dict(self):
		selparam_dict = {}
		selparam_list = self.p_select.findall(self.query)[0].split(',')
		for x in selparam_list:
			if len(x.strip().split(' as ')) == 2:
				key, nick = x.strip().split(' as ')
				selparam_dict[key] = nick
			elif len(x.strip().split(' as ')) == 1:
				key = x.strip()
				selparam_dict[key] = key
		return selparam_dict

	def evaluate_select(self, partial_query):
		pass

	@exception_decorator
	def evaluate_from(self):
		return self.p_from.findall(self.query)[0][0].strip()

	@exception_decorator
	def evaluate_join(self):
		t = self.query.split(' %s ' % self.fromparam)[1]
		t = t.replace(';', '')

		join_list = []
		p, i = 0, 0
		while i < len(t):
			if t[i:i+15] == 'left outer join' or t[i:i+10] == 'inner join' or t[i:i+5] == 'union':
				join_list.append(t[p:i].strip())
				p = i
			i += 1
		join_list.append(t[p:i])

		join_order = []
		for x in join_list:
			if x.startswith('left outer join'):
				join_type = 'left outer join'
				join_tblnick = x[15:].split(' on ')[0].strip()
				join_condition = x[15:].split(' on ')[1].split(' and ')
			elif x.startswith('inner join'):
				join_type = 'inner join'
				join_tblnick = x[10:].split(' on ')[0].strip()
				join_condition = x[10:].split(' on ')[1].split(' and ')
			elif x.startswith('union'):
				join_type = 'union'
				join_tblnick = x[5:].split(' from ')[1].strip()
				select_cols = x[5:].split(' select ')[1].split(' from ')[0].strip().split(',')
				for i, x in enumerate(select_cols):
					select_cols[i] = x.strip()
			else:
				continue

			if join_type != 'union':
				transformed = [ [y.strip() for y in x.split('=')] for x in join_condition]
				idx_dict = {}
				for sub_list in transformed:
					for element in sub_list:
						tbl_name, col_name = element.strip().split('.')
						if tbl_name == join_tblnick:
							if tbl_name not in idx_dict:
								idx_dict[tbl_name] = []
							idx_dict[tbl_name].append('%s.%s' % (tbl_name, col_name))
						else:
							if 'REF' not in idx_dict:
								idx_dict['REF'] = []
							idx_dict['REF'].append('%s.%s' % (tbl_name, col_name))
				join_order.append([join_type, join_tblnick, idx_dict])
			else:
				join_order.append([join_type, join_tblnick, select_cols])

		return join_order

def to_set(handler_obj, select_cols = False):
	if select_cols:
		return set([tuple([row[handler_obj.colname_dict[x]] for x in select_cols]) for row in handler_obj.cursor])
	return set([tuple(row) for row in handler_obj])
	

def to_dict(handler_obj, key_cols=False):
	'''
		# Params
		--------
		handler_obj : <Handler object>

		# Return
		--------
		{
			(valX, ... ,valY) : [
									[val11, ... , val1M],
									...
									[valN1, ... , valNM]
								  ],
			...
			
		}
	'''
	key_to_row_dict = defaultdict(lambda: [])

	if key_cols:

		# Retrieve indexes of key columns
		key_idx = [handler_obj.colname_dict[key_col] for key_col in key_cols]
			
		# Concatenate key column values with '|^|'
		for row in handler_obj.cursor:
			key = tuple([str(row[idx]) for idx in key_idx])
			key_to_row_dict[key].append(row)
	else:
		for row in handler_obj.cursor:
			key_to_row_dict[tuple(row)] = row

	return key_to_row_dict

class JoinManager():
	def __init__(self, obj_dict, parser_obj):
		self.obj_dict = obj_dict
		self.parser_obj = parser_obj
		self.process_queue = []
		self.gen_process_queue()
		self.ref_colname_dict = obj_dict[self.parser_obj.fromparam].colname_dict
		
	def gen_process_queue(self):
		for x in self.parser_obj.joinparam:
			self.process_queue.append(x + [self.obj_dict[x[1]]])

	@exception_decorator
	def process(self):
		ref_obj = self.obj_dict[self.parser_obj.fromparam].cursor
		while self.process_queue:
			proc_type, join_tblname, join_dict, handler_obj = self.process_queue.pop(0)

			if proc_type == 'left outer join':
				ref_idxes = [self.ref_colname_dict[key_col] for key_col in join_dict['REF']]
				ref_obj = self.left_outer_join(ref_obj, ref_idxes, to_dict(handler_obj, join_dict[join_tblname]),
										  len(handler_obj.colname_dict))
				for key in handler_obj.colname_dict.keys():
					handler_obj.colname_dict[key] += len(self.ref_colname_dict)
				self.ref_colname_dict = dict(self.ref_colname_dict, **handler_obj.colname_dict)
			elif proc_type == 'inner join':
				ref_idxes = [self.ref_colname_dict[key_col] for key_col in join_dict['REF']]
				ref_obj = self.inner_join(ref_obj, ref_idxes, to_dict(handler_obj, join_dict[join_tblname]))
				for key in handler_obj.colname_dict.keys():
					handler_obj.colname_dict[key] += len(self.ref_colname_dict)
				self.ref_colname_dict = dict(self.ref_colname_dict, **handler_obj.colname_dict)
			elif proc_type == 'union':
				ref_obj = self.union(ref_obj, handler_obj, join_dict)
				
		result = []
		for x in ref_obj:
			result.append([x[self.ref_colname_dict[y]] for y in self.parser_obj.selparam_dict.keys()])

		return result

	@exception_decorator
	def inner_join(self, ref_obj, ref_idxes, join_obj):
		'''
			# Params
			------
				ref_obj: <Object>
				-----------------
			
				join_obj: <dict>
				------------------
				{
					(key1, .. ,keyN) : <row>,
					...
				}


			# Returns : <Object>
			----------------
		'''
		result = []
		for ref_row in ref_obj:
			ref_key = tuple([ref_row[idx] for idx in ref_idxes])
			for join_row in join_obj[ref_key]:
				result.append(ref_row + join_row)
		
		return result

	@exception_decorator
	def left_outer_join(self, ref_obj, ref_idxes, join_obj, join_row_len):
		result = []
		for ref_row in ref_obj:
			ref_key = tuple([ref_row[idx] for idx in ref_idxes])
			if not join_obj[ref_key]:
				# Null Fix
				join_row = [''] * join_row_len
				result.append(list(ref_row) + join_row)
			for join_row in join_obj[ref_key]:
				result.append(list(ref_row) + join_row)
		
		return result

	@exception_decorator
	def union(self, ref_obj, handler_obj, join_dict):
		ref_obj = to_set(ref_obj)
		join_obj = to_set(handler_obj, join_dict)
		return list(ref_obj | join_obj)

@exception_decorator
def get_storage_obj(tblnick, query):
	storage_obj = IrisHandler(**iris_conn)
	storage_obj.set_tblnick(tblnick)
	storage_obj.select(query)

	return storage_obj

@exception_decorator
def main(tblnick_query_dict, join_query, save_path, field_sep):
	que = Queue.Queue()
	thread_list = list()

	for i, tblnick in enumerate(tblnick_query_dict.keys()):
		thread_list.append(Thread(target=lambda q, arg1, arg2: q.put(get_storage_obj(arg1, arg2)), args=(que, tblnick, tblnick_query_dict[tblnick])))
		thread_list[i].start()

	for t in thread_list:
		t.join()

	obj_dict = {}
	while not que.empty():
		obj = que.get()
		obj_dict[obj.tblnick] = obj

	parser_obj = QueryParser()
	parser_obj.parsing(join_query)

	result = JoinManager(obj_dict, parser_obj).process()

	with open(save_path, 'w') as fd:
		for row in result:
			fd.write(field_sep.join(row) + '\n')

	return True
		

flowFile = session.create()
if flowFile != None:
	LOG.info("=== Start ===")

	# Get properties

	# Essential properties which must be listed
	#-------------------------------------------
	properties = ['Script Engine', \
				  'Script File', \
				  'Script Body', \
				  'Module Directory', \
				  'field_sep', \
				  'log_suffix', \
				  'query', \
				  'save_path']

	save_path = str(save_path.evaluateAttributeExpressions(flowFile).value)
	log_suffix = str(log_suffix.evaluateAttributeExpressions(flowFile).value)
	field_sep = str(field_sep)
	query = str(query)
	tblnick_query_dict = {}
	for k, _ in context.getAllProperties().items():
		if k not in properties:
			tblnick_query_dict[k] = eval('%s.evaluateAttributeExpressions(flowFile).value' % k)

	# Get logfile path
	log_name = '%s-%s.log' % (str(context.name), log_suffix)
	log_path = os.path.join(log_info["log_dir"], log_name)

	#------------------------------------------------------------------------------------
	if not os.path.exists(os.path.dirname(log_path)):
		os.makedirs(os.path.dirname(log_path))
	LOG = logging.getLogger('')
	formatter = logging.Formatter(log_info["formatter"])

	LOG.setLevel(logging.DEBUG)
	file_Handler = handlers.RotatingFileHandler(log_path, log_info['mode'], log_info['maxBytes'], log_info['backupCount'])
	file_Handler.setFormatter(formatter)
	if not len(LOG.handlers):
		LOG.addHandler(file_Handler)
	#------------------------------------------------------------------------------------

	try:
		# Set directory of save_path
		if not os.path.exists(os.path.dirname(save_path)):
			os.makedirs(os.path.dirname(save_path))
		
		# Process 
		result = main(tblnick_query_dict, query, save_path, field_sep)

		# Transfer
		flowFile = session.putAttribute(flowFile, 'dat_path', save_path)
		#flowFile = session.write(flowFile, WriteCallback(save_path))
		if result:
			session.transfer(flowFile, REL_SUCCESS)
		else:
			session.transfer(flowFile, REL_FAILURE)
	except Exception, ex:
		LOG.error(getTracebackStr())
		session.transfer(originalFlowFile, REL_FAILURE)
		session.remove(flowFile)
		raise
