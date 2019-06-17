# -*- coding=utf-8 -*-
import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt
plt.style.use('seaborn')
from aqf.com.xiumei.utils import tushare_util


"""
动量策略
"""


def mumentum_strategy():
    """
    动量策略
    :return:
    """
    # 1- 数据准备与数据回测
    data = tushare_util.get_single_stock_data('hs300', start_date='2010-01-01', end_date='2017-06-30')

    # 2- 策略开发思路
    data['returns'] = np.log(data['close'] / data['close'].shift(1))
    # 持仓信号
    data['position'] = np.sign(data['returns'])
    # 避免未来函数，计算 mumentum 策略收益
    data['strategy'] = data['position'].shift(1) * data['returns']

    # 3- 策略可视化
    data[['returns', 'strategy']].cumsum().apply(np.exp).plot(figsize=(10, 6))
    # plt.show()

    # 4- 策略优化思路—参数优化和穷举
    # 上述策略存在的问题：过于频繁的买卖开仓
    data['position_5'] = np.sign(data['returns'].rolling(5).mean())
    data['strategy_5'] = data['position_5'].shift(1) * data['returns']
    data[['returns', 'strategy_5']].dropna().cumsum().apply(np.exp).plot(figsize=(10, 6))
    # plt.show()

    # 4.1- 参数寻优—使用离散 Return 计算方法
    data['returns_dis'] = data['close'] / data['close'].shift(1) - 1
    # data['returns_dis'] = data['close'].pct_change()
    data['returns_dis_cum'] = (data['returns_dis'] + 1).cumprod()
    price_plot = ['returns_dis_cum']
    for days in [10, 20, 30, 60]:
        #     data['position_%d' % days] = np.sign(data['returns'].rolling(days).mean())
        price_plot.append('sty_cumr_%dd' % days)
        data['position_%dd' % days] = np.where(data['returns'].rolling(days).mean() > 0, 1, -1)
        data['strategy_%dd' % days] = data['position_%dd' % days].shift(1) * data['returns']
        data['sty_cumr_%dd' % days] = (data['strategy_%dd' % days] + 1).cumprod()

    data[price_plot].dropna().plot(
        title='HS300 Multi Parameters Momuntum Strategy',
        figsize=(10, 6), style=['--', '--', '--', '--', '--'])
    # plt.show()

    # 4.2- 策略优化思路之一 High Frequency Data 用于 Momentum 策略
    hs300_5m = ts.get_k_data('hs300', ktype='5')
    print(hs300_5m.head())
    hs300_5m.set_index('date', inplace=True)
    hs300_5m.index = pd.to_datetime(hs300_5m.index)
    hs300_5m['returns'] = np.log(hs300_5m['close'] / hs300_5m['close'].shift(1))
    hs300_5m['position'] = np.sign(hs300_5m['returns'].rolling(10).mean())  # 10个5分钟平均；
    hs300_5m['strategy'] = hs300_5m['position'].shift(1) * hs300_5m['returns']
    hs300_5m[['returns', 'strategy']].dropna().cumsum().apply(np.exp).plot(figsize=(10, 6),
                                                                           style=['--', '--'])
    plt.show()


if __name__ == '__main__':
    mumentum_strategy()
