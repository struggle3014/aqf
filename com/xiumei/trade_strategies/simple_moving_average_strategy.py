# -*- coding=utf-8 -*-
import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt
from aqf.com.xiumei.utils import tushare_util

"""
移动平均与双均线模型
策略编写的一般步骤：
1）数据准备&数据回测
2）策略开发思路
3）计算策略年化收益率并可视化
4）策略风险评估
5）策略优化
"""


def simple_moving_average():
    """
    移动平均策略
    :return:
    """
    # 1- 数据准备与数据回测
    data = tushare_util.get_single_stock_data('hs300', start_date='2010-01-01', end_date='2017-06-30')
    # 列名重命名操作
    # data.rename(columns={'close': 'price'}, inplace=True)
    data['SMA_10'] = data['close'].rolling(10).mean()
    data['SMA_60'] = data['close'].rolling(60).mean()
    print(data.tail())
    data[['close', 'SMA_10', 'SMA_60']].plot(title='HS300 stock price', figsize=(10, 6))
    # plt.show()

    # 2- 策略开发思路
    data['position'] = np.where(data['SMA_10'] > data['SMA_60'], 1, -1)
    # 去掉空值，NaN
    data.dropna(inplace=True)
    # 生成交易信号
    data['position'].plot(ylim=[-1.1, 1.1], title='Market Positioning')
    # plt.show()

    # 3- 计算策略年化收益率并可视化
    # 将交易信号转化为持仓信号有两种方式：Numpy 向量化；循环法
    data['returns'] = np.log(data['close'] / data['close'].shift(1))
    data['returns'].hist(bins=35)
    # plt.show()

    # 注意此处的未来函数，前一天产生的交易信号在下一个交易日才能使用。
    data['strategy'] = data['position'].shift(1) * data['returns']
    # 可视化，连续计算方法
    data[['returns', 'strategy']].cumsum().apply(np.exp).plot(figsize=(10, 6))
    # plt.show()

    # 4- 策略风险评估
    # 年化收益率
    data[['returns', 'strategy']].mean() * 252
    # 年化风险;方差：pandas.series.std()
    data[['returns', 'strategy']].std() * 252 ** 0.5
    # 累计回报
    data['cumret'] = data['strategy'].cumsum().apply(np.exp)
    # 累计回报最大值，依次给出前 1、2、3、...、n 个数的最大值
    data['cummax'] = data['cumret'].cummax()
    data[['cumret', 'cummax']].plot(figsize=(10, 6))
    # plt.show()
    # 计算最大回撤
    drawdown = (data['cummax'] - data['cumret']).max()
    print(drawdown)

    # 5- 策略优化的思路
    data['10-60'] = data['SMA_10'] - data['SMA_60']
    # 阈值
    sd = 20
    data['regime'] = np.where(data['10-60'] > sd, 1, 0)
    data['regime'] = np.where(data['10-60'] < -sd, -1, data['regime'])
    # 统计各值的数量
    # data['regime'].value_counts()
    data['market'] = np.log(data['close'] / data['close'].shift(1))
    data['strategy2'] = data['regime'].shift(1) * data['market']
    data[['market', 'strategy', 'strategy2']].cumsum().apply(np.exp).plot(grid=True, figsize=(10, 8))
    plt.show()


if __name__ == '__main__':
    simple_moving_average()
