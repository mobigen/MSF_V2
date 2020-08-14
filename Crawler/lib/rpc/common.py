from spyne.application import Application
from spyne.protocol.msgpack import MessagePackRpc
from spyne.service import Service
from spyne.decorator import rpc, srpc
from spyne.model.primitive import Unicode, Any
from spyne.util.appreg import get_application
from spyne.service import ServiceBase
from spyne.protocol.http import HttpRpc
from spyne.protocol.html import HtmlMicroFormat,PrettyFormat
from spyne.protocol.json import JsonDocument

from queue import Queue
import json

from lib.rpc.management import Management
from lib.rpc.schedule import Schedule


class Common(Service):

	@rpc(_returns=Any)
	def check_alive(ctx):
		return True

	@rpc(_returns=Any)
	def get_handler_type(ctx):
		return ctx.service_class.handler.type

	@rpc(_returns=Any)
	def restart_handler(ctx):
		return ctx.service_class.handler.restart()

	@rpc(_returns=Any)
	def get_section(ctx):
		return ctx.service_class.handler.get_section()

	@rpc(_returns=Any)
	def get_handler_id(ctx):
		return ctx.service_class.handler.get_handler_id()

	@rpc(_returns=Any)
	def get_management_info(ctx):
		return ctx.service_class.handler.get_management_info()

	@rpc(Any, _returns=Any)
	def set_management_info(ctx, param):
		return ctx.service_class.handler.get_management_info(param)

	@rpc(_returns=Any)
	def get_schedule_info(ctx):
		return ctx.service_class.handler.get_schedule_info()

	@rpc(Any, _returns=Any)
	def set_schedule_info(ctx, param):
		return ctx.service_class.handler.set_schedule_info(param)

	@rpc(Any, _returns=Any)
	def remove_schedule_info(ctx, param):
		return ctx.service_class.handler.remove_schedule_info(param)

	@rpc(_returns=Any)
	def get_result_count(ctx):
		return ctx.service_class.handler.get_queue_cnt()

	@rpc(Any, _returns=Any)
	def put_crawl_result(ctx, data: object = None):
		result = 'ok'
		try:
			ctx.service_class.handler.enqueue(data) 
		except Exception as ex:
			result = str(ex)
		return result

	@rpc(_returns=Any)
	def get_crawl_result(ctx):
		return ctx.service_class.handler.dequeue()

	@rpc(_returns=Any)
	def stop_handler(ctx):
		return ctx.service_class.handler.stop_handler()

	@rpc(_returns=Any)
	def stop_crawl(ctx):
		return ctx.service_class.handler.stop_crawl()

	@rpc(_returns=Any)
	def start_crawl(ctx):
		return ctx.service_class.handler.start_crawl()


class Management(Service):
	management = Management()

	@rpc(_returns=Any)
	def show_list(ctx): 
		return ctx.service_class.management.get_info(ctx)

	@rpc(_returns=Any)
	def restart_handler(ctx):
		return ctx.service_class.management.restart_handler(ctx)

	@rpc(_returns=Any)
	def stop_crawl(ctx):
		return ctx.service_class.management.stop_crawl(ctx)

	@rpc(_returns=Any)
	def start_crawl(ctx):
		return ctx.service_class.management.start_crawl(ctx)


class Schedule(Service):
	schedule = Schedule()

	@rpc(_returns=Any)
	def show_list(ctx):
		return ctx.service_class.schedule.get_info(ctx)


Schedule = Application(
	[Schedule], name='ScheduleLib',
	tns="MobigenCrawler.rpc",
	in_protocol=HttpRpc(validator='soft'),
	out_protocol=JsonDocument(), )

Management = Application(
	[Management], name='ManagementLib',
	tns="MobigenCrawler.rpc",
	in_protocol=HttpRpc(validator='soft'),
	out_protocol=JsonDocument(), )

Common = Application(
	[Common], name='CommonLib',
	tns="MobigenCrawler.rpc",
	in_protocol=MessagePackRpc(validator="soft"),
	out_protocol=MessagePackRpc()
)
