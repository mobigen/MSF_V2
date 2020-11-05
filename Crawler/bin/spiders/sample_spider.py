from lib.scrapy.request import Request
from lib.interface.ispider import ispider



class Sample_Spider(ispider):
	name = 'SAMPLE_SPIDER'

	def __init__(self, *args, **kwargs):
		super(Sample_Spider, self).__init__(*args, **kwargs) 
		self.start_urls = ['http://www.mobigen.com/solution/IRIS-Platform.php']
		self.sections = ['SAMPLE_SPIDER']
		self.method = 'GET' 
			
	def start_requests(self):
		for url in self.start_urls: 
			yield Request(url) 

	def parse(self, response):
		ext = tldextract.extract(urlparse(response.url).netloc)
		domain = ext.registered_domain
		ext = DomainPatternLinkExtractor(domain, canonicalize=True, unique=True)
		urls = []

		if recursive:
			try:
				if response.headers['Content-Type'] \
						and response.headers['Content-Type'].decode("utf-8").lower().find("application") == -1:
					urls = [link.url for link in ext.extract_links(response)]
				else:
					return
			except Exception as ex:
				pass
			for url in urls:
				yield response.follow(url, self.parse, cb_kwargs={'recursive': recursive, 'section': section})

		try:
			ext_domain = tldextract.extract(urlparse(response.url).netloc)
			item = CommonItem()
			item["date"] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
			item["url"] = response.url
			item["domain"] = ext_domain.registered_domain
			item["body"] = response.body

			item.fields["section"] = CommonField()
			item["section"] = section

			yield item
		except Exception as ex:
			pass