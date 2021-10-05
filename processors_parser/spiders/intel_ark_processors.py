import scrapy
import sqlite3
from processors_parser.spiders.helpers import parse_page


class ProcessorsSpider(scrapy.Spider):
    name = 'intel_ark_processors'
    allowed_domains = ['ark.intel.com']
    start_urls = [
        'https://ark.intel.com/content/www/us/en/ark.html'
    ]

    field_labels = {
        '# of Cores': 'cores',
        '# of Threads': 'threads',
        'Total Threads': 'threads',
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        conn = sqlite3.connect('result.db', isolation_level=None)
        c = conn.cursor()

        table_columns = ''
        for field_name, field_type in self.field_types.items():
            table_columns += ', ' + field_name + ' ' + field_type

        c.execute('DROP TABLE IF EXISTS intel_ark_processors')

        c.execute("CREATE TABLE intel_ark_processors("
                  "id INTEGER PRIMARY KEY" +
                  table_columns + ')')

        self.conn = conn

    def parse(self, response, **kwargs):
        if len(response.body) == 0:
            return

        processor_links = response.css('a.ark-accessible-color')
        for link in processor_links:
            yield response.follow(link, self.parse_processors)


    def parse_processors(self, response):
        processor_links = response.css('#product-table tbody > tr > td:nth-child(1) > a')
        for link in processor_links:
            yield response.follow(link, self.parse_processor)


    def parse_processor(self, response):
        fields = parse_page(
            response.css('.tech-section-row'),
            lambda x: x.css('.tech-label > span::text').get(),
            lambda x: x.css('.tech-data > *::text').get(),
            self.field_labels,
            self.field_types,
            response.request.url)

        if fields is None:
            return

        c = self.conn.cursor()
        query = 'INSERT INTO intel_ark_processors(' + \
                ', '.join(fields.keys()) + \
                ') VALUES (' + \
                ', '.join(['?' for _ in range(len(fields))]) + \
                ')'
        args = list(fields.values())
        c.execute(query, args)
