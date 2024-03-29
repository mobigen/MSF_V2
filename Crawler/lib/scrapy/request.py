import uuid

from w3lib.url import safe_url_string

from scrapy.http.headers import Headers
from scrapy.utils.python import to_bytes
from scrapy.utils.trackref import object_ref
from scrapy.utils.url import escape_ajax
from scrapy.http.common import obsolete_setter
from scrapy.utils.curl import curl_to_request_kwargs

from scrapy.http import Request as scrapyReq

from lib.scrapy.parser import CommonParser

import logging

logger = logging.getLogger(__name__)


class Request(scrapyReq):

	def __init__(self, url, callback=None, method='GET', headers=None, body=None,
	             cookies=None, meta=None, encoding='utf-8', priority=0,
	             dont_filter=False, errback=None, flags=None, cb_kwargs=None):

		self._encoding = encoding  # this one has to be set first
		self.method = str(method).upper()
		self._set_url(url)
		self._set_body(body)
		if not isinstance(priority, int):
			raise TypeError("Request priority not an integer: %r" % priority)
		self.priority = priority

		if callback is None:
			callback = CommonParser.parse

		if callback is not None and not callable(callback):
			raise TypeError('callback must be a callable, got %s' % type(callback).__name__)
		if errback is not None and not callable(errback):
			raise TypeError('errback must be a callable, got %s' % type(errback).__name__)
		self.callback = callback
		self.errback = errback

		self.cookies = cookies or {}
		self.headers = Headers(headers or {}, encoding=encoding)
		self.dont_filter = dont_filter

		self._meta = dict(meta) if meta else None
		self._cb_kwargs = dict(cb_kwargs) if cb_kwargs else None
		self.flags = [] if flags is None else list(flags)

	@property
	def cb_kwargs(self):
		if self._cb_kwargs is None:
			self._cb_kwargs = {}
		return self._cb_kwargs

	@property
	def meta(self):
		if self._meta is None:
			self._meta = {}
		return self._meta

	def _get_url(self):
		return self._url

	def _set_url(self, url):
		if not isinstance(url, str):
			raise TypeError('Request url must be str or unicode, got %s:' % type(url).__name__)

		s = safe_url_string(url, self.encoding)
		self._url = escape_ajax(s)

		if ('://' not in self._url) and (not self._url.startswith('data:')):
			raise ValueError('Missing scheme in request url: %s' % self._url)

	url = property(_get_url, obsolete_setter(_set_url, 'url'))

	def _get_body(self):
		return self._body

	def _set_body(self, body):
		if body is None:
			self._body = b''
		else:
			self._body = to_bytes(body, self.encoding)

	body = property(_get_body, obsolete_setter(_set_body, 'body'))

	@property
	def encoding(self):
		return self._encoding

	def __str__(self):
		return "<%s %s>" % (self.method, self.url)

	__repr__ = __str__

	def copy(self):
		"""Return a copy of this Request"""
		return self.replace()

	def replace(self, *args, **kwargs):
		"""Create a new Request with the same attributes except for those
		given new values.
		"""
		for x in ['url', 'method', 'headers', 'body', 'cookies', 'meta', 'flags',
		          'encoding', 'priority', 'dont_filter', 'callback', 'errback', 'cb_kwargs']:
			kwargs.setdefault(x, getattr(self, x))
		cls = kwargs.pop('cls', self.__class__)
		return cls(*args, **kwargs)

	@classmethod
	def from_curl(cls, curl_command, ignore_unknown_options=True, **kwargs):
		"""Create a Request object from a string containing a `cURL
		<https://curl.haxx.se/>`_ command. It populates the HTTP method, the
		URL, the headers, the cookies and the body. It accepts the same
		arguments as the :class:`Request` class, taking preference and
		overriding the values of the same arguments contained in the cURL
		command.

		Unrecognized options are ignored by default. To raise an error when
		finding unknown options call this method by passing
		``ignore_unknown_options=False``.

		.. caution:: Using :meth:`from_curl` from :class:`~scrapy.http.Request`
					 subclasses, such as :class:`~scrapy.http.JSONRequest`, or
					 :class:`~scrapy.http.XmlRpcRequest`, as well as having
					 :ref:`downloader middlewares <topics-downloader-middleware>`
					 and
					 :ref:`spider middlewares <topics-spider-middleware>`
					 enabled, such as
					 :class:`~scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware`,
					 :class:`~scrapy.downloadermiddlewares.useragent.UserAgentMiddleware`,
					 or
					 :class:`~scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware`,
					 may modify the :class:`~scrapy.http.Request` object.

		To translate a cURL command into a Scrapy request,
		you may use `curl2scrapy <https://michael-shub.github.io/curl2scrapy/>`_.

	   """
		request_kwargs = curl_to_request_kwargs(curl_command, ignore_unknown_options)
		request_kwargs.update(kwargs)
		return cls(**request_kwargs)


class SeleniumRequest(Request):
	def __init__(self, wait_time=None, wait_until=None, screenshot=False, script=None, *args, **kwargs):
		"""Initialize a new selenium request

        Parameters
        ----------
        wait_time: int
            The number of seconds to wait.
        wait_until: method
            One of the "selenium.webdriver.support.expected_conditions". The response
            will be returned until the given condition is fulfilled.
        screenshot: bool
            If True, a screenshot of the page will be taken and the data of the screenshot
            will be returned in the response "meta" attribute.
        script: str
            JavaScript code to execute.

        """
		try:
			self.wait_time = wait_time
			self.wait_until = wait_until
			self.screenshot = screenshot
			self.script = script

			super().__init__(*args, **kwargs)

		except Exception as ex:
			logger.error("PostgreSqlExporter Exception : %s", str(ex))


class SeleniumIDERequest(Request):
	def __init__(self, url=None, ide_function=None, wait_time=None, wait_until=None, screenshot=False, script=None, *args, **kwargs):
		"""Initialize a new selenium request

        Parameters
        ----------
        wait_time: int
            The number of seconds to wait.
        wait_until: method
            One of the "selenium.webdriver.support.expected_conditions". The response
            will be returned until the given condition is fulfilled.
        screenshot: bool
            If True, a screenshot of the page will be taken and the data of the screenshot
            will be returned in the response "meta" attribute.
        script: str
            JavaScript code to execute.

        """
		self.ide_function = ide_function
		self.wait_time = wait_time
		self.wait_until = wait_until
		self.screenshot = screenshot
		self.script = script
		kwargs['url'] = 'http://0.0.0.0/' + str(uuid.uuid1())
		super().__init__(*args, **kwargs)
