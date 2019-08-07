import logging
import time
import sys
import os
import traceback
from logging import handlers

from common_info import iris_conn, log_info

from java.nio.charset import StandardCharsets
from org.apache.commons.io import IOUtils
from org.apache.nifi.processor.io import StreamCallback
from org.apache.nifi.processor.io import InputStreamCallback
from org.apache.nifi.processor.io import OutputStreamCallback


def transform_date_to_partition(partition_colval):
	return partition_colval[:10] + str(int(int(partition_colval[10:12]) / 5) * 5).zfill(2) + '00'

originalFlowFile = session.get()

if originalFlowFile != None:
	log.info("=== Start ===")

	# Get properties
	log_dir = log_info['log_dir']
	log_suffix = str(log_suffix)
	
	log_name = '%s-%s.log' % (str(context.name), log_suffix)
	log_path = os.path.join(log_info["log_dir"], log_name)

	# Set Logger ----------------------------------------------------------------------------
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


	# Get attributes
	storage_type = originalFlowFile.getAttribute('storage_type')
	tablename = originalFlowFile.getAttribute('tablename')
	key_colname = originalFlowFile.getAttribute('key_column_name')
	partition_colname = originalFlowFile.getAttribute('partition_column_name')
	save_path = originalFlowFile.getAttribute('save_path')
	field_sep = originalFlowFile.getAttribute('field_seperator')

	# set variables
	dst_path = os.path.join(save_path, storage_type, tablename)

	# Read
	inputStream = session.read(originalFlowFile)
	text_content = IOUtils.toString(inputStream, StandardCharsets.UTF_8)
	inputStream.close()

	# Get Header
	header_text = text_content.split('\n')[0]
	header_cols = header_text.split(field_sep)
	key_index = header_cols.index(key_colname)
	partition_index = header_cols.index(partition_colname)
	
	# Split and Write process
	keypartition_to_file = {}
	flowfile_list = []
	for i, line in enumerate(text_content.split('\n')[1:]):
		try:
			record_vals = line.strip().split(field_sep)
			if len(record_vals) != 1:
				dic_key = record_vals[key_index] + '_' + transform_date_to_partition(record_vals[partition_index])
			elif len(record_vals) != 50 : 
				LOG.error(record_vals)

			ym = record_vals[partition_index][:6]
			if dic_key not in keypartition_to_file.keys():
				last_path = os.path.join(dst_path, ym, dic_key + '.dat')
				if not os.path.exists(os.path.join(dst_path, ym)):
					os.makedirs(os.path.join(dst_path, ym))
				attributes = {}
				attributes['key'] = record_vals[key_index]
				attributes['partition'] = record_vals[partition_index]
				attributes['dat_path'] = last_path
				flowfile_list.append(attributes)
				keypartition_to_file[dic_key] = open(last_path, 'a')

			keypartition_to_file[dic_key].write(line + '\n')
			keypartition_to_file[dic_key].flush()
		except Exception, ex:
			if dic_key in keypartition_to_file:
				keypartition_to_file[dic_key].close()
			LOG.error(ex)
			LOG.info(record_vals)
			LOG.info("Line number : %i" % i)
			raise

	# close df	
	for f in keypartition_to_file:
		keypartition_to_file[f].close()

	flowfiles_list = []
	try:
		for attributes in flowfile_list:
			LOG.info(attributes)
			flowFile = session.create(originalFlowFile)
			if (flowFile != None):
				try:
					flowFile = session.putAttribute(flowFile, 'dat_path', attributes['dat_path'])
					flowFile = session.putAttribute(flowFile, 'key', attributes['key'])
					flowFile = session.putAttribute(flowFile, 'partition', attributes['partition'])
					session.transfer(flowFile, REL_SUCCESS)
				except:
					session.remove(flowFile)
					raise

		session.remove(originalFlowFile)
	except Exception, ex:
		LOG.error(ex)
		session.transfer(originalFlowFile, REL_FAILURE)
		raise
