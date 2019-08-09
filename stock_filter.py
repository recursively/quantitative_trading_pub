# -*- coding: utf-8 -*-
import asyncio
from pyppeteer import launch
import requests
from lxml import etree
import numpy as np
import config
from analyzer import StockAnalyzer


class StockAnalyzerA(StockAnalyzer):
    def __init__(self, base_url, query, bonus_url, debt_url):
        super(__class__, self).__init__(base_url, query, bonus_url, debt_url)
        self.qualified_stocks = []

    def extract_bonus(self, stock_code):
        res = requests.get(self.bonus_url.format(stock_code), headers=config.headers)
        root = etree.HTML(res.content)
        years = root.xpath('//*[@id="bonus_table"]/tbody/tr[*]/td[1]/text()')
        index = []
        recent_ratio = []
        for idx, val in enumerate(years):
            if "年报" in val:
                index.append(idx)

        ratio = root.xpath('//*[@id="bonus_table"]/tbody/tr[*]/td[9]/text()')
        for idx, val in enumerate(index):
            if idx < 5:
                recent_ratio.append(ratio[val])

        return recent_ratio

    async def extract_debts(self, stock_code):
        browser = await launch({'headless': True})
        page = await browser.newPage()
        await page.goto(self.debt_url.format(stock_code), {'waitUntil': "networkidle2"})
        await page.waitForSelector('#cwzbTable')
        await page.click('#cwzbTable > div.scroll_container > ul > li:nth-child(2) > a')

        all_targets = await page.xpath('//*[@id="cwzbTable"]/div[1]/div[1]/div[4]/table[2]/tbody/tr[11]/td[position()<6]')
        for item in all_targets:
            self.debt_ratio.append(await (await item.getProperty('textContent')).jsonValue())

        await browser.close()

    def judgement(self):
        # 添加深证市盈率判定
        for (k,v) in self.stock_dict.items():
            v_list = eval(v)
            roe, cashflow_profit, gross_profit = \
                np.array(v_list[:5]).astype(np.float), \
                np.array(v_list[-5:]).astype(np.float), \
                np.array(v_list[5:10]).astype(np.float)
            if np.mean(roe) < 20 or roe[0] < 20 or np.mean(cashflow_profit) < 1 or np.mean(gross_profit) < 40 or gross_profit[0] < 40:
                continue
            bonus_list = [_.strip('%') for _ in self.extract_bonus(k.split()[1])]
            if '--' in bonus_list:
                continue
            print(k, '\n', 'ROE：', roe, '\n', 'cashflow_profit：', cashflow_profit, '\n', 'gross_profit：', gross_profit)
            bonus_data = np.array(bonus_list).astype(np.float)
            print('bonus_ratio：', bonus_data)
            if np.mean(bonus_data) < 25 and (bonus_data > 25).sum() != bonus_data.size:
                continue
            
            # TODO: 派息年数不足五年？

            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.extract_debts(k.split()[-1]))
            self.debt_ratio = [_.strip('%') for _ in self.debt_ratio]
            debt_data = np.array(self.debt_ratio).astype(np.float)
            if np.mean(debt_data) < 60 and debt_data[0] < 60:
                self.qualified_stocks.append(k)
            # TODO: 增加延时
            print('debt_ratio：', debt_data, '\n')
            self.debt_ratio.clear()


class StockAnalyzerHK(StockAnalyzer):
    def __init__(self, base_url, query, bonus_url, debt_url):
        super(__class__, self).__init__(base_url, query, bonus_url, debt_url)
        self.bonus_list = []
        self.qualified_stocks = []
    
    async def extract_bonus(self, stock_code):
        # exepath = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
        details = []
        # TODO: 派息比率过高的问题？
        # TODO: 只在开头打开一次browser 异步效果？
        # browser = await launch({'executablePath': exepath, 'headless': True})
        browser = await launch({'headless': True})
        page = await browser.newPage()
        try:
            await page.goto(self.bonus_url.format(stock_code), {'waitUntil': "networkidle2"}, timeout=10000)
            # await page.waitForSelector('#highcharts-0')
        # await page.waitFor(10000)
        except Exception as e:
            print('extract_bonus_HK error: ', e)
        finally:
            for i in range(6):
                await page.hover('#highcharts-0 > svg > g.highcharts-series-group > g:nth-child(3) > rect:nth-child({})'.format(i+1))
                # 显示框有3~4行，选取倒数第2行
                rows = await page.xpath('//*[@id="highcharts-0"]/div[1]/span/span[@*]')
                details.append(rows[-2])
            for detail in details:
                self.bonus_list.append((await (await detail.getProperty('textContent')).jsonValue()).split()[2])
            # 删除最后一列空白条形图中的数据
            self.bonus_list = list(filter(lambda x: '%' in x, self.bonus_list))
            self.bonus_list = [_.strip('%') for _ in self.bonus_list]
            self.bonus_list.reverse()
        
        await browser.close()

    def combination_filter(self):
        pass

    def judgement(self):
        # TODO: 派息比率低的好公司？ choice 派息比率超过100？
        for (k,v) in self.stock_dict.items():
            v_list = eval(v)
            roe, cashflow_profit, gross_profit, debt_ratio = \
                np.array(v_list[:5]).astype(np.float), \
                np.array(v_list[-6:-11:-1]).astype(np.float), \
                np.array(v_list[5:10]).astype(np.float), \
                np.array(v_list[-5:]).astype(np.float)
            if np.mean(roe) < 20 or roe[0] < 20 or np.mean(cashflow_profit) < 1 or np.mean(gross_profit) < 40 or \
                gross_profit[0] < 40 or np.mean(debt_ratio) >= 60 or debt_ratio[0] >= 60:
                continue
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.extract_bonus(k.split()[-1]))
            # TODO: 需要针对bonus_list个数大于或小于5做处理
            bonus_data = np.array(self.bonus_list[:5]).astype(np.float)
            if np.mean(bonus_data) >= 30 and (bonus_data >= 30).sum() == bonus_data.size:
                self.qualified_stocks.append(k)
            self.bonus_list.clear()
            print('{}\nROE: {}\ncashflow_profit：{}\ngross_profit：{}\ndebt_ratio：{}\nbonus_ratio：{}\n'.format(k, roe, cashflow_profit, gross_profit, debt_ratio, bonus_data))


