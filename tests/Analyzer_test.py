import unittest
from unittest.mock import MagicMock
from analyzer import StockAnalyzer
from stock_filter import StockAnalyzerA
import config
import asyncio


class StockAnalyzerTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(__class__, self).__init__(*args, **kwargs)
        self.stock_code_cn = '600519'
        self.Analyzer_cn = StockAnalyzerA(config.base_url_A, config.query_A, config.bonus_url_A, config.debt_url_A)

    def test_bonus_fetch_cn(self):
        bonus_list = self.Analyzer_cn.extract_bonus(self.stock_code_cn)
        assert len(bonus_list) == 5

    def test_main_filter(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.Analyzer_cn.iwc_filter())
        random_item = self.stock_dict.popitem()
        assert type(int(random_item[0].split()[-1])) == int


if __name__ == '__main__':
    unittest.main()
