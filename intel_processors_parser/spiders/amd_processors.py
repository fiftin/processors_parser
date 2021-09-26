import scrapy


class AmdProcessorsSpider(scrapy.Spider):
    name = 'amd_processors'
    allowed_domains = ['amd.com']
    start_urls = [
        'https://www.amd.com/en/products/specifications/processors'
    ]
    field_labels = {
        '# of Cores': 'cores',
        '# of Threads': 'threads',
        'Processor Number': 'model',
        'Launch Date': 'launch_date',
        'Lithography': 'lithography',
        'Processor Base Frequency': 'base_frequency',
        'Configurable TDP-up Frequency': 'base_frequency',
        'Max Turbo Frequency': 'turbo_frequency',
        'Cache': 'cache_size',
        'TDP': 'tdp',
        'Configurable TDP-up': 'tdp',
        'Recommended Customer Price': 'price',
        'Product Collection': 'collection',
        'Sockets Supported': 'socket',
        'Memory Types': 'memory_type',
        'Vertical Segment': 'vertical_segment',
        'Max Memory Size (dependent on memory type)': 'max_memory_size'
    }

    field_types = {
        'cores': 'INT',
        'threads': 'INT',
        'model': 'TEXT',
        'launch_date': 'TEXT',
        'lithography': 'INT',
        'base_frequency': 'NUMERIC',
        'turbo_frequency': 'NUMERIC',
        'cache_size': 'NUMERIC',
        'tdp': 'NUMERIC',
        'price': 'NUMERIC',
        'collection': 'TEXT',
        'socket': 'TEXT',
        'memory_type': 'TEXT',
        'url': 'TEXT',
        'vertical_segment': 'TEXT',
        'max_memory_size': 'NUMERIC',
    }

    def parse(self, response):
        if len(response.body) == 0:
            return
        processor_links = response.css('#spec-table > tbody > tr')
        for link in processor_links:
            yield response.follow(link, self.parse_processor)

    def parse_processor(self):
