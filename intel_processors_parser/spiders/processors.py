import scrapy


class ProcessorsSpider(scrapy.Spider):
    name = 'processors'
    allowed_domains = ['ark.intel.com']
    start_urls = ['http://ark.intel.com/']

    def parse(self, response):
        pass
