import scrapy
import sqlite3
from processors_parser.spiders.helpers import parse_page


class AmdArchiveProcessorsSpider(scrapy.Spider):
    name = 'amd_archive_processors'
    allowed_domains = ['web.archive.org']
    user_agent = 'Test'

    field_labels = {
        'ctl00_cphBody_lblModel': 'name',
        'ctl00_cphBody_lblProductFamily': 'product_line',
        'ctl00_cphBody_lblOPNTray': 'opn_tray',
        'ctl00_cphBody_lblOPNPIB': 'opn_pib',
        'ctl00_cphBody_lblRevision': 'revision',
        'ctl00_cphBody_lblCoreSpeed': 'base_frequency',
        'ctl00_cphBody_lblMaxTemps': 'max_temp',
        'ctl00_cphBody_lblWattage': 'tdp',
        'ctl00_cphBody_lblL1CacheSize': 'cache_l1',
        'ctl00_cphBody_lblL2CacheSize': 'cache_l2',
        'ctl00_cphBody_lblL3CacheSize': 'cache_l3',
        'ctl00_cphBody_lblCMOS': 'lithography',
        'ctl00_cphBody_lblSocket': 'socket',
    }

    # field_labels = {
    #     'Model': 'name',
    #     'product_line': 'Processor',
    #     'OPN Tray': 'opn_tray',
    #     'OPN PIB': 'opn_pib',
    #     'Revision': 'revision',
    #     'Core Speed (Mhz)': 'base_frequency',
    #     'Max Temps (C)': 'max_temp',
    #     'Wattage': 'tdp',
    #     'L1 Cache Size (KB)': 'cache_l1',
    #     'L2 Cache Size (KB)': 'cache_l2',
    #     'L3 Cache Size (KB)': 'cache_l3',
    #     'CMOS': 'lithography',
    #     'Socket': 'socket',
    # }

    field_types = {
        'name': 'TEXT',
        'base_frequency': 'NUMERIC',
        'tdp': 'NUMERIC',
        'max_temp': 'NUMERIC',
        'url': 'TEXT',
        'socket': 'TEXT',
        'product_line': 'TEXT',
        'lithography': 'INT',
        'opn_tray': 'TEXT',
        'opn_pib': 'TEXT',
        'revision': 'TEXT',
        'cache_l1': 'NUMERIC',
        'cache_l2': 'NUMERIC',
        'cache_l3': 'NUMERIC',
        'first_mention_year': 'TEXT',
    }

    unique_fields = [
        ('opn_tray', 'opn_pib'),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        conn = sqlite3.connect('result.db', isolation_level=None)
        c = conn.cursor()

        table_columns = ''
        for field_name, field_type in self.field_types.items():
            table_columns += ', ' + field_name + ' ' + field_type + \
                             (' unique' if field_name in self.unique_fields else '')

        constraints = ', '.join(
                map(lambda x: 'unique(' + ', '.join(x) + ')',
                    filter(lambda x: isinstance(x, tuple), self.unique_fields)))

        if constraints != '':
            constraints = ', ' + constraints

        c.execute('DROP TABLE IF EXISTS amd_archive_processors')

        q = ("CREATE TABLE amd_archive_processors("
             "id INTEGER PRIMARY KEY" +
             table_columns +
             constraints +
             ')')

        c.execute(q)

        self.conn = conn

    def start_requests(self):
        urls = [
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

        order = len(urls)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_list, priority=order)
            order -= 1

    def parse_list(self, response, **kwargs):
        if len(response.body) == 0:
            return

        processor_links = response.css('.compareResultTable tr td a')

        for link in processor_links:
            yield response.follow(link, self.parse_processor)

    def parse_processor(self, response):
        rows = list(map(lambda x: response.css('#' + x), self.field_labels.keys()))

        fields = parse_page(
            rows,
            lambda x: x.attrib.get('id', None),
            lambda x, _: x.css('::text').get(),
            self.field_labels,
            self.field_types,
            response.request.url)

        if fields is None:
            return

        if response.request.url is not None and len(response.request.url) > 32:
            fields['first_mention_year'] = response.request.url[28:32]

        if fields['opn_tray'].lower() == 'n/a' or fields['opn_tray'] == '':
            del fields['opn_tray']

        if fields['opn_pib'].lower() == 'n/a' or fields['opn_pib'] == '':
            del fields['opn_pib']

        fields['name'] = fields['product_line'] + ' ' + fields['name']

        c = self.conn.cursor()
        query = 'INSERT INTO amd_archive_processors(' + \
                ', '.join(fields.keys()) + \
                ') VALUES (' + \
                ', '.join(['?' for _ in range(len(fields))]) + \
                ')'
        args = list(fields.values())
        c.execute(query, args)
