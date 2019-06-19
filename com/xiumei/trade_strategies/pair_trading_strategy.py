# -*- coding=utf-8 -*-
import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt
plt.style.use('seaborn')
from aqf.com.xiumei.utils import tushare_util


"""
配对交易策略

"""


def pair_trading_strategy():
    """
    配对交易策略
    :return:
    """
    # 1- 数据准备 & 数据回测
    stock_pair = ['600199', '600702']
    data1 = ts.get_k_data('600199', '2013-06-01', '2014-12-31')[['date', 'close']]
    data2 = ts.get_k_data('600702', '2013-06-01', '2014-12-31')['close']
    data = pd.concat([data1, data2], axis=1)
    data.set_index('date', inplace=True)
    data.columns = stock_pair

    # data.plot(figsize=(8, 6))
    # plt.show()
    # 2- 策略开发思路
    data['price_detla'] = data['600199'] - data['600702']
    # data['price_detla'].plot(figsize=(8, 6))
    # plt.ylabel('Spread')
    # plt.axhline(data['price_detla'].mean())
    # plt.show()
    # 价差的标准化
    data['zscore'] = (data['price_detla'] - np.mean(data['price_detla'])) / np.std(data['price_detla'])

    # 产生持仓信号
    data['position_1'] = np.where(data['zscore'] > 1.5, -1, np.nan)
    data['position_1'] = np.where(data['zscore'] < -1.5, 1, data['position_1'])
    data['position_1'] = np.where(abs(data['zscore']) < 0.5, 0, data['position_1'])
    # 产生交易信号
    data['position_1'] = data['position_1'].fillna(method='ffill')
    # data['position_1'].plot(ylim=[-1.1, 1.1], figsize=(10, 6))
    # plt.show()
    data['position_2'] = -np.sign(data['position_1'])
    print(data.head(20))
    # data['position_2'].plot(ylim=[-1.1, 1.1], figsize=(10, 6))
    # plt.show()

    # 3- 计算年化收益率并可视化
    # 做多和做空的权重分别是 50%， 50%
    data['returns_1'] = np.log(data['600199'] / data['600199'].shift(1))
    data['returns_2'] = np.log(data['600702'] / data['600702'].shift(1))
    data['strategy'] = 0.5 * (data['position_1'].shift(1) * data['returns_1']) + 0.5 * (
                data['position_2'].shift(1) * data['returns_2'])
    data[['returns_1', 'returns_2', 'strategy']].dropna().cumsum().apply(np.exp).plot(figsize=(10, 6))
    plt.show()


def pair_trading_enhanced_strategy():
    """
    增强的配对交易-考虑时间序列平稳性
    :return:
    """
    


if __name__ == '__main__':
    pair_trading_strategy()
