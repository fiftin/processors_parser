import scrapy
import sqlite3
from urllib.parse import quote_plus


class CpuBenchmarkSpider(scrapy.Spider):
    name = 'cpu_benchmark'
    allowed_domains = ['cpubenchmark.net']

    field_types = {
        'rating': 'INT',
        # 'thread_rating': 'INT',
        # 'vertical_segment': 'TEXT',
        # 'socket': 'TEXT',
        # 'price': 'NUMERIC',
        # 'tdp': 'INT',
        # 'base_frequency': 'NUMERIC',
        # 'turbo_frequency': 'NUMERIC',
        # 'other_names': 'TEXT',
        # 'first_test_date': 'TEXT',
        # 'overall_rank': 'INT',
        # 'cpu_mark_per_price': 'NUMERIC',
        'url': 'TEXT',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        conn = sqlite3.connect('result.db', isolation_level=None)
        c = conn.cursor()

        c.execute('DROP TABLE IF EXISTS cpu_benchmarks')

        table_columns = ''
        for field_name, field_type in self.field_types.items():
            table_columns += ', ' + field_name + ' ' + field_type

        c.execute('CREATE TABLE cpu_benchmarks(id INTEGER PRIMARY KEY, manufacturer TEXT, sku INT' +
                  table_columns +
                  ')')

        self.conn = conn

    def start_requests(self):
        c = self.conn.cursor()

        # AMD processors
        c.execute("SELECT sku, name FROM amd_processors")
        rows = c.fetchall()
        for row in rows:
            url = 'https://www.cpubenchmark.net/cpu.php?cpu=' + quote_plus(row[1])
            yield scrapy.Request(url, lambda response, sku=row[0]: self.parse_page('amd', sku, response))

        # Intel processors
        c.execute("SELECT sku, name FROM intel_ark_processors")
        rows = c.fetchall()
        for row in rows:
            url = 'https://www.cpubenchmark.net/cpu.php?cpu=' + quote_plus(row[1])
            yield scrapy.Request(url, lambda response, sku=row[0]: self.parse_page('intel', sku, response))

    def parse_page(self, manufacturer, sku, response):
        rating = response.css('.right-desc > *:nth-child(3)::text').get()
        c = self.conn.cursor()
        query = 'INSERT INTO cpu_benchmarks(manufacturer, sku, rating, url) values (?, ?, ?, ?)'
        c.execute(query, [manufacturer, sku, rating, response.request.url])
