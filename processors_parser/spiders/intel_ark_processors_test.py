import unittest
from processors_parser.spiders.intel_ark_processors import IntelArkProcessorsSpider

class TestIntelArkProcessorsSpider(unittest.TestCase):
    def test_get_processor_name(self):
        res = IntelArkProcessorsSpider.get_processor_name('Intel® Core™2 Extreme Processor X7900')
        self.assertEqual(res, 'Intel Core2 Extreme X7900')
