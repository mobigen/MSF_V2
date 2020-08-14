# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
try:
	import os
	from scrapy import signals

	import logging
	from collections import defaultdict

	from scrapy.exceptions import NotConfigured
	from scrapy.http import Response
	from scrapy.http.cookies import CookieJar
	from scrapy.utils.python import to_unicode

	from importlib import import_module
	from scrapy.http import HtmlResponse


	from lib.scrapy.request import SeleniumRequest, SeleniumIDERequest
	from lib.scrapy.response import SeleniumResponse

	from importlib.machinery import SourceFileLoader

	logger = logging.getLogger(__name__)
except:
	print('s')


class CommonSpiderMiddleware(object):
	# Not all methods need to be defined. If a method is not defined,
	# scrapy acts as if the spider middleware does not modify the
	# passed objects.

	@classmethod
	def from_crawler(cls, crawler):
		# This method is used by Scrapy to create your spiders.
		s = cls()
		crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
		return s

	def process_spider_input(self, response, spider):
		# Called for each response that goes through the spider
		# middleware and into the spider.

		# Should return None or raise an exception.
		return None

	def process_spider_output(self, response, result, spider):
		# Called with the results returned from the Spider, after
		# it has processed the response.

		# Must return an iterable of Request, dict or Item objects.
		for i in result: 
			yield i

	def process_spider_exception(self, response, exception, spider):
		# Called when a spider or process_spider_input() method
		# (from other spider middleware) raises an exception.

		# Should return either None or an iterable of Response, dict
		# or Item objects.
		pass

	def process_start_requests(self, start_requests, spider):
		# Called with the start requests of the spider, and works
		# similarly to the process_spider_output() method, except
		# that it doesn’t have a response associated.

		# Must return only requests (not items).
		for r in start_requests:
			yield r

	def spider_opened(self, spider):
		spider.logger.info('Spider opened: %s' % spider.name)

	def process_request(self, request, spider):
		if request.meta.get('dont_merge_cookies', False):
			return


class CommonDownloaderMiddleware(object):
	# Not all methods need to be defined. If a method is not defined,
	# scrapy acts as if the downloader middleware does not modify the
	# passed objects.

	@classmethod
	def from_crawler(cls, crawler):
		# This method is used by Scrapy to create your spiders.
		s = cls()
		crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
		return s

	def process_request(self, request, spider):
		# Called for each request that goes through the downloader
		# middleware.

		# Must either:
		# - return None: continue processing this request
		# - or return a Response object
		# - or return a Request object
		# - or raise IgnoreRequest: process_exception() methods of
		#   installed downloader middleware will be called
		return None

	def process_response(self, request, response, spider):
		# Called with the response returned from the downloader.

		# Must either;
		# - return a Response object
		# - return a Request object
		# - or raise IgnoreRequest
		return response

	def process_exception(self, request, exception, spider):
		# Called when a download handler or a process_request()
		# (from other downloader middleware) raises an exception.

		# Must either:
		# - return None: continue processing this exception
		# - return a Response object: stops process_exception() chain
		# - return a Request object: stops process_exception() chain
		pass

	def spider_opened(self, spider):
		spider.logger.info('Spider opened: %s' % spider.name)


