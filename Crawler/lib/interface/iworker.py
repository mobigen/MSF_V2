import os
import sys
import time
import signal

try:
	import ConfigParser
except:
	import configparser as ConfigParser


class iworker:
	def __init__(self, log: object = None, conf: ConfigParser = None, section: str = ''):
		self.conf = conf
		self.conf.optionxform = str
		self.section = section
		self.log = log

		if self.section is '':
			raise Exception('section is not defined')

		if self.conf:
			if self.conf.has_option(self.section, 'handler_type'):
				self.type = self.conf.get(self.section, 'handler_type')
			else:
				raise Exception('HANDLER_TYPE is not defined')
		else:
			raise Exception('conf is not defined')

		# sigNum 15 : Terminate
		signal.signal(signal.SIGTERM, self.handler)
		# sigNum  2 : Keyboard Interrupt
		signal.signal(signal.SIGINT, self.handler)
		# sigNum  1 : Hangup detected
		try:
			signal.signal(signal.SIGHUP, signal.SIG_IGN)
		except:
			pass
		# sigNum 13 : Broken Pipe
		try:
			signal.signal(signal.SIGPIPE, signal.SIG_IGN)
		except:
			pass

	def handler(self, sigNum, frame):
		self.log.Trace('Catch Signal Number : %s \n' % sigNum)
		sys.stderr.write('Catch Signal Number : %s \n' % sigNum)
		sys.stderr.flush()
		os.kill(os.getpid(), signal.SIGKILL)

	def writeStdOut(self, msg: str = ''):
		sys.stdout.write(msg + '\n')
		sys.stdout.flush()
		self.log.Trace("STD OUT : %s" % (msg))

	def writeStdErr(self, msg: str = ''):
		sys.stderr.write(msg + '\n')
		sys.stderr.flush()
		self.log.Trace("STD ERR : %s" % (msg))

	def writeLog(self, sender: object = None, msg: str = ''):
		self.log.Trace(str('%s : %s ' % (type(sender), msg)))

	def start(self):
		raise NotImplementedError()

	def end(self):
		os.kill(os.getpid(), signal.SIGKILL)
