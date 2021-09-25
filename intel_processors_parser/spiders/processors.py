import scrapy
import sqlite3


class ProcessorsSpider(scrapy.Spider):
    name = 'processors'
    allowed_domains = ['intel.com']
    start_urls = [
        'https://www.intel.com/content/www/us/en/products/details/processors/core/i3/products.html',
        'https://www.intel.com/content/www/us/en/products/details/processors/core/i5/products.html',
        'https://www.intel.com/content/www/us/en/products/details/processors/core/i7/products.html',
        'https://www.intel.com/content/www/us/en/products/details/processors/core/i9/products.html',
        'https://www.intel.com/content/www/us/en/products/details/processors/core/x/products.html',
    ]

    field_labels = {
        '': '',
    }

    field_types = {
        'cores': 'INT',
        'threads': 'INT',
        '': '',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        conn = sqlite3.connect('../../result.db')
        c = conn.cursor()

        table_columns = ''
        for field_name, field_type in self.field_types.items():
            table_columns += ', ' + field_name + ' ' + field_type

        c.execute("CREATE TABLE processors(id INTEGER PRIMARY KEY" + table_columns + ')')

        self.conn = conn

    def parse(self, response):
        if len(response.body) == 0:
            return

        for processor_link in response.css('.table-responsive > tbody > tr > td:nth-child(2) > a'):
            yield response.follow(processor_link, self.parse_processor)

    @staticmethod
    def parse_value(value, value_type):
        if value_type == 'TEXT':
            return value
        if value_type == 'INT':
            return int(value.split(' ')[0])
        if value_type == 'REAL':
            return float(value.split(' ')[0])
        raise Exception('invalid value type')

    def parse_processor(self, response):
        fields = {}

        for field_row in response.css('.tech-section-row'):
            label = field_row.css('.tech-label > span')
            value = field_row.css('.tech-data > *::text')
            field_name = self.field_labels[label]
            fields[field_name] = self.parse_value(value, self.field_types[field_name])

        c = self.conn.cursor()
        query = 'INSERT INTO ' + ', '.join(fields.keys()) + \
                ' VALUES (' + ', '.join(['?' for _ in range(len(fields))]) + ')'
        c.execute(query, fields.values())
