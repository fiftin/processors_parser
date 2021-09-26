import unittest
from intel_processors_parser.spiders.processors import ProcessorsSpider


class TestProcessorsSpider(unittest.TestCase):
    def test_parse_bytes(self):
        res = ProcessorsSpider.parse_bytes(' 104 B')
        self.assertEqual(res, 104)

    def test_parse_bytes_gb(self):
        res = ProcessorsSpider.parse_bytes(' 10.4 GB ')
        self.assertEqual(res, 10_400_000_000)

    def test_parse_value_int(self):
        res = ProcessorsSpider.parse_value(' 10 W ', 'INT')
        self.assertEqual(res, 10)

    def test_parse_value_numeric_dollar(self):
        res = ProcessorsSpider.parse_value('$10 - $100 ', 'NUMERIC')
        self.assertEqual(res, 10)

if __name__ == '__main__':
    unittest.main()
