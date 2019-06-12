# -*- coding=utf-8 -*-
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import seaborn
import tushare as ts
import scipy.stats as stats


# 1.1- 获取单个证券的股价数据
def get_single_stock_data(stock, start_date, end_date):
    # 获取证券的股价。数据类型为 pandas.core.frame.DataFrame
    data = ts.get_k_data(stock, start=start_date, end=end_date)
    # 1- 将数据 date 列指定为索引
    data.set_index('date', inplace=True)
    # 将字符串格式的 date 转换为日期格式
    data.index = pd.to_datetime(data.index)
    return data


# 1.2- 获取多只证券的股价信息
def get_multi_stock_data(stocks, start_date, end_date):
    datas = map(get_single_stock_data, stocks, fill_list(start_date, len(stocks)), fill_list(end_date, len(stocks)))
    return pd.concat(datas, keys=stocks, names=['Ticker', 'Date'])


# 填充指定长度的 list
def fill_list(thing, length):
    result = []
    for i in range(length):
        result.append(thing)
    return result


# 2.1- 金融数据可视化
def finance_data_visual():
    stocks = get_multi_stock_data(['600030', '000001', '600426'], '2019-05-05', '2019-06-06')
    # 1- 重置索引
    close_price = stocks[['close']].reset_index()
    print(close_price.head())
    # 2- 数据透视表，将所有股价信息显示在一张表中
    daily_close = close_price.pivot(index='Date', columns='Ticker', values='close')
    print(daily_close.head())
    # 3- 画图
    daily_close.plot(subplots=True, figsize=(10, 8))
    plt.show()


# 3.1- 金融数据计算，每日收益
def calculate_daily_profit():
    stocks = get_multi_stock_data(['600030', '000001', '600426'], '2019-05-05', '2019-06-06')
    # 1- 重置索引
    close_price = stocks[['close']].reset_index()
    # 2- 数据透视表，将所有股价信息显示在一张表中
    daily_close = close_price.pivot(index='Date', columns='Ticker', values='close')
    # 3- 使用 shift 方法，计算收益。shift 将每列下移 n 格。
    price_change = daily_close / daily_close.shift(1) - 1
    # print(price_change.ix[:, 0:4].head())
    print(price_change.head())
    # 4- 将 NaN 替换为 0
    price_change.fillna(0, inplace=True)
    print(price_change.head())


# 3.2- 金融数据计算，累计收益
def calculate_accu_profit():
    stocks = get_multi_stock_data(['600030', '000001', '600426'], '2019-05-05', '2019-06-06')
    # 1- 重置索引
    close_price = stocks[['close']].reset_index()
    # 2- 数据透视表，将所有股价信息显示在一张表中
    daily_close = close_price.pivot(index='Date', columns='Ticker', values='close')
    # 3- 使用 shift 方法，计算收益。shift 将每列下移 n 格。
    price_change = daily_close / daily_close.shift(1) - 1
    # print(price_change.ix[:, 0:4].head())
    # 4- 将 NaN 替换为 0
    price_change.fillna(0, inplace=True)
    cum_daily_return = (1 + price_change).cumprod()
    print(cum_daily_return.head())
    cum_daily_return.plot(figsize=(8, 6))
    plt.show()


# 4- 分析 return 分布
# 4.1- 直方图
def plot_hist():
    # stocks = get_multi_stock_data(['600030', '000001', '600426'], '2019-05-05', '2019-06-06')
    stocks = get_multi_stock_data(['600030', '600426'], '2019-05-05', '2019-06-06')
    # 1- 重置索引
    close_price = stocks[['close']].reset_index()
    # 2- 数据透视表，将所有股价信息显示在一张表中
    daily_close = close_price.pivot(index='Date', columns='Ticker', values='close')
    # 3- 使用 shift 方法，计算收益。shift 将每列下移 n 格。
    price_change = daily_close / daily_close.shift(1) - 1
    # print(price_change.ix[:, 0:4].head())
    # 4- 将 NaN 替换为 0
    price_change.fillna(0, inplace=True)
    # 5- 画出 600030 股价直方图
    price_change['600030'].hist(bins=30, figsize=(4, 3))
    plt.show()
    # 6- 画出所有股票的股价分布图
    price_change.hist(bins=20, sharex=True, figsize=(12, 8))
    plt.show()


# 4.2- QQ-Plots
# 使用 QQ 图验证股价 return 分布
def plot_qq():
    # stocks = get_multi_stock_data(['600030', '000001', '600426'], '2019-05-05', '2019-06-06')
    stocks = get_multi_stock_data(['600030', '600426'], '2019-05-05', '2019-06-06')
    # 1- 重置索引
    close_price = stocks[['close']].reset_index()
    # 2- 数据透视表，将所有股价信息显示在一张表中
    daily_close = close_price.pivot(index='Date', columns='Ticker', values='close')
    # 3- 使用 shift 方法，计算收益。shift 将每列下移 n 格。
    price_change = daily_close / daily_close.shift(1) - 1
    # print(price_change.ix[:, 0:4].head())
    # 4- 将 NaN 替换为 0
    price_change.fillna(0, inplace=True)
    # 5- 绘制 QQ 图
    fig = plt.figure(figsize=(7, 5))
    stats.probplot(price_change['600030'], dist='norm', plot=fig.add_subplot(111))
    plt.show()


# 5- 股价相关性
def plot_stocks_coors():
    # 1- 获取 hs300 股价信息
    hs300_data = get_single_stock_data('hs300', '2016-01-01', '2017-07-01')
    hs300_return = hs300_data.close.pct_change().fillna(0)
    # 2- 获取其他股票股价信息
    stocks = get_multi_stock_data(['600030', '000001', '600426'], '2016-01-01', '2017-07-01')
    close_price = stocks[['close']].reset_index()
    # 数据透视表，将所有股价信息显示在一张表中
    daily_close = close_price.pivot(index='Date', columns='Ticker', values='close')
    # 3- 数据合并
    return_all = pd.concat([hs300_return, daily_close.pct_change().fillna(0)], axis=1)
    return_all.rename(columns={'close': 'hs300'}, inplace=True)
    print(return_all.head())
    # 4- 计算累计收益
    cum_return_all = (1 + return_all).cumprod()
    print(cum_return_all.head())
    # 5- 累计收益作图
    cum_return_all[['hs300', '600030', '600426']].plot(figsize=(8, 6))
    # plt.show()
    # 6- 计算相关性，corr 协方差计算
    corrs = return_all.corr()
    seaborn.heatmap(corrs)
    plt.show()


if __name__ == '__main__':
    # get_single_stock_data()
    # result = get_multi_stock_data(['600030', '000001'], '2019-06-05', '2019-06-06')
    # finance_data_visual()
    # calculate_daily_profit()
    # calculate_accu_profit()
    # plot_hist()
    # plot_qq()
    plot_stocks_coors()