class CookiesSpiderMiddleware(object):
	def __init__(self, debug=False):
		self.jars = defaultdict(CookieJar)
		self.debug = debug

	@classmethod
	def from_crawler(cls, crawler):
		# This method is used by Scrapy to create your spiders.
		s = cls()
		crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
		return s

	def process_spider_input(self, response, spider):
		# Called for each response that goes through the spider
		# middleware and into the spider.

		# Should return None or raise an exception.
		return None

	def process_spider_output(self, response, result, spider):
		# Called with the results returned from the Spider, after
		# it has processed the response.

		# Must return an iterable of Request, dict or Item objects.
		for i in result:
			yield i

	def process_spider_exception(self, response, exception, spider):
		# Called when a spider or process_spider_input() method
		# (from other spider middleware) raises an exception.

		# Should return either None or an iterable of Response, dict
		# or Item objects.
		pass

	def process_start_requests(self, start_requests, spider):
		# Called with the start requests of the spider, and works
		# similarly to the process_spider_output() method, except
		# that it doesn’t have a response associated.

		# Must return only requests (not items).
		for request in start_requests:
			cookiejarkey = request.meta.get("cookiejar")
			jar = self.jars[cookiejarkey]
			for cookie in self._get_request_cookies(jar, request):
				jar.set_cookie_if_ok(cookie, request)

			# set Cookie header
			request.headers.pop('Cookie', None)
			jar.add_cookie_header(request)
			self._debug_cookie(request, spider)
			yield request

	def spider_opened(self, spider):
		spider.logger.info('Spider opened: %s' % spider.name)

	def _debug_cookie(self, request, spider):
		if self.debug:
			cl = [to_unicode(c, errors='replace')
			      for c in request.headers.getlist('Cookie')]
			if cl:
				cookies = "\n".join("Cookie: {}\n".format(c) for c in cl)
				msg = "Sending cookies to: {}\n{}".format(request, cookies)
				logger.debug(msg, extra={'spider': spider})

	def _debug_set_cookie(self, response, spider):
		if self.debug:
			cl = [to_unicode(c, errors='replace')
			      for c in response.headers.getlist('Set-Cookie')]
			if cl:
				cookies = "\n".join("Set-Cookie: {}\n".format(c) for c in cl)
				msg = "Received cookies from: {}\n{}".format(response, cookies)
				logger.debug(msg, extra={'spider': spider})

	def _format_cookie(self, cookie, request):
		"""
		Given a dict consisting of cookie components, return its string representation.
		Decode from bytes if necessary.
		"""
		decoded = {}
		for key in ("name", "value", "path", "domain"):
			if not cookie.get(key):
				if key in ("name", "value"):
					msg = "Invalid cookie found in request {}: {} ('{}' is missing)"
					logger.warning(msg.format(request, cookie, key))
					return
				continue
			if isinstance(cookie[key], str):
				decoded[key] = cookie[key]
			else:
				try:
					decoded[key] = cookie[key].decode("utf8")
				except UnicodeDecodeError:
					logger.warning("Non UTF-8 encoded cookie found in request %s: %s",
					               request, cookie)
					decoded[key] = cookie[key].decode("latin1", errors="replace")

		cookie_str = "{}={}".format(decoded.pop("name"), decoded.pop("value"))
		for key, value in decoded.items():  # path, domain
			cookie_str += "; {}={}".format(key.capitalize(), value)
		return cookie_str

	def _get_request_cookies(self, jar, request):
		"""
		Extract cookies from a Request. Values from the `Request.cookies` attribute
		take precedence over values from the `Cookie` request header.
		"""

		def get_cookies_from_header(jar, request):
			cookie_header = request.headers.get("Cookie")
			if not cookie_header:
				return []
			cookie_gen_bytes = (s.strip() for s in cookie_header.split(b";"))
			cookie_list_unicode = []
			for cookie_bytes in cookie_gen_bytes:
				try:
					cookie_unicode = cookie_bytes.decode("utf8")
				except UnicodeDecodeError:
					logger.warning("Non UTF-8 encoded cookie found in request %s: %s",
					               request, cookie_bytes)
					cookie_unicode = cookie_bytes.decode("latin1", errors="replace")
				cookie_list_unicode.append(cookie_unicode)
			response = Response(request.url, headers={"Set-Cookie": cookie_list_unicode})
			return jar.make_cookies(response, request)

		def get_cookies_from_attribute(jar, request):
			if not request.cookies:
				return []
			elif isinstance(request.cookies, dict):
				cookies = ({"name": k, "value": v} for k, v in request.cookies.items())
			else:
				cookies = request.cookies
			formatted = filter(None, (self._format_cookie(c, request) for c in cookies))
			response = Response(request.url, headers={"Set-Cookie": formatted})
			return jar.make_cookies(response, request)

		return get_cookies_from_header(jar, request) + get_cookies_from_attribute(jar, request)


