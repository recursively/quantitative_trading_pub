import unittest
from unittest.mock import MagicMock
from analyzer import StockAnalyzer
from stock_filter import StockAnalyzerA, StockAnalyzerHK, StockAnalyzerUS
import config
import asyncio


class StockAnalyzerTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(__class__, self).__init__(*args, **kwargs)
        self.stock_code_cn = '600519'
        self.Analyzer_cn = StockAnalyzerA(config.base_url_A, config.query_A, config.bonus_url_A, config.debt_url_A)
        self.Analyzer_hk = StockAnalyzerHK(config.base_url_HK, config.query_HK, config.bonus_url_HK, None)
        self.Analyzer_us = StockAnalyzerUS(config.base_url_US, config.query_US, config.base_url_US, None)

    def test_main_filter(self):
        trial_count = 0
        trial_confirm = True
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.Analyzer_cn.iwc_filter())
        except Exception as e:
            while trial_count < 3 and trial_confirm is True:
                try:
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(self.Analyzer_cn.iwc_filter())
                    trial_confirm = False
                except Exception as e:
                    trial_count += 1
                    print('test_main_filter error: ', e)
        assert type(int(self.Analyzer_cn.stock_dict.popitem()[0].split()[-1])) == int

    def test_bonus_fetch_cn(self):
        bonus_list = self.Analyzer_cn.extract_bonus(self.stock_code_cn)
        assert len(bonus_list) == 5

    def test_debts_fetch_cn(self):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.Analyzer_cn.extract_debts(self.stock_code_cn))
        except Exception as e:
            print('test_debts_fetch_cn error: ', e)
        assert len(self.Analyzer_cn.debt_ratio) == 5

    def test_bonus_fetch_hk(self):
        pass


if __name__ == '__main__':
    unittest.main()
