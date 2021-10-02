import scrapy
import sqlite3
from processors_parser.spiders.helpers import parse_value, parse_page


class AmdProcessorsSpider(scrapy.Spider):
    name = 'amd_processors'
    allowed_domains = ['amd.com']
    start_urls = [
        'https://www.amd.com/en/products/specifications/processors'
    ]

    field_labels = {
        '# of CPU Cores': 'cores',
        '# of Threads': 'threads',
        'Launch Date': 'launch_date',
        'Processor Technology for CPU Cores': 'lithography',
        'Max. Boost Clock': 'base_frequency',
        'Base Clock': 'base_frequency',
        'Max Turbo Frequency': 'turbo_frequency',
        'Cache': 'cache_size',
        'Default TDP': 'tdp',
        'Product Line': 'product_line',
        'CPU Socket': 'socket',
        'System Memory Type': 'memory_type',
        'Platform': 'vertical_segment',
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

        c.execute("CREATE TABLE amd_processors("
                  "id INTEGER PRIMARY KEY" +
                  table_columns + ')')

        self.conn = conn

    def parse(self, response, **kwargs):
        if len(response.body) == 0:
            return
        processor_links = response.css('#spec-table > tbody > tr')
        for link in processor_links:
            yield response.follow(link, self.parse_processor)

    def parse_processor(self, response):
        fields = parse_page(
            response.css('.fieldset-wrapper > .field'),
            '.field__label::text',
            '.field__item::text',
            self.field_labels,
            self.field_types,
            response.request.url)

        if fields is None:
            return

        c = self.conn.cursor()
        query = 'INSERT INTO amd_processors(' + \
                ', '.join(fields.keys()) + \
                ') VALUES (' + \
                ', '.join(['?' for _ in range(len(fields))]) + \
                ')'
        args = list(fields.values())
        c.execute(query, args)
