import re

import scrapy
import sqlite3
from processors_parser.spiders.helpers import parse_page, prepare_brand, format_date


class IntelArkProcessorsSpider(scrapy.Spider):
    name = 'intel_ark_processors'
    allowed_domains = ['ark.intel.com']
    start_urls = [
        'https://ark.intel.com/content/www/us/en/ark.html'
    ]

    field_labels = {
        'Processor Number': 'processor_number',
        '# of Cores': 'cores',
        'Total Cores': 'cores',
        '# of Threads': 'threads',
        'Total Threads': 'threads',
        'Bus Speed': 'bus_speed',
        'Launch Date': 'launch_date',
        'Lithography': 'lithography',
        'Configurable TDP-up Frequency': 'configurable_tdp_up_frequency',
        'Max Turbo Frequency': 'turbo_frequency',
        'Processor Base Frequency': 'base_frequency',
        'Cache': 'cache_size',
        'TDP': 'tdp',
        'Configurable TDP-up': 'configurable_tdp_up',
        'Recommended Customer Price': 'price',
        'Product Collection': 'product_line',
        'Sockets Supported': 'socket',
        'Memory Types': 'memory_type',
        'Vertical Segment': 'vertical_segment',
        'Max Memory Size (dependent on memory type)': 'max_memory_size',
        'Status': 'status',
        'Operating Temperature (Maximum)': 'max_temp',
        'TJUNCTION': 'max_temp',
        'TCASE': 'max_temp',
        'Package Size': 'package_size',
    }

    field_types = {
        'cores': 'INT',
        'threads': 'INT',
        'name': 'TEXT',
        'processor_number': 'TEXT',
        'launch_date': 'TEXT',
        'lithography': 'INT',
        'bus_speed': 'NUMERIC',
        'base_frequency': 'NUMERIC',
        'turbo_frequency': 'NUMERIC',
        'configurable_tdp_up_frequency': 'NUMERIC',
        'cache_size': 'NUMERIC',
        'tdp': 'NUMERIC',
        'configurable_tdp_up': 'NUMERIC',
        'price': 'NUMERIC',
        'product_line': 'TEXT',
        'socket': 'TEXT',
        'memory_type': 'TEXT',
        'url': 'TEXT',
        'vertical_segment': 'TEXT',
        'max_memory_size': 'NUMERIC',
        'status': 'TEXT',
        'max_temp': 'NUMERIC',
        'sku': 'INT',
        'package_size': 'TEXT',
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

        processor_links = response.css('.products.processors a.ark-accessible-color')
        for link in processor_links:
            yield response.follow(link, self.parse_processors)

    def parse_processors(self, response):
        processor_links = response.css('#product-table tbody > tr > td:nth-child(1) > a')
        for link in processor_links:
            yield response.follow(link, self.parse_processor)

    @staticmethod
    def get_processor_sku(response):
        m = re.search(r'/products/(\d+)/', response.request.url)
        return None if m is None else m[1]

    @staticmethod
    def get_processor_name(fullname, process_number=None):
        if fullname.find('Processor') == -1 and fullname.find('Microcontroller') == -1:
            return None

        name = prepare_brand(fullname) \
            .replace('Processor', '') \
            .replace('Microcontroller', '') \
            .replace('  ', ' ')

        m = re.search('$([^(]+)', name)
        if m is not None:
            name = m[1]

        if process_number is not None:
            i = name.find(process_number)
            if i != -1:
                name = name[0:i + len(process_number)]

        return name.strip()

    @staticmethod
    def get_processor_family(response):
        fullname = response.css('h1::text').get()
        m = re.search(r'Intel\s+([^\s]+)\s+', prepare_brand(fullname))
        return None if m is None else m[1]

    @staticmethod
    def get_field_value(value_selector, row, field_name):
        value = ''.join(row.css(value_selector).extract()).strip()
        if field_name == 'launch_date':
            return format_date(value)
        else:
            return value

    def parse_processor(self, response):
        fields = parse_page(
            response.css('.arkProductSpecifications li'),
            lambda x: ''.join(x.css('.label *::text').extract()),
            lambda x, field_name: self.get_field_value('.value::text', x, field_name),
            self.field_labels,
            self.field_types,
            response.request.url)

        if fields is None:
            return

        fields['name'] = self.get_processor_name(response.css('h1::text').get(), fields.get('processor_number', None))
        fields['fullname'] = prepare_brand(response.css('h1::text').get()).strip()

        if fields.get('name', None) is None and fields.get('processor_number', None) is None:
            return

        fields['sku'] = self.get_processor_sku(response)

        c = self.conn.cursor()
        query = 'INSERT INTO intel_ark_processors(' + \
                ', '.join(fields.keys()) + \
                ') VALUES (' + \
                ', '.join(['?' for _ in range(len(fields))]) + \
                ')'
        args = list(fields.values())
        c.execute(query, args)