class CookiesDownloaderMiddleware:
	"""This middleware enables working with sites that need cookies"""

	def __init__(self, debug=False):
		self.jars = defaultdict(CookieJar)
		self.debug = debug

	@classmethod
	def from_crawler(cls, crawler):
		if not crawler.settings.getbool('COOKIES_ENABLED'):
			raise NotConfigured
		return cls(crawler.settings.getbool('COOKIES_DEBUG'))

	def process_request(self, request, spider):
		if request.meta.get('dont_merge_cookies', False):
			return

		cookiejarkey = request.meta.get("cookiejar")
		jar = self.jars[cookiejarkey]
		for cookie in self._get_request_cookies(jar, request):
			jar.set_cookie_if_ok(cookie, request)

		# set Cookie header
		request.headers.pop('Cookie', None)
		jar.add_cookie_header(request)
		self._debug_cookie(request, spider)

	def process_response(self, request, response, spider):
		if request.meta.get('dont_merge_cookies', False):
			return response

		# extract cookies from Set-Cookie and drop invalid/expired cookies
		cookiejarkey = request.meta.get("cookiejar")
		jar = self.jars[cookiejarkey]
		jar.extract_cookies(response, request)
		self._debug_set_cookie(response, spider)

		return response

	def _debug_cookie(self, request, spider):
		if self.debug:
			cl = [to_unicode(c, errors='replace')
			      for c in request.headers.getlist('Cookie')]
			if cl:
				cookies = "\n".join("Cookie: {}\n".format(c) for c in cl)
				msg = "Sending cookies to: {}\n{}".format(request, cookies)
				logger.debug(msg, extra={'spider': spider})

	def _debug_set_cookie(self, response, spider):
		if self.debug:
			cl = [to_unicode(c, errors='replace')
			      for c in response.headers.getlist('Set-Cookie')]
			if cl:
				cookies = "\n".join("Set-Cookie: {}\n".format(c) for c in cl)
				msg = "Received cookies from: {}\n{}".format(response, cookies)
				logger.debug(msg, extra={'spider': spider})

	def _format_cookie(self, cookie, request):
		"""
		Given a dict consisting of cookie components, return its string representation.
		Decode from bytes if necessary.
		"""
		decoded = {}
		for key in ("name", "value", "path", "domain"):
			if not cookie.get(key):
				if key in ("name", "value"):
					msg = "Invalid cookie found in request {}: {} ('{}' is missing)"
					logger.warning(msg.format(request, cookie, key))
					return
				continue
			if isinstance(cookie[key], str):
				decoded[key] = cookie[key]
			else:
				try:
					decoded[key] = cookie[key].decode("utf8")
				except UnicodeDecodeError:
					logger.warning("Non UTF-8 encoded cookie found in request %s: %s",
					               request, cookie)
					decoded[key] = cookie[key].decode("latin1", errors="replace")

		cookie_str = "{}={}".format(decoded.pop("name"), decoded.pop("value"))
		for key, value in decoded.items():  # path, domain
			cookie_str += "; {}={}".format(key.capitalize(), value)
		return cookie_str

	def _get_request_cookies(self, jar, request):
		"""
		Extract cookies from a Request. Values from the `Request.cookies` attribute
		take precedence over values from the `Cookie` request header.
		"""

		def get_cookies_from_header(jar, request):
			cookie_header = request.headers.get("Cookie")
			if not cookie_header:
				return []
			cookie_gen_bytes = (s.strip() for s in cookie_header.split(b";"))
			cookie_list_unicode = []
			for cookie_bytes in cookie_gen_bytes:
				try:
					cookie_unicode = cookie_bytes.decode("utf8")
				except UnicodeDecodeError:
					logger.warning("Non UTF-8 encoded cookie found in request %s: %s",
					               request, cookie_bytes)
					cookie_unicode = cookie_bytes.decode("latin1", errors="replace")
				cookie_list_unicode.append(cookie_unicode)
			response = Response(request.url, headers={"Set-Cookie": cookie_list_unicode})
			return jar.make_cookies(response, request)

		def get_cookies_from_attribute(jar, request):
			if not request.cookies:
				return []
			elif isinstance(request.cookies, dict):
				cookies = ({"name": k, "value": v} for k, v in request.cookies.items())
			else:
				cookies = request.cookies
			formatted = filter(None, (self._format_cookie(c, request) for c in cookies))
			response = Response(request.url, headers={"Set-Cookie": formatted})
			return jar.make_cookies(response, request)

		return get_cookies_from_header(jar, request) + get_cookies_from_attribute(jar, request)


