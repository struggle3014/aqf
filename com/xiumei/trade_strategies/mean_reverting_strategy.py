# -*- coding=utf-8 -*-
import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt
plt.style.use('seaborn')
from aqf.com.xiumei.utils import tushare_util


"""
均值回归策略
策略思想：
均值回归策略应用了股市投资中经典的高抛低吸思想，该类型策略一般在震荡市中表现优异；但是在单边趋势行情中一般表现糟糕，往往会会大幅
跑输市场；
"""


def mean_reverting_strategy():
    """
    均值回归策略
    :return:
    """
    # 1- 数据准备&回测准备
    data = tushare_util.get_single_stock_data('hs300', start_date='2010-01-01', end_date='2016-06-30')

    # 2- 策略开发思路
    data['returns'] = np.log(data['close'] / data['close'].shift(1))
    SMA_50 = 50
    data['SMA_50'] = data['close'].rolling(SMA_50).mean()
    threshold = 250  # 阈值；
    data['distance'] = data['close'] - data['SMA_50']
    data['distance'].dropna().plot(figsize=(10, 6), legend=True)
    # 画横线
    plt.axhline(threshold, color='r')
    plt.axhline(-threshold, color='r')
    plt.axhline(0, color='r')
    plt.show()
    # 核心精髓；不满足条件的使用 NaN 填充，方便后续使用向量化产生持仓信号
    data['position'] = np.where(data['distance'] > threshold, -1, np.nan)
    data['position'] = np.where(data['distance'] < -threshold, 1, data['position'])
    # 避免未来函数
    data['position'] = np.where(data['distance'] *
                                data['distance'].shift(1) < 0, 0, data['position'])
    data['position'] = data['position'].ffill().fillna(0)
    data['position'].iloc[SMA_50:].plot(ylim=[-1.1, 1.1], figsize=(10, 6))
    # plt.show()

    # 3- 计算策略年化收益率并可视化
    data['strategy'] = data['position'].shift(1) * data['returns']
    data[['returns', 'strategy']].dropna().cumsum().apply(np.exp).plot(figsize=(10, 6))
    plt.show()

if __name__ == '__main__':
    mean_reverting_strategy()
