import scrapy
import sqlite3
import re
from processors_parser.spiders.helpers import parse_page, format_date


class AmdProcessorsSpider(scrapy.Spider):
    name = 'amd_processors'
    allowed_domains = ['amd.com']
    user_agent = 'Test'
    start_urls = [
        'https://www.amd.com/en/products/specifications/processors'
    ]

    field_labels = {
        'view-name-table-column': 'name',
        'view-field-cpu-core-count-table-column': 'cores',
        'view-field-thread-count-table-column': 'threads',
        'view-field-launch-date-table-column': 'launch_date',
        'view-field-cmos-table-column': 'lithography',
        'view-field-cpu-clock-speed-table-column': 'base_frequency',
        'view-field-max-cpu-clock-speed-table-column': 'turbo_frequency',
        'view-field-total-l1-cache-table-column': 'cache_l1',
        'view-field-total-l2-cache-table-column': 'cache_l2',
        'view-field-total-l3-cache-table-column': 'cache_l3',
        'view-field-default-tdp-table-column': 'tdp',
        'view-product-type-1-table-column': 'product_line',
        'view-field-socket-table-column': 'socket',
        'view-product-type-6-table-column': 'memory_type',
        'view-platform-table-column': 'vertical_segment',
        'view-field-max-temps-table-column': 'max_temp',
        'view-field-max-memory-speed-table-column': 'max_memory_speed',
    }

    field_types = {
        'cores': 'INT',
        'threads': 'INT',
        'name': 'TEXT',
        'launch_date': 'TEXT',
        'lithography': 'INT',
        'base_frequency': 'NUMERIC',
        'turbo_frequency': 'NUMERIC',
        'cache_l1': 'NUMERIC',
        'cache_l2': 'NUMERIC',
        'cache_l3': 'NUMERIC',
        'tdp': 'NUMERIC',
        'product_line': 'TEXT',
        'socket': 'TEXT',
        'memory_type': 'TEXT',
        'url': 'TEXT',
        'vertical_segment': 'TEXT',
        'max_temp': 'NUMERIC',
        'max_memory_speed': 'INT',
        'sku': 'INT',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        conn = sqlite3.connect('result.db', isolation_level=None)
        c = conn.cursor()

        table_columns = ''
        for field_name, field_type in self.field_types.items():
            table_columns += ', ' + field_name + ' ' + field_type

        c.execute('DROP TABLE IF EXISTS amd_processors')

        c.execute("CREATE TABLE amd_processors("
                  "id INTEGER PRIMARY KEY" +
                  table_columns + ')')

        self.conn = conn

    def parse(self, response, **kwargs):
        if len(response.body) == 0:
            return

        processor_rows = response.css('#spec-table > tbody > tr')

        for row in processor_rows:
            self.parse_processor(row)

    @staticmethod
    def get_field_value(value, field_name):
        if field_name == 'launch_date':
            return format_date(value)
        else:
            return value

    def parse_processor(self, row):
        sku = re.search(r'entity-(\d+)', row.css('td:nth-child(2)').attrib['class'])[1]

        fields = parse_page(
            row.css('td'),
            lambda x: x.attrib.get('headers', None),
            lambda x, field_name: self.get_field_value(x.css('::text').get(), field_name),
            self.field_labels,
            self.field_types,
            'https://www.amd.com/en/product/' + sku)

        if fields is None:
            return

        fields['sku'] = sku

        c = self.conn.cursor()
        query = 'INSERT INTO amd_processors(' + \
                ', '.join(fields.keys()) + \
                ') VALUES (' + \
                ', '.join(['?' for _ in range(len(fields))]) + \
                ')'
        args = list(fields.values())
        c.execute(query, args)
