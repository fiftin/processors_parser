import unittest
from processors_parser.spiders.helpers import parse_value, \
    parse_bytes, extract_number, extract_number_with_tail


class TestProcessorsSpider(unittest.TestCase):
    def test_extract_number(self):
        res = extract_number('up to 10w')
        self.assertEqual(res, '10')

        res = extract_number('up to $10 - $20')
        self.assertEqual(res, '10')

    def test_extract_number_with_tail(self):
        res = extract_number_with_tail('up to 10w')
        self.assertEqual(res, '10w')

        res = extract_number_with_tail('up to $10 - $20')
        self.assertEqual(res, '$10 - $20')

    def test_parse_bytes(self):
        res = parse_bytes(' 104 B')
        self.assertEqual(res, 104)

    def test_parse_bytes_gb(self):
        res = parse_bytes(' 10.4 GB ')
        self.assertEqual(res, 10_400_000_000)

    def test_parse_value_int(self):
        res = parse_value(' 10 W ', 'INT')
        self.assertEqual(res, 10)

    def test_parse_value_numeric_dollar(self):
        res = parse_value('$10 - $100 ', 'NUMERIC')
        self.assertEqual(res, 10)


if __name__ == '__main__':
    unittest.main()
