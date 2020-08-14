import os
import sys
import time
import threading
from queue import Queue

import datetime
import json
from json import JSONEncoder
import uuid

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from lib.interface.iworker import iworker
from lib.rpc.client import Client
from lib.rpc.server import Server

import inspect

import logging

try:
	import ConfigParser
except:
	import configparser as ConfigParser


class ihandler(threading.Thread):
	def __init__(self, parent: object = None):
		threading.Thread.__init__(self)
		self.id = str(uuid.uuid1())
		loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
		for logger in loggers:
			if 'spyne' in logger.name:
				logger.setLevel(level=logging.ERROR)
			elif 'scrapy' in logger.name:
				logger.setLevel(level=logging.DEBUG)

		assert not issubclass(iworker, type(parent))

		self.parent = parent
		self.isruning = True

		ip = '0.0.0.0'
		port = '0'
		clients_ip = []
		clients_port = []

		self.queue = Queue()

		self.management_info = {}

		self.schedule_info = {}

		self.type = None

		if self.parent and self.parent.conf:
			if self.parent.conf.has_option(self.parent.section, 'ip'):
				ip = self.parent.conf.get(self.parent.section, 'ip')
			if self.parent.conf.has_option(self.parent.section, 'port'):
				port = self.parent.conf.get(self.parent.section, 'port')
			if self.parent.conf.has_option(self.parent.section, 'clients_port'):
				clients_port = self.parent.conf.get(self.parent.section, 'clients_port').split(',')

			if self.parent.conf.has_option(self.parent.section, 'clients_ip'):
				clients_ip = self.parent.conf.get(self.parent.section, 'clients_ip').split(',')
				if len(clients_port) != len(clients_ip):
					raise ValueError('Length is diffrent with CLIENTS_IP and CLIENTS_PORT')
			else:
				for p in range(len(clients_port)):
					clients_ip.append('0.0.0.0')

			if self.parent.conf.has_option(self.parent.section, 'handler_type'):
				self.type = self.parent.conf.get(self.parent.section, 'handler_type')

		else:
			raise Exception('HANDLER_TYPE is not defined')

		clients = list(zip(clients_ip, clients_port))

		self.rpc_clients = []
		self.rpc_server = None

		if port is not '0':
			self.rpc_server = Server(parent=self, ip=ip, port=port)

		for c in clients:
			self.rpc_clients.append(Client(parent=self, ip=c[0], port=c[1]))

		if self.rpc_server:
			self.rpc_server.start()

		if self.type.lower() == 'spider' or self.type.lower() == 'result' or self.type.lower() == 'parser':
			self.management_info.setdefault('queue_count', 0)
		if self.type.lower() == 'spider':
			self.management_info.setdefault('spiders', [])
		if self.type.lower() == 'result':
			self.management_info.setdefault('sent_count', 0)
		if self.type.lower() == 'parser':
			self.management_info.setdefault('export_count', 0)
			self.management_info.setdefault('export_err_count', 0)

		pass

	def run(self):
		self.isruning = True
		raise NotImplementedError()

	def get_handler_info(self):
		info = {}
		info['type'] = self.type
		info['name'] = self.getName()
		info['section'] = self.parent.section
		info['url'] = self.rpc_server.url
		return info

	def get_handler_id(self):
		return self.id

	def get_management_info(self):
		self.management_info.update(self.get_handler_info())
		return self.management_info

	def set_management_info(self, param):
		self.management_info.update(param)

	def get_schedule_info(self):
		self.schedule_info.update(self.get_handler_info())
		return self.schedule_info

	def set_schedule_info(self, param):
		self.schedule_info.update(param)

	def remove_schedule_info(self, param):
		map(self.schedule_info.pop, filter(lambda k: k in param and param[k] == self.schedule_info[k], self.schedule_info))

	def stop_handler(self):
		raise NotImplementedError()

	def enqueue(self, data):
		self.queue.put(data)

	def dequeue(self):
		if self.queue.qsize() > 0:
			return self.queue.get()
		else:
			return b''

	def get_queue_cnt(self):
		return self.queue.qsize()

	def get_section(self):
		return self.parent.section
