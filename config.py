# -*- coding: utf-8 -*-
import datetime


headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
           'Upgrade-Insecure-Requests':'1',
           'Proxy-Connection':'keep-alive',
           'Cache-Control':'max-age=0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate',
           'Content-Type':'application/x-www-form-urlencoded',
           'cookie':'ASPSESSIONIDSSSDDTTA=KABHCBMAFGPOGLLDJAJFOHIL',
           'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6'}

query_list = []

query_list.append(r'%E8%BF%9E%E7%BB%AD5%E5%B9%B4ROE%E5%A4%A7%E4%BA%8E15%25')

query_list.append(r'%E6%AF%9B%E5%88%A9%E7%8E%87%E5%A4%A7%E4%BA%8E30%25')

query_list.append(r'%E8%B5%84%E4%BA%A7%E8%B4%9F%E5%80%BA%E7%8E%87%E5%B0%8F%E4%BA%8E60%25')

query_list.append(r'%E8%BF%9E%E7%BB%AD5%E5%B9%B4%E7%BB%8F%E8%90%A5%E6%B4%BB%E5%8A%A8%E7%8E%B0%E9%87%91%E6%B5%81%E9%87%8F%E5%87%80%E9%A2%9D%E9%99%A4%E4%BB%A5%E5%87%80%E5%88%A9%E6%B6%A6%E7%9A%84%E6%AF%94%E7%8E%87%E5%A4%A7%E4%BA%8E80%25')

query_A = r'%EF%BC%8C'.join(query_list)

query_list.clear()

query_list.append(r'%E8%BF%9E%E7%BB%AD5%E5%B9%B4ROE%E5%A4%A7%E4%BA%8E15%25')

query_list.append(r'%E8%BF%9E%E7%BB%AD5%E5%B9%B4%E6%AF%9B%E5%88%A9%E7%8E%87%E5%A4%A7%E4%BA%8E30%25')

query_list.append(r'%E8%BF%9E%E7%BB%AD5%E5%B9%B4%E7%BB%8F%E8%90%A5%E6%B4%BB%E5%8A%A8%E5%87%80%E7%8E%B0%E9%87%91%E6%B5%81%E9%87%8F%E9%99%A4%E4%BB%A5%E5%87%80%E5%88%A9%E6%B6%A6%E5%A4%A7%E4%BA%8E80%25')

query_list.append(r'%E8%BF%9E%E7%BB%AD5%E5%B9%B4%E8%B5%84%E4%BA%A7%E8%B4%9F%E5%80%BA%E7%8E%87%E5%B0%8F%E4%BA%8E65%25')

query_HK = r'%EF%BC%8C'.join(query_list)

query_list.append(r'%E8%BF%9E%E7%BB%AD5%E5%B9%B4ROE%E5%A4%A7%E4%BA%8E15%25')

query_list.append(r'%E8%BF%9E%E7%BB%AD5%E5%B9%B4%E6%AF%9B%E5%88%A9%E7%8E%87%E5%A4%A7%E4%BA%8E40%25')

query_list.append(r'%E8%BF%9E%E7%BB%AD5%E5%B9%B4%E7%BB%8F%E8%90%A5%E6%B4%BB%E5%8A%A8%E5%87%80%E7%8E%B0%E9%87%91%E6%B5%81%E9%87%8F%E9%99%A4%E4%BB%A5%E5%87%80%E5%88%A9%E6%B6%A6%E5%A4%A7%E4%BA%8E80%25')

query_list.append(r'%E8%B5%84%E4%BA%A7%E8%B4%9F%E5%80%BA%E7%8E%87%E5%B0%8F%E4%BA%8E60%25')

query_list.append(r'%E5%B8%82%E5%80%BC%E5%A4%A7%E4%BA%8E50%E4%BA%BF')

query_US = r'%EF%BC%8C'.join(query_list)

base_url_A = 'http://www.iwencai.com/stockpick/search?typed=1&preParams=&ts=1&f=1&qs=index_rewrite&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w={}'

bonus_url_A = 'http://basic.10jqka.com.cn/{}/bonus.html'

debt_url_A = 'http://basic.10jqka.com.cn/{}/finance.html'

base_url_HK = 'http://www.iwencai.com/stockpick/search?typed=1&preParams=&ts=1&f=1&qs=result_channel&selfsectsn=&querytype=hkstock&searchfilter=&tid=stockpick&w={}'

bonus_url_HK = 'http://www.aastocks.com/sc/stocks/analysis/dividend.aspx?symbol={}'

cn_treasury = 'https://cn.investing.com/rates-bonds/china-10-year-bond-yield'

treasury_path = '//*[@id="last_last"]/text()'

us_treasury = 'https://cn.investing.com/rates-bonds/u.s.-10-year-bond-yield'

base_url_US = 'http://www.iwencai.com/stockpick/search?typed=1&preParams=&ts=1&f=1&qs=result_rewrite&selfsectsn=&querytype=usstock&searchfilter=&tid=stockpick&w={}'

year = datetime.datetime.now().year

bonus_general_query = '{}年到{}年{}年度分红，净利润'
