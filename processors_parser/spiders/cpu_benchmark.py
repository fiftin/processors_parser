import scrapy


class CpuBenchmarkSpider(scrapy.Spider):
    name = 'cpu_benchmark'
    allowed_domains = ['cpubenchmark.net']
    start_urls = ['https://cpubenchmark.net/']

    def parse(self, response):
        pass
