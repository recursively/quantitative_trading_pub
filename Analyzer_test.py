import unittest
from unittest.mock import MagicMock
from analyzer import StockAnalyzer
from stock_filter import StockAnalyzerA
import config


class StockAnalyzerTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(__class__, self).__init__(*args, **kwargs)
        self.stock_code_cn = '600660'

    def test_bonus_fetch_cn(self):
        Analyzer = StockAnalyzerA(config.base_url_A, config.query_A, config.bonus_url_A, config.debt_url_A)
        bonus_list = Analyzer.extract_bonus(self.stock_code_cn)
        assert len(bonus_list) > 2 and len(bonus_list) < 10


if __name__ == '__main__':
    unittest.main()
