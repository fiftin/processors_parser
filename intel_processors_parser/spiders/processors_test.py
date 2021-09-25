import unittest
from intel_processors_parser.spiders.processors import ProcessorsSpider


class TestProcessorsSpider(unittest.TestCase):

    def test_upper(self):
        res = ProcessorsSpider.parse_value('10 W', 'INT')
        self.assertEqual(res, 10)


if __name__ == '__main__':
    unittest.main()
