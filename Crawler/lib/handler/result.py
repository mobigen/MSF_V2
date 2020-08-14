import os
import time
from lib.interface.ihandler import ihandler
import json
import logging
import ast

logger = logging.getLogger(__name__)


class ResultHandler(ihandler):
	def __init__(self, *args, **kwargs):
		super(ResultHandler, self).__init__(*args, **kwargs)
		self.setName('ResultHandler')

		self.is_listen = False
		if self.parent.conf.has_option(self.parent.section, 'is_listen'):
			self.is_listen = ast.literal_eval(self.parent.conf.get(self.parent.section, 'is_listen'))

	def run(self):
		self.isruning = True
		self.parent.writeLog(self, "---- ResultHandler Start ----")
		keep_data = False
		data = b''
		while self.isruning:
			try: 
				self.management_info['queue_count'] = self.get_queue_cnt()
				if self.rpc_server: 
					c_alives = [c for c in self.rpc_clients if c.is_connected]
					if len(c_alives) > 0:
						if not self.is_listen:
							if not keep_data:
								data = self.dequeue()
							if data is not b'':
								send_results = [c for c in c_alives if c.service.put_crawl_result(data) == 'ok']
								if len(send_results) > 0:
									self.management_info['sent_count'] = self.management_info.get('sent_count') + 1
									keep_data = False
								else:
									keep_data = True
									time.sleep(1)
									continue
							else:
								time.sleep(1)
								continue
						else:
							send_results = [c.service.get_crawl_result() for c in c_alives]
							if len(send_results) > 0:
								for data in send_results:
									if data is not None and data is not b'':
										self.enqueue(data)
							else:
								time.sleep(1)
								continue
					else:
						time.sleep(1)
						continue


				else:
					time.sleep(1)



			except Exception as ex:
				logger.error("ResultHandler Exception : %s", str(ex))
				self.parent.writeLog(self, str('Exception -> %s' % ex))
				self.stop_handler()

	def stop_handler(self):
		try:
			self.isruning = False
			self.parent.writeLog(self, "---- ResultHandler Stop ----")
			self.parent.end()

		except Exception as ex:
			return False
		return True
