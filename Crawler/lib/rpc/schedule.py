from spyne.decorator import rpc, srpc
from spyne.model.primitive import Unicode, Any
import json
import logging

logger = logging.getLogger(__name__)


class Schedule:

	def __init__(self, handler=None, *args, **kwargs):
		self.handlers = []

	def get_info(self, ctx):
		result = None
		try:
			schedule_info = []
			infos = [c.get_schedule_info() for c in self.handlers if c.get_schedule_info() is not None]
			for info in infos:
				if info.get('pattern'):
					schedule_info.append(info)

			result = {'schedule_handlers': schedule_info}
		except Exception as ex:
			logger.error("RPC Schedule Exception : %s", str(ex))
			return False
		return result

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
