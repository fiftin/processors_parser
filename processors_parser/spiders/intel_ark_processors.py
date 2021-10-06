from processors_parser.spiders.intel_processor_base import IntelProcessorsBaseSpider


class IntelArkProcessorsSpider(IntelProcessorsBaseSpider):
    name = 'intel_ark_processors'
    allowed_domains = ['ark.intel.com']
    start_urls = [
        'https://ark.intel.com/content/www/us/en/ark.html'
    ]

    processor_collection_link_selector = '.products.processors a.ark-accessible-color'
    processors_link_selector = '#product-table tbody > tr > td:nth-child(1) > a'
    url_sku_re = r'/products/(\d+)/'
    processor_prop_selector = '.arkProductSpecifications li'
    processor_prop_label_selector = '.label *::text'
    processor_prop_value_selector = '.value::text'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
