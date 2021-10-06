from processors_parser.spiders.intel_processor_base import IntelProcessorsBaseSpider


class IntelProcessorsSpider(IntelProcessorsBaseSpider):
    name = 'intel_processors'
    allowed_domains = ['intel.com']
    start_urls = [
        'https://www.intel.com/content/www/us/en/products/details/processors/core/i3/products.html',
        'https://www.intel.com/content/www/us/en/products/details/processors/core/i5/products.html',
        'https://www.intel.com/content/www/us/en/products/details/processors/core/i7/products.html',
        'https://www.intel.com/content/www/us/en/products/details/processors/core/i9/products.html',
        'https://www.intel.com/content/www/us/en/products/details/processors/core/x/products.html',

        'https://www.intel.com/content/www/us/en/products/details/processors/celeron/products.html',

        'https://www.intel.com/content/www/us/en/products/details/processors/pentium/gold/products.html',
        'https://www.intel.com/content/www/us/en/products/details/processors/pentium/silver/products.html',

        'https://www.intel.com/content/www/us/en/products/details/processors/atom/c/products.html',
        'https://www.intel.com/content/www/us/en/products/details/processors/atom/p/products.html',

        'https://www.intel.com/content/www/us/en/products/details/processors/xeon/scalable/platinum/products.html',
        'https://www.intel.com/content/www/us/en/products/details/processors/xeon/scalable/gold/products.html',
        'https://www.intel.com/content/www/us/en/products/details/processors/xeon/scalable/silver/products.html',
        'https://www.intel.com/content/www/us/en/products/details/processors/xeon/scalable/bronze/products.html',

        'https://www.intel.com/content/www/us/en/products/details/processors/xeon/e/products.html',
        'https://www.intel.com/content/www/us/en/products/details/processors/xeon/w/products.html',
        'https://www.intel.com/content/www/us/en/products/details/processors/xeon/d/products.html',
    ]

    processor_link_selector = '.table-responsive tbody > tr > td:nth-child(2) > a'
    url_sku_re = r'/products/sku/(\d+)/'
    processor_prop_selector = '.tech-section-row'
    processor_prop_label_selector = '.tech-label > span::text'
    processor_prop_value_selector = '.tech-data > *::text'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