class SeleniumMiddleware:

	try:
		from selenium.webdriver.support.ui import WebDriverWait
	except:
		raise Exception('SeleniumMiddleware can not import WebDriverWait')

	"""Scrapy middleware handling the requests using selenium"""

	def __init__(self, driver_name, driver_executable_path, driver_arguments,
	             browser_executable_path):
		"""Initialize the selenium webdriver

		Parameters
		----------
		driver_name: str
			The selenium ``WebDriver`` to use
		driver_executable_path: str
			The path of the executable binary of the driver
		driver_arguments: list
			A list of arguments to initialize the driver
		browser_executable_path: str
			The path of the executable binary of the browser
		"""
		try:
			webdriver_base_path = f'selenium.webdriver.{driver_name}'

			driver_klass_module = import_module(f'{webdriver_base_path}.webdriver')
			driver_klass = getattr(driver_klass_module, 'WebDriver')

			driver_options_module = import_module(f'{webdriver_base_path}.options')
			driver_options_klass = getattr(driver_options_module, 'Options')

			driver_options = driver_options_klass()
			if browser_executable_path:
				driver_options.binary_location = browser_executable_path
			for argument in driver_arguments:
				driver_options.add_argument(argument)

			driver_kwargs = {
				'executable_path': driver_executable_path,
				f'{driver_name}_options': driver_options
			}

			self.driver = driver_klass(**driver_kwargs)
			self.driver.set_page_load_timeout(5)
		except Exception as ex:
			logger.error('SeleniumMiddleware Error: %s' % (str(ex)))

	@classmethod
	def from_crawler(cls, crawler):
		"""Initialize the middleware with the crawler settings"""
		middleware = None
		try:
			driver_name = crawler.settings.get('SELENIUM_DRIVER_NAME')
			driver_executable_path = crawler.settings.get('SELENIUM_DRIVER_EXECUTABLE_PATH')
			browser_executable_path = crawler.settings.get('SELENIUM_BROWSER_EXECUTABLE_PATH')
			driver_arguments = crawler.settings.get('SELENIUM_DRIVER_ARGUMENTS')

			if not driver_name or not driver_executable_path:
				raise NotConfigured(
					'SELENIUM_DRIVER_NAME and SELENIUM_DRIVER_EXECUTABLE_PATH must be set'
				)

			middleware = cls(
				driver_name=driver_name,
				driver_executable_path=driver_executable_path,
				driver_arguments=driver_arguments,
				browser_executable_path=browser_executable_path
			)

			crawler.signals.connect(middleware.spider_closed, signals.spider_closed)

		except Exception as ex:
			logger.error('SeleniumMiddleware Error: %s' % (str(ex)))

		return middleware

	def process_start_requests(self, start_requests, spider):
		# Called with the start requests of the spider, and works
		# similarly to the process_spider_output() method, except
		# that it doesn’t have a response associated.

		# Must return only requests (not items).
		for request in start_requests:
			yield request

	def process_request(self, request, spider):
		"""Process a request using the selenium driver if applicable"""
		res = None
		try:
			if not isinstance(request, SeleniumRequest):
				return None

			self.driver.get(request.url)

			for cookie_name, cookie_value in request.cookies.items():
				self.driver.add_cookie(
					{
						'name': cookie_name,
						'value': cookie_value
					}
				)

			if request.wait_until:
				WebDriverWait(self.driver, request.wait_time).until(
					request.wait_until
				)

			if request.screenshot:
				request.meta['screenshot'] = self.driver.get_screenshot_as_png()

			if request.script:
				self.driver.execute_script(request.script)

			body = str.encode(self.driver.page_source)

			# Expose the driver via the "meta" attribute
			request.meta.update({'driver': self.driver})
			res = SeleniumResponse(
				self.driver.current_url,
				body=body,
				encoding='utf-8',
				driver=self.driver,
				request=request
			)
		except Exception as ex:
			logger.error('SeleniumMiddleware Error: %s - %s' % (spider.name, str(ex)))

		return res

	def process_exception(self, request, spider):
		return None

	def spider_closed(self):
		"""Shutdown the driver when spider is closed"""

		self.driver.quit()


