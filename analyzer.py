# -*- coding: utf-8 -*-
import asyncio
from lxml import etree
import requests
import config
import time
from futu import *
from pyppeteer import launch


class StockAnalyzer():
    def __init__(self, base_url, query, bonus_url, debt_url):
        self.base_url = base_url
        self.query = query
        self.bonus_url = bonus_url
        self.debt_url = debt_url
        self.stock_dict = {}
        self.debt_ratio = []
        self.qualified_stocks = []

    async def iwc_filter(self):
        browser = await launch({'headless': True})
        page = await browser.newPage()
        try:
            await page.goto(self.base_url.format(self.query))
            await page.waitForNavigation()
        except Exception as e:
            print(e)
        finally:
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

    def extract_bonus(self, stock_code):
        raise Exception("extract_bonus not implemented.")

    def treasury_fetch(self, url, path):
        res = requests.get(url, headers=config.headers)
        root = etree.HTML(res.content)
        treasury_yield = float(root.xpath(path)[0])
        
        return treasury_yield

    def price_calc(self, stocks):
        raise Exception("price_calc not implemented.")

    def price_calc(self, stocks):
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        if type(self).__name__ == 'StockAnalyzerA':
            treasury_yield = self.treasury_fetch(config.cn_treasury, config.treasury_path)
            treasury_dashboard = 'Treasury chosen: {:.3f}'.format(treasury_yield)
        if type(self).__name__ == 'StockAnalyzerHK':
            cn_treasury = self.treasury_fetch(config.cn_treasury, config.treasury_path)
            us_treasury = self.treasury_fetch(config.us_treasury, config.treasury_path)
            treasury_yield = max(cn_treasury, us_treasury)
            treasury_dashboard = 'Treasury chosen: {:.3f}  |  cn_treasury: {:.3f}, us_treasury: {:.3f}'.format(treasury_yield, cn_treasury, us_treasury)
        info_list = []
        # quote_ctx.get_market_snapshot(['SH.600519', 'SH.600660'])[1][['code', 'last_price', 'pe_ttm_ratio', 'dividend_ttm']].ix[[0]].values[0]
        request_count = 0
        for stock in stocks:
            code = stock.split()[1]
            if type(self).__name__ == 'StockAnalyzerA':
                try:
                    if request_count < 11:  # 30s内请求10次
                        request_count += 1
                    else:
                        print('Delaying 30 seconds to avoid being banned...')
                        time.sleep(30)
                        request_count = 1
                    info_list = quote_ctx.get_market_snapshot(['SH.{}'.format(code)])[1][['code', 'last_price', 'pe_ttm_ratio', 'dividend_ttm']].values[0]
                except Exception as e:
                    try:
                        if request_count < 11:
                            request_count += 1
                        else:
                            print('Delaying 30 seconds to avoid being banned...')
                            time.sleep(30)
                            request_count = 1
                        info_list = quote_ctx.get_market_snapshot(['SZ.{}'.format(code)])[1][['code', 'last_price', 'pe_ttm_ratio', 'dividend_ttm']].values[0]
                    except Exception as e:
                        pass
            elif type(self).__name__ == 'StockAnalyzerHK':
                if request_count < 11:  # 30s内请求10次
                    request_count += 1
                else:
                    print('Delaying 30 seconds to avoid being banned...')
                    time.sleep(30)
                    request_count = 1
                info_list = quote_ctx.get_market_snapshot(['HK.{}'.format(code)])[1][['code', 'last_price', 'pe_ttm_ratio', 'dividend_ttm']].values[0]
            price = min(15 * info_list[1]/info_list[2], 100 * info_list[3]/treasury_yield)
            if info_list[1] < price:
                print('{:<15s} Stock code: {} Last price: {:8.2f} Good price: {:8.2f}  √'.format(stock, info_list[0], info_list[1], price))
            else:
                print('{:<15s} Stock code: {} Last price: {:8.2f} Good price: {:8.2f}'.format(stock, info_list[0], info_list[1], price))
            info_list.fill(0)
        print(treasury_dashboard)

        quote_ctx.close()

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.iwc_filter())
        self.judgement()
        print('Qualified stocks: ')
        for i in self.qualified_stocks:
            print(i)
        # self.price_calc(self.qualified_stocks)
        