class StockAnalyzerUS(StockAnalyzer):
    def __init__(self, base_url, query, bonus_url, debt_url):
        super(__class__, self).__init__(base_url, query, bonus_url, debt_url)
        self.bonus_info = {}
        self.bonus_list = []

    # 适用于所有market派息比率计算
    async def extract_bonus(self, stock_tag):
        browser = await launch({'headless': True})
        page = await browser.newPage()
        try:
            await page.goto(self.bonus_url.format(config.bonus_general_query.format(config.year-5, config.year-1, stock_tag)), timeout=60000)
            await page.waitForNavigation()
        except Exception as e:
            print('extract_bonus_US error: ', e)
        finally:
            all_elements = []
            get_profit = False
            profit = []
            all_targets = await page.xpath('//*[@id="tableWrap"]/div[2]/div/div[2]/div/table/tbody/tr[*]/td[4]/div/a')
            for i in range(len(all_targets)):
                # TODO: 判断股票与数据相对应 股票名与代码对应
                all_elements.append(await page.xpath('//*[@id="tableWrap"]/div[2]/div/div[1]/div/div/div[2]/table/tbody/tr[{}]/td[position()>2]'.format(i+1)))
                stock_code = await page.xpath('//*[@id="tableWrap"]/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[3]/div'.format(i+1))
                # print(await (await all_targets[i].getProperty('textContent')).jsonValue(), ":", end='')
                elements_list = [(await (await item.getProperty('textContent')).jsonValue()).strip() for item in all_elements[i]]
                if not get_profit:
                    profit = elements_list[1:6]
                    get_profit = True
                while '' in elements_list: elements_list.remove('')
                self.bonus_info[str(i) + stock_tag + ' ' + await (await stock_code[0].getProperty('textContent')).jsonValue()] = str(elements_list)
            idx = 0
            for value in self.bonus_info.values():
                dividend = float(eval(value)[0].strip('万亿').replace(',', '')) / 10000 if '万' in eval(value)[0] else float(eval(value)[0].strip('万亿').replace(',', ''))
                profit_val = float(profit[idx].strip('万亿').replace(',', '')) / 10000 if '万' in profit[idx] else float(profit[idx].strip('万亿').replace(',', ''))
                try:
                    self.bonus_list.append(dividend / profit_val)
                except Exception as e:
                    pass
                idx += 1
            self.bonus_info.clear()

        await browser.close()

    def judgement(self):
        # TODO: 派息比率低的好公司？ choice 派息比率超过100？
        for (k,v) in self.stock_dict.items():
            v_list = eval(v)
            # TODO: 最后一列有市值会影响结果
            roe, cashflow_profit, gross_profit, debt_ratio = \
                np.array(v_list[:5]).astype(np.float), \
                np.array(v_list[-7:-12:-1]).astype(np.float), \
                np.array(v_list[5:10]).astype(np.float), \
                np.array(v_list[-6:-1:1]).astype(np.float)
                # np.array(v_list[-5:]).astype(np.float) 
                # np.array(v_list[-6:-1:1]).astype(np.float)
            if np.mean(roe) < 20 or roe[0] < 20 or np.mean(cashflow_profit) < 1:
                continue
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.extract_bonus(k.split()[-1]))
            bonus_data = np.array(self.bonus_list).astype(np.float)
            if np.mean(bonus_data) >= 0.2 and (bonus_data >= 0.2).sum() == bonus_data.size:
                self.qualified_stocks.append(k)
            self.bonus_list.clear()
            print('{}\nROE: {}\ncashflow_profit：{}\ngross_profit：{}\ndebt_ratio：{}\nbonus_ratio：{}\n'.format(k, roe, cashflow_profit, gross_profit, debt_ratio, bonus_data))
