import unittest
from unittest.mock import MagicMock, patch
from analyzer import StockAnalyzer
from stock_filter import StockAnalyzerA, StockAnalyzerHK, StockAnalyzerUS
import config
import asyncio
import numpy as np
import time


class StockAnalyzerTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(__class__, self).__init__(*args, **kwargs)
        self.stock_code_cn = '600519'
        self.stock_code_hk = '00799'
        self.stock_code_us = 'DIS'
        self.Analyzer_cn = StockAnalyzerA(config.base_url_A, config.query_A, config.bonus_url_A, config.debt_url_A)
        self.Analyzer_hk = StockAnalyzerHK(config.base_url_HK, config.query_HK, config.bonus_url_HK, None)
        self.Analyzer_us = StockAnalyzerUS(config.base_url_US, config.query_US, config.base_url_US, None)

    def test_main_filter(self):
        # trial_count = 0
        # trial_confirm = True
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.Analyzer_cn.iwc_filter())
        except Exception as e:
            print('test_main_filter error: ', e)
        # except Exception as e:
        #     while trial_count < 3 and trial_confirm is True:
        #         try:
        #             loop = asyncio.get_event_loop()
        #             loop.run_until_complete(self.Analyzer_cn.iwc_filter())
        #             trial_confirm = False
        #         except Exception as e:
        #             trial_count += 1
        #             print('test_main_filter error: ', e)
        self.assertEqual(type(int(self.Analyzer_cn.stock_dict.popitem()[0].split()[-1])), int)

    def test_bonus_fetch_cn(self):
        bonus_list = self.Analyzer_cn.extract_bonus(self.stock_code_cn)
        self.assertEqual(len(bonus_list), 5)

    def test_debts_fetch_cn(self):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.Analyzer_cn.extract_debts(self.stock_code_cn))
        except Exception as e:
            print('test_debts_fetch_cn error: ', e)
        self.assertEqual(len(self.Analyzer_cn.debt_ratio), 5)

    def test_bonus_fetch_hk(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.Analyzer_hk.extract_bonus(self.stock_code_hk))
        bonus_data = np.array(self.Analyzer_hk.bonus_list[:5]).astype(np.float)
        self.assertTrue(np.mean(bonus_data) >= 10)

    def test_bonut_fetch_us(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.Analyzer_us.extract_bonus(self.stock_code_us))
        bonus_data = np.array(self.Analyzer_us.bonus_list).astype(np.float)
        self.assertTrue(np.mean(bonus_data) >= 0.2)

    def test_treasury_fetch(self):
        cn_treasury = StockAnalyzer.treasury_fetch(config.cn_treasury, config.treasury_path)
        us_treasury = StockAnalyzer.treasury_fetch(config.us_treasury, config.treasury_path)
        self.assertTrue(1 < max(cn_treasury, us_treasury) < 5)

    async def side_effect(self, stock_code):
        if stock_code == self.stock_code_cn:
            self.Analyzer_cn.debt_ratio = config.debt_ratio_sample_cn
        if stock_code == self.stock_code_hk:
            self.Analyzer_hk.bonus_list = config.bonus_list_sample_hk
        if stock_code == self.stock_code_us:
            self.Analyzer_us.bonus_list = config.bonus_list_sample_us

    def test_judgement_cn(self):
        StockAnalyzerA.extract_debts = MagicMock(side_effect=self.side_effect)
        self.Analyzer_cn.stock_dict = config.origin_sample_cn
        self.Analyzer_cn.judgement()
        self.assertEqual(self.Analyzer_cn.qualified_stocks[0].split()[-1], self.stock_code_cn)

    def test_judgement_hk(self):
        StockAnalyzerHK.extract_bonus = MagicMock(side_effect=self.side_effect)
        self.Analyzer_hk.stock_dict = config.origin_sample_hk
        self.Analyzer_hk.judgement()
        self.assertEqual(self.Analyzer_hk.qualified_stocks[0].split()[-1], self.stock_code_hk)

    def test_judgement_us(self):
        StockAnalyzerUS.extract_bonus = MagicMock(side_effect=self.side_effect)
        self.Analyzer_us.stock_dict = config.origin_sample_us
        self.Analyzer_us.judgement()
        self.assertEqual(self.Analyzer_us.qualified_stocks[0].split()[-1], self.stock_code_us)

    @patch('analyzer.Quote')
    def test_price_calculation(self, mock_tmp):
        mock_tmp.return_value.__enter__.return_value.name = 'entering'
        call_count = 0
        def side_effect(quote, market, stock_code):
            if market == 'SZ':
                print('dealing with SZ market')
            nonlocal call_count
            if call_count == 5:
                call_count += 1
                raise Exception('Intentionally raise an Exception to simulate the different market.')
            call_count += 1
            info_list = ['SH.600519', 962.03, 30.679, 14.539]
            return info_list
        StockAnalyzer.get_stock_info = MagicMock(side_effect=side_effect)
        start = time.perf_counter()
        self.Analyzer_cn.price_calc(['stock 000000'] * 15)
        self.Analyzer_hk.price_calc(['stock 000000'] * 15)
        stop = time.perf_counter()
        self.assertEqual(int(self.Analyzer_cn.gprice), 470)
        self.assertEqual(int(self.Analyzer_hk.gprice), 470)
        self.assertTrue(stop - start >= 59)

    def test_pe_fetch(self):
        pe = StockAnalyzer.pe_fetch()
        self.assertTrue(float(pe) > 0)


if __name__ == '__main__':
    unittest.main()
