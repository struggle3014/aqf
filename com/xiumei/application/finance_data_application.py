# -*- coding=utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime
import tushare as ts
import matplotlib.pyplot as plt
import talib as ta
import math
from functools import reduce
from aqf.com.xiumei.utils import tushare_util

"""
金融数据处理分析实战案例
"""


def simple_finance_apply():
    """
    简单的金融应用和分析
    :return:
    """
    # 1- 获取股票数据
    hs300 = tushare_util.get_single_stock_data('hs300', '2015-01-01', '2017-06-30')
    # print(hs300.head())
    # 2- 画出股价走势图
    # hs300['close'].plot(figsize=(8, 5), grid=True, title='HS300 Close Price')
    # plt.show()
    # 3- 计算收益（连续收益/离散收益）
    # 3.1- 连续收益
    hs300['return_continue'] = np.log(hs300['close'] / hs300['close'].shift(1))
    # 3.2- 离散收益计算公式：当日收盘价Series / 前一日收盘价Series -1 或者 当日收盘价Series.cumprod()。
    hs300['return_spread'] = (hs300['close'] / hs300['close'].shift(1) - 1)
    hs300['return_spread_2'] = hs300['close'].pct_change()
    print(hs300['close'].pct_change())
    # 4- 计算股价的平均移动 SMA
    # 4.1- 使用 rolling(window=) 计算移动平均
    hs300['SMA20'] = hs300['close'].rolling(window=20).mean()
    hs300[['close', 'SMA20']].plot(figsize=(8, 6))
    # plt.show()
    # 4.2- 使用 talib 计算移动平均；talib 技术分析包
    hs300['SMA20_ta'] = ta.SMA(np.asarray(hs300['close']), 20)  # talib 的数据结构有些指标只支持 Ndarray 格式；
    hs300[['close', 'SMA20_ta']].plot(figsize=(8, 6))
    # plt.show()
    hs300['SMA60_ta'] = ta.SMA(np.asarray(hs300['close']), 60)
    hs300[['close', 'SMA20_ta', 'SMA60_ta']].plot(figsize=(8, 6))
    # plt.show()
    hs300['Upper'], hs300['middle'], hs300['Lower'] = ta.BBANDS(np.asarray(hs300['close']),
                                                                timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    hs300[['close', 'Upper', 'middle', 'Lower']].plot(figsize=(10, 6))
    hs300['Mov_Vol'] = hs300['return_continue'].rolling(window=252, min_periods=60).std() * math.sqrt(252)
    hs300[['close', 'Mov_Vol', 'return_continue']].plot(subplots=True, figsize=(10, 8), grid=True)
    plt.show()


def analysis_stock_select():
    """
    爬取 tushare 数据进行选股条件分析
    :return:
    """
    # 1- 获取沪深 300 股票代码列表
    data = ts.get_hs300s()
    # print(data.head())
    hs300 = ts.get_hs300s()['code'].tolist()

    # 2- 获取基本面数据
    # rev: 收入同比（%）  profit：利润同比（%）  npr: 净利润率（%）详细解释参见源码
    # print(ts.get_stock_basics().reset_index(inplace=True).head())
    stock_basics = ts.get_stock_basics()
    stock_basics.reset_index(inplace=True)
    print(stock_basics.head())
    # isin():数据过滤的方法；从 stcok_basics 这张大表格里面把 hs300 的这 300 只股票代码给挑选出来；
    data1 = stock_basics.loc[stock_basics['code'].isin(hs300),
                            ['code', 'name', 'industry', 'pe', 'pb', 'esp','rev', 'profit']]
    # print(data1.head())

    # 3- 获取盈利能力数据
    stock_profit = ts.get_profit_data(2018, 3)
    # print(stock_profit.head())
    data2 = stock_profit.loc[stock_profit['code'].isin(hs300), ['code', 'roe', 'gross_profit_rate', 'net_profit_ratio']]
    # print(data2.head())

    # 4- 获取成长能力数据
    # nprg:净利润增长率（%）  nav:净资产增长率
    stock_growth = ts.get_growth_data(2017, 1)
    data3 = stock_growth.loc[stock_growth['code'].isin(hs300), ['code', 'nprg']]
    # print(data3.head())

    # 5- 将基本面数据、盈利能力数据、成长能力数据合并
    # merge 方法，使用指定列合并 DataFrame
    merge = lambda x, y: pd.merge(x, y, how='left', on='code')
    data = reduce(merge, [data1, data2, data3])
    # 去除重复数据
    data.drop_duplicates(inplace=True)
    # print(data.head())

    # 6- 根据已有列，计算数据
    # 估值系数，烟蒂值 = pe * pb
    data['voluation_coefficient'] = data['pe'] * data['pb']

    # 7- 条件选股
    data_filter = data.loc[(data['voluation_coefficient'] < 60) & (data['roe'] > 5),
        ['code', 'name', 'pe', 'pb', 'voluation_coefficient', 'roe', 'rev']]
    print(data_filter.head())
    print("筛选出共 %d 只个股" % len(data_filter))

    # 8- 按照特定字段对数据进行排序
    # 8.1- 按成长性（烟蒂值）排序
    data_filter.sort_values(['voluation_coefficient'], ascending=True, inplace=True)
    print(data_filter.head())
    # 8.2- 计算成长性
    data['growth'] = data.apply(map_func, axis=1)
    print(data.head())
    # 8.3- 对高成长分类按“烟蒂系数”做升序排序
    data_growth = data[data['growth'] == '高成长'].sort_values(['voluation_coefficient'], ascending=True)
    print(data_growth.head())
    # 8.4- 按成长性分组并排序
    data_group = data.groupby('growth')
    print(data_group.size())
    # DataFrameGroupBy 参考有道云笔记
    data_group = data.groupby('growth').apply(sort_dataframe, sort_values=['voluation_coefficient'])
    print(data_group)


def map_func(x):
    """
    根据 roe 值计算成长性。作为 apply 函数的参数传入
    :param x: DataFrame 中一行或一列数据，取决于 apply 函数参数的 axis
    :return: 将每个计算结果组合，返回一个 Series
    """
    if x['roe'] > 5:
        return '高成长'
    elif x['roe'] >= 0:
        return '低成长'
    elif x['roe'] < 0:
        return '亏损'


def sort_dataframe(dataframe, sort_values, is_asceding=True):
    """
    将 DataFrame 按照指定值排序。
    :param dataframe: DataFrame
    :param sort_values: 排序字段
    :param is_asceding: 是否是升序
    :return: 返回按指定排序字段排序后的数据
    """
    # 按‘成长性’分组，筛选每个分组中‘烟蒂系数’最低的两个个股
    return dataframe.sort_values(sort_values, ascending=is_asceding)[:2]


if __name__ == '__main__':
    # simple_finance_apply()
    analysis_stock_select()
