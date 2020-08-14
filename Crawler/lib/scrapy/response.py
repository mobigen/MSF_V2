from scrapy.http import HtmlResponse

class SeleniumResponse(HtmlResponse):
	def __init__(self, *args, **kwargs):
		self.driver = kwargs.pop('driver', None)
		super(SeleniumResponse, self).__init__(*args, **kwargs)