class SeleniumIDEMiddleware:
	"""Scrapy middleware handling the requests using selenium"""

	try:
		from selenium.webdriver.support.ui import WebDriverWait
	except:
		raise Exception('SeleniumMiddleware can not import WebDriverWait')

	def __init__(self, driver_name, driver_executable_path, driver_arguments,
	             browser_executable_path):
		"""Initialize the selenium webdriver

		Parameters
		----------
		driver_name: str
			The selenium ``WebDriver`` to use
		driver_executable_path: str
			The path of the executable binary of the driver
		driver_arguments: list
			A list of arguments to initialize the driver
		browser_executable_path: str
			The path of the executable binary of the browser
		"""
		try:
			webdriver_base_path = f'selenium.webdriver.{driver_name}'

			driver_klass_module = import_module(f'{webdriver_base_path}.webdriver')
			driver_klass = getattr(driver_klass_module, 'WebDriver')

			driver_options_module = import_module(f'{webdriver_base_path}.options')
			driver_options_klass = getattr(driver_options_module, 'Options')

			driver_options = driver_options_klass()
			if browser_executable_path:
				driver_options.binary_location = browser_executable_path
			for argument in driver_arguments:
				driver_options.add_argument(argument)

			driver_kwargs = {
				'executable_path': driver_executable_path,
				f'{driver_name}_options': driver_options
			}

			self.driver = driver_klass(**driver_kwargs)
			self.driver.set_page_load_timeout(5)
		except Exception as ex:
			logger.error('SeleniumIDEMiddleware Error: %s - %s' % (str(ex)))

	@classmethod
	def from_crawler(cls, crawler):
		"""Initialize the middleware with the crawler settings"""
		middleware = None
		try:
			driver_name = crawler.settings.get('SELENIUM_DRIVER_NAME')
			driver_executable_path = crawler.settings.get('SELENIUM_DRIVER_EXECUTABLE_PATH')
			browser_executable_path = crawler.settings.get('SELENIUM_BROWSER_EXECUTABLE_PATH')
			driver_arguments = crawler.settings.get('SELENIUM_DRIVER_ARGUMENTS')

			if not driver_name or not driver_executable_path:
				raise NotConfigured(
					'SELENIUM_DRIVER_NAME and SELENIUM_DRIVER_EXECUTABLE_PATH must be set'
				)

			middleware = cls(
				driver_name=driver_name,
				driver_executable_path=driver_executable_path,
				driver_arguments=driver_arguments,
				browser_executable_path=browser_executable_path
			)

			crawler.signals.connect(middleware.spider_closed, signals.spider_closed)

		except Exception as ex:
			logger.error('SeleniumIDEMiddleware Error: %s' % (str(ex)))
		return middleware

	def process_start_requests(self, start_requests, spider):
		# Called with the start requests of the spider, and works
		# similarly to the process_spider_output() method, except
		# that it doesn’t have a response associated.

		# Must return only requests (not items).

		for r in start_requests:
			if r.ide_function:
				yield r

	def process_request(self, request, spider):
		"""Process a request using the selenium driver if applicable"""
		res = None
		try:
			if not isinstance(request, SeleniumIDERequest):
				return None

			request.ide_function(self)

			for cookie_name, cookie_value in request.cookies.items():
				self.driver.add_cookie(
					{
						'name': cookie_name,
						'value': cookie_value
					}
				)

			if request.wait_until:
				WebDriverWait(self.driver, request.wait_time).until(
					request.wait_until
				)

			if request.screenshot:
				request.meta['screenshot'] = self.driver.get_screenshot_as_png()

			if request.script:
				self.driver.execute_script(request.script)

			body = str.encode(self.driver.page_source)

			# Expose the driver via the "meta" attribute
			request.meta.update({'driver': self.driver})

			res = SeleniumResponse(
				self.driver.current_url,
				body=body,
				encoding='utf-8',
				request=request
			)
		except Exception as ex:
			logger.error('SeleniumMiddleware Error: %s-%s' % (spider.name, str(ex)))

		return res

	def process_exception(self, request, spider):
		return None

	def spider_closed(self):
		"""Shutdown the driver when spider is closed"""

		self.driver.quit()
