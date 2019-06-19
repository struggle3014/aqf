# -*- coding=utf-8 -*-
import pandas as pd
import numpy as np
import tushare as ts
import talib as ta
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.style.use('seaborn')
from aqf.com.xiumei.utils import tushare_util
# 确保可以显示‘-’号
mpl.rcParams['axes.unicode_minus']=False
# 确保中文显示正常
mpl.rcParams['font.sans-serif'] = ['SimHei']


"""
cci 策略
"""


def cci_combine_istrade_isposition():
    """
    CCI 交易信号和持仓信号合并
    :return:
    """
    # 1- 获取数据
    data = tushare_util.get_single_stock_data('600030', start_date='2016-06-01', end_date='2017-06-30')
    data['cci'] = ta.CCI(np.asarray(data['high']), np.asarray(data['low']), np.asarray(data['close']), timeperiod=20)

    # 2- 绘制 CCI 指标图
    # plt.subplot(2, 1, 1)
    # plt.title('600030 CCI 指标图')
    # 不显示横坐标
    # plt.gca().axes.get_xaxis().set_visible(False)
    # data['close'].plot(figsize=(10, 8))
    # plt.legend()
    # plt.subplot(2, 1, 2)
    # data['cci'].plot(figsize=(10, 8))
    # plt.legend()
    # plt.show()

    # 2- 交易信号、持仓信号和策略逻辑
    data['yes_cci'] = data['cci'].shift(1)
    data['daybeforeyes_cci'] = data['cci'].shift(2)

    # 2.1- 交易和持仓信号合并；产生开平仓信号
    # 开多信号：当前天 cci 小于 -100，昨日 cci 大于 -100，则记开多信号
    data['signal'] = np.where(np.logical_and(data['daybeforeyes_cci'] < -100, data['yes_cci'] > -100),  1, np.nan)
    # 开空信号：当前天 cci 大于 100，昨日 cci 小于 100，则记为开空信号
    data['signal'] = np.where(np.logical_and(data['daybeforeyes_cci'] > 100, data['yes_cci'] < 100), -1, data['signal'])

    data['signal'] = data['signal'].fillna(method='ffill') # 在下一个信号产生之前，都是沿用上一个信号。
    data['signal'] = data['signal'].fillna(0)
    print(data.tail())

    # 2.2- 交易和持仓信号分开
    # 开多信号：当前天 cci 小于 -100，昨日 cci 大于 -100，则记开多信号
    data['signal'] = np.where(np.logical_and(data['daybeforeyes_cci'] < -100, data['yes_cci'] > -100), 1, 0)
    # 开空信号：当前天 cci 大于 100，昨日 cci 小于 100，则记为开空信号
    data['signal'] = np.where(np.logical_and(data['daybeforeyes_cci'] > 100, data['yes_cci'] < 100), -1, data['signal'])
    # 如果当天没有交易信号，设置为nan，如果有，取原来信号
    data['signal'] = np.where(data['signal'] == 0, np.nan, data['signal'])
    # 通过前向填充生成持仓记录
    data['position'] = data['signal'].fillna(method='ffill')
    data['position'] = data['signal'].fillna(0)

    # plt.subplot(3, 1, 1)
    # plt.title('600030 CCI 开仓图')
    # # 不显示横坐标
    # plt.gca().axes.get_xaxis().set_visible(False)
    # data['close'].plot(figsize=(10, 8))
    # plt.legend(loc='upper left')
    #
    # plt.subplot(3, 1, 2)
    # data['cci'].plot(figsize=(10, 8))
    # plt.legend(loc='upper left')
    # plt.gca().axes.get_xaxis().set_visible(False)
    #
    # plt.subplot(3, 1, 3)
    # data['signal'].plot(figsize=(10, 8), marker='o', linestyle='')
    # plt.legend(loc='upper left')
    # plt.show()

    # 3- 收益计算和净值绘制
    # 计算股票每日收益率
    data['pct_change'] = data['close'].pct_change()
    # 计算股票累计收益率
    data['return'] = (data['pct_change'] + 1).cumprod()
    # 计算策略每日收益率
    data['strategy_return'] = data['pct_change'] * data['signal']
    # 计算策略累计收益率
    data['strategy_cum_return'] = (data['strategy_return'] + 1).cumprod()

    # 绘制股票和策略累计收益
    data[['return', 'strategy_cum_return']].plot(figsize=(10, 6))
    plt.title('600030 CCI 收益图')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    cci_combine_istrade_isposition()
