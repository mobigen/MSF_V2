import os
import time
from lib.interface.ihandler import ihandler
import json
import logging
import croniter
import datetime

logger = logging.getLogger(__name__)


class ScheduleHandler(ihandler):
	def __init__(self, *args, **kwargs):
		super(ScheduleHandler, self).__init__(*args, **kwargs)
		self.setName('ScheduleHandler')

	def run(self):
		self.isruning = True
		self.parent.writeLog(self, "---- ScheduleHandler Start ----")
		while self.isruning:
			try:
				self.rpc_server.service.schedule.handlers = [c.service for c in self.rpc_clients if c.is_connected and c.service.get_schedule_info() is not None]

				if len(self.rpc_server.service.schedule.handlers) > 0:
					for handler in self.rpc_server.service.schedule.handlers:
						type = handler.get_handler_type()
						info = handler.get_schedule_info()
						if type is not None and type.lower() == 'spider' and info is not None:
							schedule_info = info
							if schedule_info.get('pattern'):
								now = datetime.datetime.now()
								last_time = None
								next_time = None
								pass_time = None
								if schedule_info.get('last_schedule'):
									last_time = datetime.datetime.strptime(schedule_info.get('last_schedule'), "%Y%m%d%H%M%S")
								if schedule_info.get('next_schedule'):
									next_time = datetime.datetime.strptime(schedule_info.get('next_schedule'), "%Y%m%d%H%M%S")
								if schedule_info.get('pass_schedule'):
									next_time = datetime.datetime.strptime(schedule_info.get('pass_schedule'), "%Y%m%d%H%M%S")

								if not next_time:
									cron = croniter.croniter(schedule_info['pattern'], now)
									next_time = cron.get_next(datetime.datetime)
									handler.set_schedule_info({'next_schedule': next_time.strftime("%Y%m%d%H%M%S")})
								elif next_time > now:
									handler.set_schedule_info({'next_schedule': next_time.strftime("%Y%m%d%H%M%S")})
								else:
									handler.remove_schedule_info({'pass_schedule': now.strftime("%Y%m%d%H%M%S")})
									handler.set_schedule_info({'last_schedule': next_time.strftime("%Y%m%d%H%M%S")})
									cron = croniter.croniter(schedule_info['pattern'], now)
									next_time = cron.get_next(datetime.datetime)
									handler.stop_crawl()
									handler.start_crawl()
									handler.set_schedule_info({'next_schedule': next_time.strftime("%Y%m%d%H%M%S")})

				time.sleep(1)
			except Exception as ex:
				logger.error("ScheduleHandler Exception : %s", str(ex))
				self.parent.writeLog(self, str('Exception -> %s' % ex))
				self.stop_handler()

	def stop_handler(self):
		try:
			self.isruning = False
			self.parent.writeLog(self, "---- ScheduleHandler Stop ----")
			self.parent.end()

		except Exception as ex:
			return False
		return True
