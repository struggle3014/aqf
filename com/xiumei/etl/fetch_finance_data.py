# -*- coding=utf-8 -*-
import warnings
import quandl
import tushare as ts
import pandas as pd
import numpy as np
import yfinance as yf
from pandas_datareader import data as web
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
warnings.simplefilter('ignore')  # 忽略可能会出现的警告信息，警告并不是错误，可以忽略；
yf.pdr_override()


# 从雅虎接口获取股票数据（行情数据和基本面数据）
def get_data_from_yahoo():
    data = web.get_data_yahoo('GS', start='2010-01-01', end='2012-01-01')
    print(data.head())


# 从 Quandl 接口获取数据，详情见 Quandl 官网
def get_data_from_quandl():
    data = quandl.get('EOD/KO', start_date='2019-05-05', end_date='2019-06-05')
    print(data.head())


# 从 Tushare 接口获取股票数据，详情见 Tushare 官网。
def get_data_from_tushare():
    # 1- 通过接口获取股票数据，pandas.core.frame.DataFrame
    # data = ts.get_k_data('hs300', start='2019-01-01', end='2019-06-05')
    # 2- 设置 DataFrame 索引
    # data.set_index('date', inplace=True)
    # 3- 画出股价走势图。下面的写法等价于 data.close.plot(figsize=(10, 6))
    # data['close'].plot(figsize=(10, 6))
    # print(data.head())
    # plt.show()

    # 4- 获取数据，tushare 不支持多股票查询。
    # data1 = ts.get_k_data('600030')  # 默认前复权价格
    # data2 = ts.get_k_data('600030', autype='hfq')  # 不复权
    # data3 = ts.get_k_data('600030', ktype='5')  # 两个日期之间的前复权价格

    # 4.1- 获取历史逐笔交易数据
    # df = ts.get_tick_data('601166', date='2019-06-06')
    # print(type(df))
    # df.sort_index(inplace=True, ascending=False)
    # print(df.head())

    # 4.2- 获取当前主流指数列表
    # df = ts.get_index()
    # print(df.head())

    # 4.3- 获取股票基本面数据
    # df = ts.get_stock_basics()
    # print(df.head)
    # df.set_index('code', inplace=True)
    # data = ts.get_profit_data(2019, 1)
    # print(data.head)
    # date = df.ix['600848']['timeToMarket']
    # print(date)

    # 4.4- 获取非结构化新闻、舆情数据。接口获取不了数据
    data = ts.get_latest_news(top=5, show_content=True)  # 显示最多5条新闻，并打印新闻内容
    print(type(data))
    # print(data)

    # 4.5- 获取龙虎榜信息
    # top_list = ts.top_list('2019-06-06')
    # print(top_list.head())


if __name__ == '__main__':
    # get_data_from_yahoo()
    # get_data_from_quandl()
    get_data_from_tushare()


