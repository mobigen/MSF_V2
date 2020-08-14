from spyne.decorator import rpc, srpc
from spyne.model.primitive import Unicode, Any
import json
import logging

logger = logging.getLogger(__name__)


class Management:
	def __init__(self, *args, **kwargs):
		self.handlers = []

	def get_info(self, ctx):
		result = None
		try:
			management_info = [c.get_management_info() for c in self.handlers if c.get_management_info() is not None]
			result = {'management_handlers': management_info}
		except Exception as ex:
			logger.error("RPC Management  Exception : %s", str(ex))
			return False
		return result

	def restart_handler(self, ctx):
		try:
			handlers, results = self.find_handler(ctx)
			for h in handlers:
				h.stop_handler()
			return results
		except Exception as ex:
			logger.error("RPC Management  Exception : %s", str(ex))
			return False

	def start_crawl(self, ctx):
		try:
			handlers, results = self.find_handler(ctx)
			new_result = []
			for i, h in enumerate(handlers):
				if results[i]['type'].lower() == 'spider':
					h.start_crawl()
					new_result.append(results[i])
			return new_result
		except Exception as ex:
			logger.error("RPC Management  Exception : %s", str(ex))
			return False

	def stop_crawl(self, ctx):
		try:
			handlers, results = self.find_handler(ctx)
			new_result =  []
			for i, h in enumerate(handlers):
				if results[i]['type'].lower() == 'spider':
					h.stop_crawl()
					new_result.append(results[i])
			return new_result
		except Exception as ex:
			logger.error("RPC Management  Exception : %s", str(ex))
			return False

	def find_handler(self, ctx):
		shs = self.handlers
		handlers = []
		results = []
		for sh in shs:
			section = sh.get_section()
			type = sh.get_handler_type()
			if ctx.in_body_doc and ctx.in_body_doc.get('section'):
				if section and section.lower() not in ctx.in_body_doc.get('section'):
					continue
			if ctx.in_body_doc and ctx.in_body_doc.get('type'):
				if type and type.lower() not in ctx.in_body_doc.get('type'):
					continue
			if sh:
				r = dict()
				r['section'] = section.lower() if section else ''
				r['type'] = type.lower() if type else ''
				results.append(r)
				handlers.append(sh)

		return handlers, results
