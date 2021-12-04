import scrapy
import sqlite3
import re
from processors_parser.spiders.helpers import parse_page


class AmdArchiveProcessorsSpider(scrapy.Spider):
    name = 'amd_archive_processors'
    allowed_domains = ['web.archive.org']
    user_agent = 'Test'
    start_urls = [
        'https://web.archive.org/web/20071201082516/http://products.amd.com/en-us/DesktopCPUResult.aspx',
        'https://web.archive.org/web/20081204062327/http://products.amd.com/en-us/DesktopCPUResult.aspx',
        'https://web.archive.org/web/20091031060354/http://products.amd.com/en-US/DesktopCPUResult.aspx',
        'https://web.archive.org/web/20100604022602/http://products.amd.com/en-us/DesktopCPUResult.aspx',
        'https://web.archive.org/web/20110902072938/http://products.amd.com/en-us/DesktopCPUResult.aspx',
        'https://web.archive.org/web/20121101192858/http://products.amd.com/en-us/desktopcpuresult.aspx',
        'https://web.archive.org/web/20131202021519/http://products.amd.com/pages/DesktopCPUResult.aspx',
        'https://web.archive.org/web/20141028101157/http://products.amd.com/en-us/DesktopCPUResult.aspx',
        'https://web.archive.org/web/20150711210326/http://products.amd.com/en-us/DesktopCPUResult.aspx',
    ]

    field_labels = {
    }

    field_types = {
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        conn = sqlite3.connect('result.db', isolation_level=None)
        c = conn.cursor()

        table_columns = ''
        for field_name, field_type in self.field_types.items():
            table_columns += ', ' + field_name + ' ' + field_type

        c.execute('DROP TABLE IF EXISTS amd_archive_processors')

        c.execute("CREATE TABLE amd_archive_processors("
                  "id INTEGER PRIMARY KEY" +
                  table_columns + ')')

        self.conn = conn

    def parse(self, response, **kwargs):
        if len(response.body) == 0:
            return

        processor_rows = response.css('#spec-table > tbody > tr')

        for row in processor_rows:
            self.parse_processor(row)

    def parse_processor(self, row):
        sku = re.search(r'entity-(\d+)', row.css('td:nth-child(2)').attrib['class'])[1]

        fields = parse_page(
            row.css('td'),
            lambda x: x.attrib.get('headers', None),
            lambda x, _: x.css('::text').get(),
            self.field_labels,
            self.field_types,
            'https://www.amd.com/en/product/' + sku)

        if fields is None:
            return

        fields['sku'] = sku

        c = self.conn.cursor()
        query = 'INSERT INTO amd_archive_processors(' + \
                ', '.join(fields.keys()) + \
                ') VALUES (' + \
                ', '.join(['?' for _ in range(len(fields))]) + \
                ')'
        args = list(fields.values())
        c.execute(query, args)
