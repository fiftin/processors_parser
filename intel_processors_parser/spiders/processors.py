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
        '# of Cores':       'cores',
        '# of Threads':     'threads',
        'Processor Number': 'model',
        'Launch Date':      'launch_date',
        'Lithography':      'lithography',
        'Processor Base Frequency': 'base_frequency',
        'Configurable TDP-up Frequency': 'base_frequency',
        'Max Turbo Frequency': 'turbo_frequency',
        'Cache':            'cache_size',
        'TDP':              'tdp',
        'Configurable TDP-up': 'tdp',
        'Recommended Customer Price': 'price',
        'Product Collection':   'collection',
        'Sockets Supported': 'socket',
        'Memory Types':     'memory_type',
    }

    field_types = {
        'cores':        'INT',
        'threads':      'INT',
        'model':        'TEXT',
        'launch_date':  'TEXT',
        'lithography':  'INT',
        'base_frequency': 'NUMERIC',
        'turbo_frequency': 'NUMERIC',
        'cache_size':   'INT',
        'tdp':          'INT',
        'price':        'NUMERIC',
        'collection':   'TEXT',
        'socket':       'TEXT',
        'memory_type':  'TEXT',
        'url':          'TEXT',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        conn = sqlite3.connect('result.db', isolation_level=None)
        c = conn.cursor()

        table_columns = ''
        for field_name, field_type in self.field_types.items():
            table_columns += ', ' + field_name + ' ' + field_type

        c.execute("CREATE TABLE processors("
                  "id INTEGER PRIMARY KEY" +
                  table_columns + ')')

        self.conn = conn

    def parse(self, response):
        if len(response.body) == 0:
            return

        processor_links = response.css('.table-responsive tbody > tr > td:nth-child(2) > a')
        for link in processor_links:
            yield response.follow(link, self.parse_processor)


    @staticmethod
    def parse_value(value, value_type):
        value = value.strip()
        if value_type == 'TEXT':
            return value
        if value_type == 'INT':
            return int(value.split(' ')[0])
        if value_type == 'REAL':
            return float(value.split(' ')[0])
        if value_type == 'NUMERIC':
            if value.startswith('$'):
                value = value[1:]
            return float(value.split(' ')[0])
        raise Exception('invalid value type')

    def parse_processor(self, response):
        fields = {}

        for field_row in response.css('.tech-section-row'):
            label = field_row.css('.tech-label > span::text').get()
            value = field_row.css('.tech-data > *::text').get()
            field_name = self.field_labels.get(label, None)
            if field_name is None:
                continue
            fields[field_name] = self.parse_value(value, self.field_types[field_name])

        if len(fields) == 0:
            return

        fields['url'] = response.request.url

        c = self.conn.cursor()
        query = 'INSERT INTO processors(' + \
                ', '.join(fields.keys()) + \
                ') VALUES (' + \
                ', '.join(['?' for _ in range(len(fields))]) + \
                ')'
        args = list(fields.values())
        c.execute(query, args)
