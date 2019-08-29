# -*- coding: utf-8 -*-
import asyncio
from lxml import etree
import requests
import config
from futu import *
from pyppeteer import launch
import time


class Quote():
    def __init__(self):
        self.quote = OpenQuoteContext(host='127.0.0.1', port=11111)

    def __enter__(self):
        return self.quote

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quote.close()


class StockAnalyzer():
    def __init__(self, base_url, query, bonus_url, debt_url):
        self.base_url = base_url
        self.query = query
        self.bonus_url = bonus_url
        self.debt_url = debt_url
        self.stock_dict = {}
        self.debt_ratio = []
        self.qualified_stocks = []
        self.gprice = 0

    async def iwc_filter(self):
        browser = await launch({'headless': True, 'args': ['--disable-dev-shm-usage']})
        page = await browser.newPage()
        await page.goto(self.base_url.format(self.query), timeout=60000)

        await page.waitForNavigation(timeout=60000)
        page_count = 1
        while page_count < 3:
            page_count += 1
            all_targets = await page.xpath('//*[@id="tableWrap"]/div[2]/div/div[2]/div/table/tbody/tr[*]/td[4]/div/a')

            for i in range(len(all_targets)):
                all_elements = (await page.xpath('//*[@id="tableWrap"]/div[2]/div/div[1]/div/div/div[2]/table/tbody/tr[{}]/td[position()>2]'.format(i+1)))
                stock_code = await page.xpath('//*[@id="tableWrap"]/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[3]/div'.format(i+1))
                # print(await (await all_targets[i].getProperty('textContent')).jsonValue(), ":", end='')
                elements_list = [(await (await item.getProperty('textContent')).jsonValue()).strip() for item in all_elements]
                while '' in elements_list: elements_list.remove('')
                self.stock_dict[await (await all_targets[i].getProperty('textContent')).jsonValue() + ' ' + await (await stock_code[0].getProperty('textContent')).jsonValue()] = str(elements_list)

            try:
                await page.click('#next')
                await page.waitFor(1000)
            except Exception as e:
                pass

        await browser.close()

    @staticmethod
    def pe_fetch():
        res = requests.get(config.pe_url, headers=config.headers)
        root = etree.HTML(res.content)
        pe_list = root.xpath('/html/body/div[1]/div[2]/div/div[2]/div[1]/div[3]/div[1]/div/div/div[2]/div/div[2]/div[1]/text()')
        pe = pe_list[0].split('：')[-1]
        return pe

    def judgement(self):
        raise Exception("judgment not implemented.")

    @staticmethod
    def treasury_fetch(url, path):
        res = requests.get(url, headers=config.headers)
        root = etree.HTML(res.content)
        treasury_yield = float(root.xpath(path)[0])

        return treasury_yield

    @staticmethod
    def get_stock_info(quote, market, stock_code):
        if market == 'SH':
            return quote.get_market_snapshot(['SH.{}'.format(stock_code)])[1][
                ['code', 'last_price', 'pe_ttm_ratio', 'dividend_ttm']].values[0]
        if market == 'SZ':
            return quote.get_market_snapshot(['SZ.{}'.format(stock_code)])[1][
                ['code', 'last_price', 'pe_ttm_ratio', 'dividend_ttm']].values[0]
        if market == 'HK':
            return quote.get_market_snapshot(['HK.{}'.format(stock_code)])[1][
                ['code', 'last_price', 'pe_ttm_ratio', 'dividend_ttm']].values[0]

    def price_calc(self, stocks):
        treasury_yield = 0
        dashboard = ''
        pe = StockAnalyzer.pe_fetch()
        if type(self).__name__ == 'StockAnalyzerA':
            treasury_yield = StockAnalyzer.treasury_fetch(config.cn_treasury, config.treasury_path)
            dashboard = 'Treasury chosen: {:.3f}\nShenzhen Stock Exchange PE ratio: {}'.format(treasury_yield, pe)
        if type(self).__name__ == 'StockAnalyzerHK':
            cn_treasury = StockAnalyzer.treasury_fetch(config.cn_treasury, config.treasury_path)
            us_treasury = StockAnalyzer.treasury_fetch(config.us_treasury, config.treasury_path)
            treasury_yield = max(cn_treasury, us_treasury)
            dashboard = 'Treasury chosen: {:.3f}  |  cn_treasury: {:.3f}, us_treasury: {:.3f}'.format(treasury_yield, cn_treasury, us_treasury)
        info_list = []
        # quote_ctx.get_market_snapshot(['SH.600519', 'SH.600660'])[1][['code', 'last_price', 'pe_ttm_ratio', 'dividend_ttm']].ix[[0]].values[0]
        request_count = 0
        with Quote() as quote_ctx:
            for stock in stocks:
                code = stock.split()[-1]
                if type(self).__name__ == 'StockAnalyzerA':
                    try:
                        if request_count > 9:  # 30s内请求10次
                            print('Delaying 30 seconds to avoid being banned...')
                            time.sleep(30)
                            request_count = 0
                        request_count += 1
                        info_list = StockAnalyzer.get_stock_info(quote_ctx, 'SH', code)
                    except Exception as e:
                        try:
                            if request_count > 9:
                                print('Delaying 30 seconds to avoid being banned...')
                                time.sleep(30)
                                request_count = 0
                            request_count += 1
                            info_list = StockAnalyzer.get_stock_info(quote_ctx, 'SZ', code)
                        except Exception as e:
                            pass
                elif type(self).__name__ == 'StockAnalyzerHK':
                    if request_count > 9:  # 30s内请求10次
                        print('Delaying 30 seconds to avoid being banned...')
                        time.sleep(30)
                        request_count = 0
                    request_count += 1
                    info_list = StockAnalyzer.get_stock_info(quote_ctx, 'HK', code)
                self.gprice = min(15 * info_list[1]/info_list[2], 100 * info_list[3]/treasury_yield)
                if info_list[1] < self.gprice:
                    print('{:<15s} Stock code: {} Last price: {:8.2f} Good price: {:8.2f}  √'.format(stock, info_list[0], info_list[1], self.gprice))
                else:
                    print('{:<15s} Stock code: {} Last price: {:8.2f} Good price: {:8.2f}'.format(stock, info_list[0], info_list[1], self.gprice))
        print(dashboard)

    # def start(self):
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(self.iwc_filter())
    #     self.judgement()
    #     print('Qualified stocks: ')
    #     for i in self.qualified_stocks:
    #         print(i)
    #     self.price_calc(self.qualified_stocks)
