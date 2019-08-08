import unittest
from unittest.mock import MagicMock
from analyzer import StockAnalyzer

class StockAnalyzerTestCase(unittest.TestCase):
    def __init__():
        self.stock_code_cn = '600660'

    def m1(self):
        Analyzer = StockAnalyzerA(config.base_url_A, config.query_A, config.bonus_url_A, config.debt_url_A)
        assert len(Analyzer.extract_bonus(self.stock_code_cn)) > 2

    
